#!/usr/bin/env node
/** Install the bundled writing skill and, optionally, explicitly pinned companions. */
import { spawn } from 'node:child_process';
import { existsSync, realpathSync } from 'node:fs';
import { lstat, readFile, stat } from 'node:fs/promises';
import { homedir } from 'node:os';
import path from 'node:path';
import { createInterface } from 'node:readline/promises';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const AGENTS = ['codex', 'claude-code'];
const ENHANCEMENTS = ['humanize-korean', 'stack-diagram'];
const CLI = 'skills@1.7.5';
const SHA = /^[a-f0-9]{40}$/i;
const HELP = `Usage: korean-dev-writing-install [options]

Install korean-dev-writing from this package. Project scope is the default.

  --with-enhancements           Also install humanize-korean and stack-diagram
  -a, --agent <agent>           codex or claude-code; repeat to select both
  -g, --global                  Install for the current user
  --project-dir <directory>     Project directory (default: current directory)
  --copy                       Copy instead of linking to canonical skill files
  --yes                        Accept the displayed plan without prompting
  --replace-existing           Explicitly allow replacement of same-name skills
  --dry-run                    Display the plan without commands or writes
  --humanize-source <source>    GitHub owner/repo or HTTPS repository URL
  --humanize-ref <commit>       Full 40-character Git commit SHA
  --stack-source <source>       GitHub owner/repo or HTTPS repository URL
  --stack-ref <commit>          Full 40-character Git commit SHA
  -h, --help                    Show this help

Sources can include #<full-commit-SHA>. A source override clears its default pin.
The default humanize-korean is bundled; use --humanize-source for another origin.
Enhancement overrides require --with-enhancements. --yes never permits replacement.
Node.js >=22.20.0, npm, and Git are required. No Python tools run during installation.
`;

export function parseArgs(argv) {
  const options = { agents: [], withEnhancements: false, global: false, copy: false,
    yes: false, replaceExisting: false, dryRun: false, help: false };
  const bools = { '--with-enhancements': 'withEnhancements', '-g': 'global', '--global': 'global',
    '--copy': 'copy', '--yes': 'yes', '--replace-existing': 'replaceExisting',
    '--dry-run': 'dryRun', '-h': 'help', '--help': 'help' };
  const values = { '-a': 'agents', '--agent': 'agents', '--project-dir': 'projectDir',
    '--humanize-source': 'humanizeSource', '--humanize-ref': 'humanizeRef',
    '--stack-source': 'stackSource', '--stack-ref': 'stackRef' };
  const seen = new Set();
  for (let i = 0; i < argv.length; i++) {
    const token = argv[i];
    const equal = token.indexOf('=');
    const flag = equal < 0 ? token : token.slice(0, equal);
    if (Object.hasOwn(bools, flag)) {
      if (equal >= 0) throw new Error(`${flag} does not accept a value.`);
      options[bools[flag]] = true;
      continue;
    }
    if (!Object.hasOwn(values, flag)) throw new Error(`Unknown argument: ${token}. Use --help.`);
    const value = equal < 0 ? argv[++i] : token.slice(equal + 1);
    if (!value || value.startsWith('-') || /[\x00-\x1f\x7f]/.test(value)) {
      throw new Error(`${flag} requires a non-empty value.`);
    }
    const key = values[flag];
    if (key === 'agents') {
      if (!AGENTS.includes(value)) throw new Error(`Unsupported agent: ${value}. Choose ${AGENTS.join(' or ')}.`);
      if (!options.agents.includes(value)) options.agents.push(value);
    } else {
      if (seen.has(key)) throw new Error(`${flag} may only be supplied once.`);
      seen.add(key);
      options[key] = value;
    }
  }
  if (!options.help && !options.withEnhancements &&
      ['humanizeSource', 'humanizeRef', 'stackSource', 'stackRef'].some(key => options[key] !== undefined)) {
    throw new Error('Enhancement source/ref options require --with-enhancements.');
  }
  return options;
}

/** Accept GitHub repositories only; refs are immutable commits, never shell fragments. */
export function normalizeSource(source, explicitRef) {
  if (typeof source !== 'string' || /[\s\x00-\x1f\x7f]/.test(source)) throw new Error('Invalid GitHub source.');
  const parts = source.split('#');
  if (parts.length > 2 || (parts.length === 2 && !SHA.test(parts[1]))) {
    throw new Error('A source #ref must be a full 40-character commit SHA.');
  }
  let repository = parts[0];
  if (repository.startsWith('https://')) {
    const url = new URL(repository);
    if (url.hostname !== 'github.com' || url.port || url.username || url.password || url.search) {
      throw new Error('Source URLs must use https://github.com without credentials, ports, or query strings.');
    }
    repository = url.pathname.replace(/^\//, '').replace(/\/$/, '');
  }
  repository = repository.replace(/\.git$/, '');
  if (!/^[A-Za-z0-9][A-Za-z0-9-]{0,38}\/[A-Za-z0-9_][A-Za-z0-9_.-]*$/.test(repository)) {
    throw new Error(`Invalid GitHub repository: ${source}. Use owner/repo or https://github.com/owner/repo.`);
  }
  if (explicitRef !== undefined && !SHA.test(explicitRef)) throw new Error('Refs must be full 40-character commit SHAs.');
  if (parts[1] && explicitRef && parts[1].toLowerCase() !== explicitRef.toLowerCase()) {
    throw new Error('The source #ref and explicit --ref disagree.');
  }
  const ref = (explicitRef || parts[1])?.toLowerCase() ?? null;
  return { source: repository, ref, url: `https://github.com/${repository}${ref ? `#${ref}` : ''}` };
}

export function validateConfig(config) {
  if (!config || ![1, 2].includes(config.schemaVersion) || config.skillsCli !== CLI || !Array.isArray(config.enhancements) ||
      config.enhancements.length !== ENHANCEMENTS.length) throw new Error('Unsupported enhancements.json configuration.');
  for (const name of ENHANCEMENTS) {
    const matches = config.enhancements.filter(item => item?.name === name);
    if (matches.length !== 1) throw new Error(`Missing or duplicate configuration for ${name}.`);
    const entry = matches[0];
    if (entry.source === 'bundled') {
      if (config.schemaVersion !== 2 || name !== 'humanize-korean' || entry.ref !== null ||
          entry.skillPath !== 'skills/humanize-korean') throw new Error(`Invalid bundled configuration for ${name}.`);
    } else {
      if (!SHA.test(entry.ref ?? '')) throw new Error(`Missing or invalid pinned configuration for ${name}.`);
      normalizeSource(entry.source, entry.ref);
    }
  }
  return config;
}

export function buildPlan(options, config, context = {}) {
  validateConfig(config);
  const root = path.resolve(context.root ?? ROOT);
  const projectDir = path.resolve(context.cwd ?? process.cwd(), options.projectDir ?? '.');
  const home = context.home ?? homedir();
  const env = context.env ?? process.env;
  if (options.global) {
    for (const [agent, variable] of [['claude-code', 'CLAUDE_CONFIG_DIR'], ['codex', 'CODEX_HOME']]) {
      const original = env[variable] ?? '';
      const configured = original.trim();
      if (options.agents.includes(agent) && original !== configured) {
        throw new Error(`${variable} must not contain leading or trailing whitespace for global ${agent} installation. Use an exact absolute path or unset it before retrying.`);
      }
      if (options.agents.includes(agent) && configured && !path.isAbsolute(configured)) {
        throw new Error(`${variable} must be an absolute path for global ${agent} installation. Set it to an absolute path or unset it before retrying.`);
      }
    }
  }
  const scope = options.global ? 'global' : 'project';
  const canonical = options.global ? path.join(home, '.agents', 'skills') : path.join(projectDir, '.agents', 'skills');
  const directories = { codex: canonical, 'claude-code': options.global
    ? path.resolve((env.CLAUDE_CONFIG_DIR ?? '').trim() || path.join(home, '.claude'), 'skills')
    : path.join(projectDir, '.claude', 'skills') };
  const protectedDirectories = new Set([canonical, ...options.agents.map(agent => directories[agent])]);
  if (options.agents.includes('codex')) {
    protectedDirectories.add(options.global
      ? path.resolve((env.CODEX_HOME ?? '').trim() || path.join(home, '.codex'), 'skills')
      : path.join(projectDir, '.codex', 'skills'));
  }
  const skills = [{ name: 'korean-dev-writing', role: '기본 한국어 개발 문서 작성', source: root, ref: null, argument: root, bundled: true }];
  if (options.withEnhancements) {
    for (const name of ENHANCEMENTS) {
      const entry = config.enhancements.find(item => item.name === name);
      const prefix = name === 'humanize-korean' ? 'humanize' : 'stack';
      const override = options[`${prefix}Source`];
      if (entry.source === 'bundled' && override === undefined) {
        if (options[`${prefix}Ref`] !== undefined) {
          throw new Error(`The bundled ${name} has no independent Git ref. Specify --${prefix}-source together with --${prefix}-ref to select an external version.`);
        }
        skills.push({ name, role: entry.role ?? name, source: root, ref: null, argument: root, bundled: true });
        continue;
      }
      const ref = options[`${prefix}Ref`] ?? (override === undefined ? entry.ref : undefined);
      const normalized = normalizeSource(override ?? entry.source, ref);
      // Always select by exact skill name; a source override never inherits a default subpath.
      skills.push({ name, role: entry.role ?? name, ...normalized, argument: normalized.url });
    }
  }
  return { skills, root, projectDir, scope, agents: [...options.agents], copy: options.copy,
    canonical, directories, protectedDirectories: [...protectedDirectories], options };
}

export async function preflightExisting(plan, inspect = lstat) {
  const existing = [];
  for (const skill of plan.skills) {
    for (const directory of plan.protectedDirectories) {
      const target = path.join(directory, skill.name);
      try { await inspect(target); existing.push(target); }
      catch (error) { if (error.code !== 'ENOENT') throw error; }
    }
  }
  if (existing.length && !plan.options.replaceExisting) {
    throw new Error(`Existing skills found; nothing was installed.\n${existing.map(item => `  ${item}`).join('\n')}\nReview their sources, then use --replace-existing to permit replacement. --yes alone does not permit replacement.`);
  }
  return existing;
}

/** Prefix arguments let callers run npm without a shell, including on Windows. */
export function resolveNpmLauncher({ platform = process.platform, env = process.env,
  execPath = process.execPath, exists = existsSync } = {}) {
  const p = platform === 'win32' ? path.win32 : path;
  const inherited = env.npm_execpath;
  if (inherited && p.isAbsolute(inherited) && p.basename(inherited).toLowerCase() === 'npm-cli.js' && exists(inherited)) {
    return { command: execPath, args: [inherited] };
  }
  if (platform !== 'win32') return { command: 'npm', args: [] };
  const pathValue = Object.entries(env).find(([name]) => name.toLowerCase() === 'path')?.[1] ?? '';
  const candidates = [p.join(p.dirname(execPath), 'node_modules', 'npm', 'bin', 'npm-cli.js'),
    ...pathValue.split(';').filter(Boolean).map(directory => p.join(directory, 'node_modules', 'npm', 'bin', 'npm-cli.js'))];
  const npmCli = candidates.find(candidate => exists(candidate));
  if (!npmCli) throw new Error('Could not locate npm-cli.js on Windows. Install Node.js with npm or run this installer through npm exec.');
  return { command: execPath, args: [npmCli] };
}

export function installArguments(plan, skill) {
  return ['exec', '--yes', `--package=${CLI}`, '--', 'skills', 'add', skill.argument,
    '--skill', skill.name, '--agent', ...plan.agents, '--yes', '--json',
    ...(plan.scope === 'global' ? ['--global'] : []), ...(plan.copy ? ['--copy'] : [])];
}

export function validateInstallResult(result, plan, skill) {
  if (result.code !== 0) {
    const details = [];
    if (result.stderr?.trim()) details.push(result.stderr.trim());
    try {
      const json = JSON.parse(result.stdout);
      const failures = (Array.isArray(json) ? json : [json])
        .filter(record => record && typeof record === 'object' &&
          (record.status === 'failed' || record.status === 'skipped' || typeof record.error === 'string'))
        .slice(0, 3)
        .map(record => Object.fromEntries(['name', 'status', 'error']
          .filter(key => typeof record[key] === 'string')
          .map(key => [key, record[key].slice(0, key === 'error' ? 1024 : 128)])));
      if (failures.length) {
        const summary = JSON.stringify(failures);
        details.push(`CLI failure details: ${summary.slice(0, 4096)}${summary.length > 4096 ? '… [truncated]' : ''}`);
      }
    } catch { /* A nonzero exit remains a failure even without valid JSON diagnostics. */ }
    throw new Error(`skills exited with ${result.code ?? 'no exit status'}${details.length ? `:\n${details.join('\n')}` : '.'}`);
  }
  let records;
  try { records = JSON.parse(result.stdout); } catch { throw new Error('skills returned malformed or empty JSON.'); }
  if (!Array.isArray(records) || records.length !== 1 || records[0]?.name !== skill.name || records[0]?.status !== 'installed') {
    throw new Error(`skills did not confirm installation of exactly ${skill.name}: ${JSON.stringify(records)}`);
  }
  const record = records[0];
  const aliases = { codex: 'codex', Codex: 'codex', 'claude-code': 'claude-code', 'Claude Code': 'claude-code' };
  const agents = Array.isArray(record.agents) ? record.agents.map(agent => aliases[agent]) : [];
  if (agents.length !== plan.agents.length || new Set(agents).size !== agents.length ||
      agents.some(agent => !plan.agents.includes(agent))) throw new Error('skills reported unexpected or skipped agents.');
  const allowedPaths = new Set([path.join(plan.canonical, skill.name),
    ...plan.agents.map(agent => path.join(plan.directories[agent], skill.name))].map(item => path.resolve(item)));
  if (record.scope !== plan.scope || typeof record.path !== 'string' || !path.isAbsolute(record.path) ||
      !allowedPaths.has(path.resolve(record.path))) throw new Error('skills reported an unexpected installation path or scope.');
  if (!['symlink', 'copy'].includes(record.mode) || (plan.copy && record.mode !== 'copy')) throw new Error('skills reported an unexpected installation mode.');
  if (record.ref !== skill.ref) throw new Error('skills reported a different Git ref from the requested source.');
  return record;
}

export function runCommand(command, args, { cwd, env = process.env } = {}) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, { cwd, env, shell: false, windowsHide: true, stdio: ['ignore', 'pipe', 'pipe'] });
    let stdout = '';
    let stderr = '';
    let tooLarge = false;
    child.stdout.setEncoding('utf8');
    child.stderr.setEncoding('utf8');
    child.stdout.on('data', chunk => {
      stdout += chunk;
      if (stdout.length > 8 * 1024 * 1024) { tooLarge = true; child.kill(); }
    });
    child.stderr.on('data', chunk => { stderr = (stderr + chunk).slice(-1024 * 1024); });
    child.on('error', reject);
    child.on('close', code => tooLarge ? reject(new Error('skills JSON output exceeded 8 MiB.')) : resolve({ code, stdout, stderr }));
  });
}

function renderPlan(plan) {
  const lines = [`Installation plan (${plan.options.withEnhancements ? 'enhanced' : 'basic'})`,
    `Scope: ${plan.scope}${plan.scope === 'project' ? ` — ${plan.projectDir}` : ''}`,
    `Agents: ${plan.agents.join(', ')}; mode: ${plan.copy ? 'copy' : 'symlink'}`,
    `Installer: ${CLI}; replacement: ${plan.options.replaceExisting ? 'explicitly allowed' : 'blocked'}`];
  for (const skill of plan.skills) lines.push(`\n${skill.name} — ${skill.role}\n  Source: ${skill.source}\n  Ref: ${skill.ref ?? (skill.bundled ? 'bundled package content' : 'upstream default branch (not pinned)')}`);
  for (const agent of plan.agents) lines.push(`\n${agent} destination: ${plan.directories[agent]}`);
  return lines.join('\n');
}

export async function main(argv = process.argv.slice(2), dependencies = {}) {
  const output = dependencies.output ?? (message => process.stdout.write(`${message}\n`));
  const errorOutput = dependencies.errorOutput ?? (message => process.stderr.write(`${message}\n`));
  const isTTY = dependencies.isTTY ?? Boolean(process.stdin.isTTY && process.stdout.isTTY);
  const prompt = dependencies.prompt ?? (async question => {
    const readline = createInterface({ input: process.stdin, output: process.stdout });
    try { return await readline.question(question); } finally { readline.close(); }
  });
  const completed = [];
  let current;
  try {
    const options = parseArgs(argv);
    if (options.help) { output(HELP); return 0; }
    const version = (dependencies.nodeVersion ?? process.versions.node).split('.').map(Number);
    if (version[0] < 22 || (version[0] === 22 && version[1] < 20)) throw new Error('Node.js >=22.20.0 is required.');
    if (!options.agents.length) {
      if (!isTTY) throw new Error('Choose an agent explicitly in non-interactive mode: -a codex, -a claude-code, or both.');
      const selection = (await prompt('Agents: 1) Codex  2) Claude Code  3) Both [1/2/3]: ')).trim().toLowerCase();
      options.agents = ({ '1': ['codex'], codex: ['codex'], '2': ['claude-code'], 'claude-code': ['claude-code'], '3': AGENTS, both: AGENTS })[selection];
      if (!options.agents) throw new Error('No valid agent selected.');
    }
    const root = dependencies.root ?? ROOT;
    const config = dependencies.config ?? JSON.parse(await readFile(path.join(root, 'enhancements.json'), 'utf8'));
    const plan = buildPlan(options, config, { ...dependencies, root });
    if (!(await (dependencies.stat ?? stat)(plan.projectDir)).isDirectory()) throw new Error('Project directory must already exist.');
    output(renderPlan(plan));
    const existing = await preflightExisting(plan, dependencies.lstat ?? lstat);
    if (existing.length) output(`\nExisting locations that may be replaced:\n${existing.map(item => `  ${item}`).join('\n')}`);
    if (options.dryRun) { output('\nDry run complete. No commands were run and no files were written.'); return 0; }
    if (!options.yes) {
      if (!isTTY) throw new Error('Non-interactive installation requires --yes after reviewing a --dry-run plan.');
      if (!/^(y|yes)$/i.test((await prompt('\nInstall this plan? [y/N]: ')).trim())) {
        output('Installation cancelled. No files were written.'); return 0;
      }
    }
    const launcher = (dependencies.resolveNpmLauncher ?? resolveNpmLauncher)({ env: dependencies.env ?? process.env });
    const runner = dependencies.run ?? runCommand;
    for (const skill of plan.skills) {
      current = skill.name;
      output(`\nInstalling ${skill.name}…`);
      const result = await runner(launcher.command, [...launcher.args, ...installArguments(plan, skill)],
        { cwd: plan.projectDir, env: dependencies.env ?? process.env });
      const record = validateInstallResult(result, plan, skill);
      completed.push(skill.name);
      output(`Installed ${skill.name}: ${record.path}`);
      current = undefined;
    }
    output(`\nInstallation complete: ${completed.join(', ')}.`);
    return 0;
  } catch (error) {
    errorOutput(`Installation failed${current ? ` while installing ${current}` : ''}: ${error.message}`);
    if (completed.length) errorOutput(`Confirmed installed: ${completed.join(', ')}. These installations have been kept.`);
    if (current) errorOutput(`${current} may have partial files. Inspect the selected destinations before retrying; no rollback or deletion was performed.`);
    return 1;
  }
}

if (process.argv[1] && existsSync(process.argv[1]) && realpathSync(process.argv[1]) === fileURLToPath(import.meta.url)) {
  process.exitCode = await main();
}
