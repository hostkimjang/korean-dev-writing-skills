import assert from 'node:assert/strict';
import { mkdtemp, mkdir, readFile, readdir, rm, symlink, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { buildPlan, installArguments, main, normalizeSource, parseArgs, preflightExisting,
  resolveNpmLauncher, validateConfig, validateInstallResult } from './install.mjs';

const PIN_A = 'a'.repeat(40);
const PIN_B = 'b'.repeat(40);
const config = {
  schemaVersion: 1, skillsCli: 'skills@1.7.5', enhancements: [
    { name: 'humanize-korean', source: 'original/humanize-korean', ref: PIN_A, skillPath: 'humanize-korean' },
    { name: 'stack-diagram', source: 'original/stack-diagram', ref: PIN_B, skillPath: 'skills/stack-diagram' },
  ],
};

async function fixture(t) {
  const directory = await mkdtemp(path.join(tmpdir(), 'korean-installer-test-'));
  t.after(() => rm(directory, { recursive: true, force: true }));
  const cwd = path.join(directory, 'project with spaces');
  const root = path.join(directory, 'package with spaces');
  const home = path.join(directory, 'home');
  await Promise.all([cwd, root, home].map(value => mkdir(value)));
  const output = [];
  const errors = [];
  const calls = [];
  const dependencies = { config, cwd, root, home, env: {}, isTTY: false,
    output: value => output.push(value), errorOutput: value => errors.push(value),
    resolveNpmLauncher: () => ({ command: '/fake/node', args: ['/fake/npm-cli.js'] }),
    run: async (command, args, options) => { calls.push({ command, args, options }); throw new Error('Unexpected child command.'); } };
  return { directory, cwd, root, home, output, errors, calls, dependencies };
}

function installed(plan, skill, extra = {}) {
  return { code: 0, stdout: JSON.stringify([{ name: skill.name, status: 'installed',
    source: skill.source, ref: skill.ref, path: path.join(plan.canonical, skill.name), scope: plan.scope,
    agents: plan.agents.map(agent => agent === 'codex' ? 'Codex' : 'Claude Code'),
    mode: plan.copy ? 'copy' : 'symlink', ...extra }]), stderr: 'Ordinary CLI progress belongs on stderr.' };
}

test('strict arguments reject unknown switches and ignored enhancement configuration', () => {
  for (const args of [['--agent'], ['-a', 'cursor'], ['--copy=true'], ['--wat'],
    ['--humanize-ref', PIN_A], ['--project-dir', 'one', '--project-dir', 'two']]) {
    assert.throws(() => parseArgs(args));
  }
  const options = parseArgs(['-a', 'codex', '--agent=claude-code', '-a', 'codex', '--global']);
  assert.deepEqual(options.agents, ['codex', 'claude-code']);
  assert.equal(options.global, true);
});

test('sources permit GitHub repositories and immutable SHAs only', () => {
  assert.deepEqual(normalizeSource(`https://github.com/owner/repo.git#${PIN_A}`), {
    source: 'owner/repo', ref: PIN_A, url: `https://github.com/owner/repo#${PIN_A}`,
  });
  assert.equal(normalizeSource('owner/repo', PIN_B).ref, PIN_B);
  for (const source of ['--help', 'file:///tmp/skill', 'git@github.com:owner/repo',
    'https://evil.example/owner/repo', 'https://user:pass@github.com/owner/repo',
    'https://github.com:443/owner/repo?token=x', 'owner/repo/subdir', 'owner/repo@skill',
    'owner/repo#main', 'owner/repo#', 'owner/repo;rm', 'owner/repo$(echo bad)', 'owner/repo\n']) {
    assert.throws(() => normalizeSource(source), source);
  }
  assert.throws(() => normalizeSource('owner/repo', 'v1.0'));
  assert.throws(() => normalizeSource(`owner/repo#${PIN_A}`, PIN_B));
});

test('configuration rejects unexpected versions, names, duplicates, and mutable refs', () => {
  assert.equal(validateConfig(config), config);
  for (const invalid of [null, { ...config, schemaVersion: 3 }, { ...config, skillsCli: 'skills@latest' },
    { ...config, enhancements: [config.enhancements[0], config.enhancements[0]] },
    { ...config, enhancements: [{ ...config.enhancements[0], ref: 'main' }, config.enhancements[1]] }]) {
    assert.throws(() => validateConfig(invalid));
  }
});

test('source overrides discard the default ref and subpath; explicit new refs remain', async t => {
  const f = await fixture(t);
  const plan = buildPlan(parseArgs(['-a', 'codex', '--with-enhancements', '--humanize-source', 'new-author/different-layout']), config, f);
  assert.equal(plan.skills[1].ref, null);
  assert.equal(plan.skills[1].argument, 'https://github.com/new-author/different-layout');
  assert(!plan.skills[1].argument.includes('humanize-korean/'));
  assert.equal(plan.skills[2].ref, PIN_B);
  const pinned = buildPlan(parseArgs(['-a', 'codex', '--with-enhancements', '--humanize-source', 'new/repo', '--humanize-ref', PIN_B]), config, f);
  assert.equal(pinned.skills[1].argument, `https://github.com/new/repo#${PIN_B}`);
  const embedded = buildPlan(parseArgs(['-a', 'codex', '--with-enhancements', '--stack-source', `new/stack#${PIN_A}`]), config, f);
  assert.equal(embedded.skills[2].ref, PIN_A);
});

test('child arguments have one source and exact skill with explicit agents, scope and mode', async t => {
  const f = await fixture(t);
  const plan = buildPlan(parseArgs(['-a', 'codex', '-a', 'claude-code', '--global', '--copy']), config, f);
  assert.deepEqual(installArguments(plan, plan.skills[0]), ['exec', '--yes', '--package=skills@1.7.5', '--',
    'skills', 'add', f.root, '--skill', 'korean-dev-writing', '--agent', 'codex', 'claude-code',
    '--yes', '--json', '--global', '--copy']);
});

test('Windows npm launch uses node and npm-cli.js with argv, never a command shell', () => {
  const npmCli = 'C:\\Program Files\\nodejs\\node_modules\\npm\\bin\\npm-cli.js';
  const node = 'C:\\Program Files\\nodejs\\node.exe';
  assert.deepEqual(resolveNpmLauncher({ platform: 'win32', execPath: node, env: {}, exists: item => item === npmCli }),
    { command: node, args: [npmCli] });
  const inherited = 'D:\\npm cache\\npm\\bin\\npm-cli.js';
  assert.deepEqual(resolveNpmLauncher({ platform: 'win32', execPath: node,
    env: { npm_execpath: inherited }, exists: item => item === inherited }), { command: node, args: [inherited] });
  assert.throws(() => resolveNpmLauncher({ platform: 'win32', execPath: node,
    env: { npm_execpath: 'C:\\pnpm\\pnpm.cjs' }, exists: () => false }), /npm-cli/);
});

test('Windows npm discovery handles Path and POSIX preserves an npm exec launcher', () => {
  const candidate = 'D:\\Tools\\node_modules\\npm\\bin\\npm-cli.js';
  assert.deepEqual(resolveNpmLauncher({ platform: 'win32', execPath: 'C:\\Node\\node.exe',
    env: { Path: 'D:\\Tools;D:\\Other' }, exists: item => item === candidate }),
  { command: 'C:\\Node\\node.exe', args: [candidate] });
  assert.deepEqual(resolveNpmLauncher({ platform: 'linux', execPath: '/bin/node', env: {}, exists: () => false }),
    { command: 'npm', args: [] });
  assert.deepEqual(resolveNpmLauncher({ platform: 'linux', execPath: '/bin/node',
    env: { npm_execpath: '/opt/npm/bin/npm-cli.js' }, exists: () => true }),
  { command: '/bin/node', args: ['/opt/npm/bin/npm-cli.js'] });
});

test('help works without npm, agents, configuration, or project reads', async t => {
  const f = await fixture(t);
  assert.equal(await main(['--help'], { ...f.dependencies, config: undefined, root: '/absent',
    stat: () => { throw new Error('Unexpected filesystem inspection'); } }), 0);
  assert.equal(f.calls.length, 0);
  assert.match(f.output.join('\n'), /--replace-existing/);
});

test('invalid arguments and invalid refs fail before any install', async t => {
  const f = await fixture(t);
  for (const args of [['--unknown'], ['-a', 'codex', '--with-enhancements', '--stack-ref', 'main'],
    ['-a', 'codex', '--with-enhancements', '--humanize-source', '$(bad)']]) {
    assert.equal(await main(args, f.dependencies), 1);
  }
  assert.equal(f.calls.length, 0);
  assert.deepEqual(await readdir(f.cwd), []);
});

test('non-interactive runs require explicit agents and confirmation before installation', async t => {
  const f = await fixture(t);
  assert.equal(await main(['--yes'], f.dependencies), 1);
  assert.match(f.errors.at(-1), /agent explicitly/);
  assert.equal(await main(['-a', 'codex'], f.dependencies), 1);
  assert.match(f.errors.at(-1), /requires --yes/);
  assert.equal(f.calls.length, 0);
});

test('dry run is offline and leaves the project untouched', async t => {
  const f = await fixture(t);
  assert.equal(await main(['--with-enhancements', '-a', 'codex', '-a', 'claude-code', '--dry-run'],
    { ...f.dependencies, resolveNpmLauncher: () => { throw new Error('Unexpected npm discovery'); } }), 0);
  assert.equal(f.calls.length, 0);
  assert.deepEqual(await readdir(f.cwd), []);
  assert.match(f.output.join('\n'), /humanize-korean/);
  assert.match(f.output.join('\n'), new RegExp(PIN_B));
});

test('companion collision stops before core installation; --yes does not bypass it', async t => {
  const f = await fixture(t);
  const existing = path.join(f.cwd, '.agents', 'skills', 'stack-diagram');
  await mkdir(existing, { recursive: true });
  await writeFile(path.join(existing, 'SKILL.md'), 'another author');
  assert.equal(await main(['-a', 'codex', '--with-enhancements', '--yes'], f.dependencies), 1);
  assert.equal(f.calls.length, 0);
  assert.match(f.errors.join('\n'), /--replace-existing/);
  assert.equal(await readFile(path.join(existing, 'SKILL.md'), 'utf8'), 'another author');
});

test('preflight detects broken symlinks and legacy Codex directories', async t => {
  const f = await fixture(t);
  const parent = path.join(f.cwd, '.codex', 'skills');
  await mkdir(parent, { recursive: true });
  await symlink(path.join(f.cwd, 'absent'), path.join(parent, 'korean-dev-writing'), 'dir');
  const plan = buildPlan(parseArgs(['-a', 'codex']), config, f);
  await assert.rejects(preflightExisting(plan), /Existing skills/);
  plan.options.replaceExisting = true;
  assert.deepEqual(await preflightExisting(plan), [path.join(parent, 'korean-dev-writing')]);
});

test('global preflight uses canonical and configured Claude/Codex locations without changing HOME', async t => {
  const f = await fixture(t);
  const customClaude = path.join(f.directory, 'custom Claude');
  const customCodex = path.join(f.directory, 'custom Codex');
  const plan = buildPlan(parseArgs(['-g', '-a', 'codex', '-a', 'claude-code']), config,
    { ...f, env: { CLAUDE_CONFIG_DIR: customClaude, CODEX_HOME: customCodex } });
  assert.deepEqual(new Set(plan.protectedDirectories), new Set([
    path.join(f.home, '.agents', 'skills'), path.join(customClaude, 'skills'), path.join(customCodex, 'skills') ]));
  const occupied = path.join(customClaude, 'skills', 'korean-dev-writing');
  await mkdir(occupied, { recursive: true });
  await assert.rejects(preflightExisting(plan), /custom Claude/);
});

test('global relative agent homes fail before plan or commands, even with a different project directory', async t => {
  const f = await fixture(t);
  for (const [agent, variable] of [['claude-code', 'CLAUDE_CONFIG_DIR'], ['codex', 'CODEX_HOME']]) {
    const env = Object.freeze({ [variable]: 'relative-agent-config' });
    const previousOutput = f.output.length;
    assert.equal(await main(['-g', '-a', agent, '--project-dir', f.root, '--yes', '--replace-existing'],
      { ...f.dependencies, env }), 1);
    assert.match(f.errors.at(-1), new RegExp(`${variable} must be an absolute path`));
    assert.equal(f.output.length, previousOutput);
    assert.equal(env[variable], 'relative-agent-config');
  }
  assert.equal(f.calls.length, 0);
  assert.deepEqual(await readdir(f.cwd), []);
  assert.deepEqual(await readdir(f.root), []);
  assert.doesNotThrow(() => buildPlan(parseArgs(['-a', 'codex', '-a', 'claude-code']), config,
    { ...f, env: { CLAUDE_CONFIG_DIR: 'relative', CODEX_HOME: 'relative' } }));
  assert.doesNotThrow(() => buildPlan(parseArgs(['-g', '-a', 'codex']), config,
    { ...f, env: { CLAUDE_CONFIG_DIR: 'relative-unselected-agent' } }));
});

test('global agent homes with padded or whitespace-only values are rejected without changing the environment', async t => {
  const f = await fixture(t);
  for (const [agent, variable] of [['claude-code', 'CLAUDE_CONFIG_DIR'], ['codex', 'CODEX_HOME']]) {
    for (const value of [` ${path.join(f.home, 'config')} `, '   ']) {
      const env = Object.freeze({ [variable]: value });
      assert.equal(await main(['-g', '-a', agent, '--yes'], { ...f.dependencies, env }), 1);
      assert.match(f.errors.at(-1), new RegExp(`${variable} must not contain leading or trailing whitespace`));
      assert.equal(env[variable], value);
    }
  }
  assert.equal(f.calls.length, 0);
  assert.deepEqual(f.output, []);
  assert.deepEqual(await readdir(f.home), []);
});

test('basic install executes exactly one child and accepts display names in JSON', async t => {
  const f = await fixture(t);
  const args = ['-a', 'codex', '-a', 'claude-code', '--copy', '--yes'];
  const plan = buildPlan(parseArgs(args), config, f);
  const result = await main(args, { ...f.dependencies, run: async (command, childArgs, options) => {
    f.calls.push({ command, args: childArgs, options });
    return installed(plan, plan.skills[0]);
  } });
  assert.equal(result, 0);
  assert.equal(f.calls.length, 1);
  assert.equal(f.calls[0].options.cwd, f.cwd);
  assert(f.calls[0].args.includes(f.root));
  assert.match(f.output.at(-1).trim(), /^Installation complete: korean-dev-writing\./);
});

test('enhanced installs execute sequentially and use each pinned upstream', async t => {
  const f = await fixture(t);
  const args = ['--with-enhancements', '-a', 'codex', '--yes'];
  const plan = buildPlan(parseArgs(args), config, f);
  let active = 0;
  assert.equal(await main(args, { ...f.dependencies, run: async (command, childArgs) => {
    assert.equal(active, 0);
    active++;
    const skill = plan.skills[f.calls.length];
    f.calls.push(childArgs);
    await Promise.resolve();
    active--;
    return installed(plan, skill);
  } }), 0);
  assert.equal(f.calls.length, 3);
  assert(f.calls[1].includes(`https://github.com/original/humanize-korean#${PIN_A}`));
  assert(f.calls[2].includes(`https://github.com/original/stack-diagram#${PIN_B}`));
});

test('explicit replacement is required and is passed through one final confirmation', async t => {
  const f = await fixture(t);
  const existing = path.join(f.cwd, '.agents', 'skills', 'korean-dev-writing');
  await mkdir(existing, { recursive: true });
  const args = ['--replace-existing'];
  let prompts = 0;
  const plan = buildPlan(parseArgs(['-a', 'codex', '--replace-existing']), config, f);
  assert.equal(await main(args, { ...f.dependencies, isTTY: true,
    prompt: async () => (++prompts === 1 ? '1' : 'yes'),
    run: async () => installed(plan, plan.skills[0]) }), 0);
  assert.equal(prompts, 2); // One agent selection and one installation confirmation.
});

test('declining confirmation does not install', async t => {
  const f = await fixture(t);
  let prompts = 0;
  assert.equal(await main(['-a', 'codex'], { ...f.dependencies, isTTY: true,
    prompt: async () => { prompts++; return ''; } }), 0);
  assert.equal(prompts, 1);
  assert.equal(f.calls.length, 0);
  assert.match(f.output.at(-1), /cancelled/);
});

test('a failed companion stops further calls and keeps confirmed and partial files', async t => {
  const f = await fixture(t);
  const args = ['--with-enhancements', '-a', 'codex', '--yes'];
  const plan = buildPlan(parseArgs(args), config, f);
  assert.equal(await main(args, { ...f.dependencies, run: async () => {
    const skill = plan.skills[f.calls.length];
    f.calls.push(skill.name);
    const destination = path.join(plan.canonical, skill.name);
    await mkdir(destination, { recursive: true });
    await writeFile(path.join(destination, 'SKILL.md'), skill.name);
    return skill.name === 'korean-dev-writing' ? installed(plan, skill)
      : { code: 1, stdout: '[]', stderr: 'Upstream fetch failed.' };
  } }), 1);
  assert.deepEqual(f.calls, ['korean-dev-writing', 'humanize-korean']);
  assert.equal(await readFile(path.join(plan.canonical, 'korean-dev-writing', 'SKILL.md'), 'utf8'), 'korean-dev-writing');
  assert.equal(await readFile(path.join(plan.canonical, 'humanize-korean', 'SKILL.md'), 'utf8'), 'humanize-korean');
  assert.match(f.errors.join('\n'), /Confirmed installed: korean-dev-writing/);
  assert.match(f.errors.join('\n'), /Upstream fetch failed/);
  assert.match(f.errors.join('\n'), /may have partial files/);
  assert(!f.output.some(line => line.includes('Installation complete:')));
});

test('malformed, skipped, wrong-agent, wrong-path, wrong-scope and false-success JSON are rejected', async t => {
  const f = await fixture(t);
  const plan = buildPlan(parseArgs(['--with-enhancements', '-a', 'codex', '-a', 'claude-code', '--copy']), config, f);
  const skill = plan.skills[1];
  for (const bad of [{ code: 0, stdout: '' }, { code: 0, stdout: 'log\n[]' },
    { code: 0, stdout: '[]' }, { code: 0, stdout: '{}' },
    { ...installed(plan, skill), code: 1 },
    installed(plan, skill, { status: 'skipped' }), installed(plan, skill, { status: 'failed' }),
    installed(plan, skill, { name: 'some-other-skill' }),
    installed(plan, skill, { agents: ['Codex'] }), installed(plan, skill, { agents: ['Codex', 'Codex'] }),
    installed(plan, skill, { agents: ['Codex', 'Cursor'] }),
    installed(plan, skill, { path: '/unexpected/path' }), installed(plan, skill, { path: '.agents/skills/humanize-korean' }),
    installed(plan, skill, { scope: 'global' }), installed(plan, skill, { mode: 'symlink' }),
    installed(plan, skill, { ref: PIN_B })]) {
    assert.throws(() => validateInstallResult(bad, plan, skill), JSON.stringify(bad));
  }
  assert.equal(validateInstallResult(installed(plan, skill), plan, skill).name, skill.name);
});

test('invalid JSON during main reports failure and never prints a completed installation', async t => {
  const f = await fixture(t);
  assert.equal(await main(['-a', 'codex', '--yes'], { ...f.dependencies,
    run: async () => ({ code: 0, stdout: '[]', stderr: '' }) }), 1);
  assert.match(f.errors.join('\n'), /did not confirm installation/);
  assert(!f.output.some(line => line.includes('Installation complete:')));
});

test('nonzero exits preserve bounded JSON failure details when stderr is empty', async t => {
  const f = await fixture(t);
  const args = ['-a', 'codex', '--yes'];
  const plan = buildPlan(parseArgs(args), config, f);
  const failure = { code: 1, stderr: '', stdout: JSON.stringify([
    { name: 'korean-dev-writing', status: 'failed', error: 'Repository access denied.', unrelated: 'must not leak' },
  ]) };
  assert.equal(await main(args, { ...f.dependencies, run: async () => failure }), 1);
  const diagnostic = f.errors.join('\n');
  assert.match(diagnostic, /skills exited with 1/);
  assert.match(diagnostic, /"name":"korean-dev-writing"/);
  assert.match(diagnostic, /"status":"failed"/);
  assert.match(diagnostic, /Repository access denied/);
  assert(!diagnostic.includes('must not leak'));
  assert(!f.output.some(line => line.includes('Installation complete:')));
  assert(!diagnostic.includes('Confirmed installed:'));

  const large = { code: 1, stderr: '', stdout: JSON.stringify(Array.from({ length: 20 }, () => ({
    name: 'korean-dev-writing', status: 'failed', error: '\u0001'.repeat(10_000),
  }))) };
  assert.throws(() => validateInstallResult(large, plan, plan.skills[0]), error => {
    assert(error.message.length < 4300);
    assert.match(error.message, /truncated/);
    return true;
  });
  assert.throws(() => validateInstallResult({ code: 2, stdout: 'not JSON', stderr: '' }, plan, plan.skills[0]), /skills exited with 2/);
});

test('minimum Node version is checked before running npm', async t => {
  const f = await fixture(t);
  assert.equal(await main(['-a', 'codex', '--yes'], { ...f.dependencies, nodeVersion: '22.19.0' }), 1);
  assert.equal(f.calls.length, 0);
  assert.match(f.errors.join('\n'), /Node.js >=22.20.0/);
});

function bundledConfig() {
  return { ...config, schemaVersion: 2, enhancements: [
    { name: 'humanize-korean', source: 'bundled', ref: null, skillPath: 'skills/humanize-korean' },
    config.enhancements[1],
  ] };
}

test('enhanced default installs the maintained humanize resources from this package', async t => {
  const f = await fixture(t);
  const settings = bundledConfig();
  const plan = buildPlan(parseArgs(['--with-enhancements', '-a', 'codex']), settings, f);
  assert.equal(plan.skills[1].argument, f.root);
  assert.equal(plan.skills[1].ref, null);
  assert.equal(plan.skills[1].bundled, true);
  assert.equal(plan.skills[2].argument, `https://github.com/original/stack-diagram#${PIN_B}`);
  assert.equal(validateInstallResult(installed(plan, plan.skills[1]), plan, plan.skills[1]).ref, null);
  assert.deepEqual(installArguments(plan, plan.skills[1]).slice(4, 9),
    ['skills', 'add', f.root, '--skill', 'humanize-korean']);
});

test('external humanize override bypasses the bundled variant and can pin its own commit', async t => {
  const f = await fixture(t);
  const plan = buildPlan(parseArgs(['--with-enhancements', '-a', 'codex',
    '--humanize-source', 'author/another-humanize', '--humanize-ref', PIN_A]), bundledConfig(), f);
  assert.equal(plan.skills[1].argument, `https://github.com/author/another-humanize#${PIN_A}`);
  assert.equal(plan.skills[1].bundled, undefined);
  const unpinned = buildPlan(parseArgs(['--with-enhancements', '-a', 'codex',
    '--humanize-source', 'author/another-humanize']), bundledConfig(), f);
  assert.equal(unpinned.skills[1].ref, null);
});

test('a standalone ref cannot silently change the provenance of a bundled skill', async t => {
  const f = await fixture(t);
  const result = await main(['--with-enhancements', '-a', 'codex', '--humanize-ref', PIN_A, '--yes'],
    { ...f.dependencies, config: bundledConfig() });
  assert.equal(result, 1);
  assert.equal(f.calls.length, 0);
  assert.match(f.errors.join('\n'), /--humanize-source/);
});

test('bundled configuration rejects external refs, unknown resources and unsupported schema', () => {
  const settings = bundledConfig();
  assert.equal(validateConfig(settings), settings);
  for (const entry of [
    { ...settings.enhancements[0], ref: PIN_A },
    { ...settings.enhancements[0], skillPath: '../outside' },
    { ...settings.enhancements[1], source: 'bundled', ref: null },
  ]) {
    const malformed = { ...settings, enhancements: settings.enhancements.map(x => x.name === entry.name ? entry : x) };
    assert.throws(() => validateConfig(malformed), /bundled/);
  }
  assert.throws(() => validateConfig({ ...settings, schemaVersion: 1 }), /bundled/);
});
