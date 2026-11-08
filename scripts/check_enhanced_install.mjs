#!/usr/bin/env node
/** Exercise the published-package entry point and real skills CLI in temporary projects. */
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { existsSync, lstatSync, mkdirSync, mkdtempSync, readFileSync, realpathSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { resolveNpmLauncher } from './install.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const temporary = mkdtempSync(path.join(tmpdir(), 'korean-dev-writing-smoke-'));
const configuration = JSON.parse(readFileSync(path.join(root, 'enhancements.json'), 'utf8'));
const baseFiles = ['LICENSE', 'SKILL.md', 'agents/openai.yaml', 'references/before-after-guide.md',
  'references/document-types.md', 'references/reading-flow.md'];
const env = { ...process.env, CI: '1', DISABLE_TELEMETRY: '1',
  npm_config_cache: process.env.npm_config_cache || path.join(temporary, 'npm-cache'),
  npm_config_fetch_retries: '0', npm_config_fetch_timeout: '30000', SKILLS_CLONE_TIMEOUT_MS: '60000' };

function run(command, args, cwd, expectedStatus = 0) {
  const result = spawnSync(command, args, { cwd, env, encoding: 'utf8', timeout: 240_000, maxBuffer: 8 * 1024 * 1024 });
  if (result.error || result.status !== expectedStatus) {
    throw new Error(`${command} ${args.join(' ')}\n${result.error?.message || `exit ${result.status}`}\n${result.stdout}\n${result.stderr}`);
  }
  return result.stdout;
}

function project(name) {
  const directory = path.join(temporary, name);
  mkdirSync(directory);
  return directory;
}

function withinProject(target, directory) {
  const relative = path.relative(realpathSync(directory), realpathSync(target));
  assert(!relative.startsWith('..') && !path.isAbsolute(relative), `installation escaped temporary project: ${target}`);
}

function verifyBase(directory) {
  for (const agentDirectory of ['.agents/skills', '.claude/skills']) {
    const installed = path.join(directory, agentDirectory, 'korean-dev-writing');
    withinProject(installed, directory);
    for (const relative of baseFiles) {
      assert.deepEqual(readFileSync(path.join(installed, relative)),
        readFileSync(path.join(root, 'skills/korean-dev-writing', relative)), `${agentDirectory}: ${relative}`);
    }
  }
}

try {
  const launcher = resolveNpmLauncher();
  const npm = (args, cwd) => run(launcher.command, [...launcher.args, ...args], cwd);
  const packed = JSON.parse(npm(['pack', '--ignore-scripts', '--json', '--pack-destination', temporary], root));
  assert.equal(packed.length, 1);
  const filePaths = new Set(packed[0].files.map(file => file.path));
  for (const expected of ['scripts/install.mjs', 'enhancements.json', 'package.json', ...baseFiles.map(p => `skills/korean-dev-writing/${p}`)]) {
    assert(filePaths.has(expected), `npm package is missing ${expected}`);
  }
  assert(![...filePaths].some(p => p.startsWith('evaluations/') || p.startsWith('docs/')), 'evaluation or comparison files leaked into npm package');
  const archive = path.join(temporary, packed[0].filename);
  const basic = project('basic-copy');
  console.log('Installing the packaged basic skill for Codex and Claude Code (copy mode).');
  npm(['exec', '--yes', `--package=${archive}`, '--', 'korean-dev-writing-install',
    '-a', 'codex', '-a', 'claude-code', '--copy', '--yes'], basic);
  verifyBase(basic);
  assert(!lstatSync(path.join(basic, '.claude/skills/korean-dev-writing')).isSymbolicLink());
  assert(!existsSync(path.join(basic, '.agents/skills/humanize-korean')));
  console.log('PASS: package entry point installs exactly the basic skill with unchanged resources.');

  const enhanced = project('enhanced');
  console.log('Installing the enhanced profile for both agents from the pinned upstreams.');
  const enhancedOutput = run(process.execPath, [path.join(root, 'scripts/install.mjs'),
    '--with-enhancements', '-a', 'codex', '-a', 'claude-code', '--yes'], enhanced);
  verifyBase(enhanced);
  const expectedResources = {
    'humanize-korean': ['references/core-workflow.md', 'scripts/segment.py', 'scripts/reassemble.py', 'scripts/audit_revision.py'],
    'stack-diagram': ['references/geometry.md', 'scripts/fetch_icons.py', 'scripts/build.py', 'scripts/render_png.py', 'assets/template.html', 'assets/fonts'],
  };
  const lock = JSON.parse(readFileSync(path.join(enhanced, 'skills-lock.json'), 'utf8'));
  for (const skill of configuration.enhancements) {
    assert.equal(lock.skills[skill.name]?.ref, skill.ref, `${skill.name}: installed ref differs from configured pin`);
    for (const agentDirectory of ['.agents/skills', '.claude/skills']) {
      const installed = path.join(enhanced, agentDirectory, skill.name);
      withinProject(installed, enhanced);
      const skillText = readFileSync(path.join(installed, 'SKILL.md'), 'utf8');
      assert(new RegExp(`^name:\\s*${skill.name}\\s*$`, 'm').test(skillText), `${skill.name}: wrong skill metadata`);
      for (const relative of expectedResources[skill.name]) {
        assert(existsSync(path.join(installed, relative)), `${skill.name}: missing ${relative}`);
      }
    }
  }
  console.log(enhancedOutput.trim());
  console.log('PASS: both agents receive all three skills, pinned refs, scripts, references, and assets.');

  const existing = path.join(basic, '.agents/skills/korean-dev-writing/SKILL.md');
  const before = createHash('sha256').update(readFileSync(existing)).digest('hex');
  run(process.execPath, [path.join(root, 'scripts/install.mjs'),
    '--with-enhancements', '-a', 'codex', '--yes'], basic, 1);
  assert.equal(createHash('sha256').update(readFileSync(existing)).digest('hex'), before);
  assert(!existsSync(path.join(basic, '.agents/skills/humanize-korean')));
  console.log('PASS: existing skill stops the entire installation before any new skill is written.');

  const dry = project('dry-run');
  run(process.execPath, [path.join(root, 'scripts/install.mjs'), '--with-enhancements',
    '-a', 'codex', '--dry-run'], dry);
  assert(!existsSync(path.join(dry, '.agents')));
  console.log('PASS: dry run leaves skill directories absent.');
  console.log('Installation only: no agent invocation, proofreading, image rendering, or quality comparison was performed.');
} finally {
  rmSync(temporary, { recursive: true, force: true });
}
