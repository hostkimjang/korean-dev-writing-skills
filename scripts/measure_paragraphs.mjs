#!/usr/bin/env node
/** Describe Markdown structure. These counts are review signals, not quality scores.
 * Usage: node scripts/measure_paragraphs.mjs DOCUMENT.md [DOCUMENT.md ...]
 * A JSON source with a string `draft` field measures that draft instead.
 */
import fs from 'node:fs';
import { createHash } from 'node:crypto';
import { marked } from './vendor/marked/marked.esm.mjs';

const paths = process.argv.slice(2);
if (!paths.length) throw new Error('Supply Markdown documents or source JSON files with a draft field.');
const documents = paths.map(path => {
  const bytes = fs.readFileSync(path);
  let text = bytes.toString('utf8');
  const field = path.endsWith('.json') ? 'draft' : null;
  if (field) {
    text = JSON.parse(text).draft;
    if (typeof text !== 'string') throw new Error('Source JSON has no string draft field: ' + path);
  }
  const tokens = marked.lexer(text);
  const paragraphs = tokens.filter(token => token.type === 'paragraph');
  const lengths = paragraphs.map(token => [...token.raw.trim()].length);
  const headings = tokens.filter(token => token.type === 'heading' && token.depth >= 2);
  return {
    path, field, file_sha256: createHash('sha256').update(bytes).digest('hex'),
    characters: [...text].length,
    prose_paragraphs: lengths.length,
    longest_prose_paragraph: Math.max(0, ...lengths),
    prose_paragraphs_over_250: lengths.filter(n => n > 250).length,
    prose_paragraphs_over_300: lengths.filter(n => n > 300).length,
    subheadings: headings.length,
    numbered_subheadings: headings.filter(token => /^\d+[.)]\s/.test(token.text)).length,
    judgment_tags: (text.match(/\(판단\)|\(추측\)/g) || []).length,
  };
});
process.stdout.write(JSON.stringify({
  method: 'Marked top-level paragraph tokens; raw inline Markdown retained; surrounding whitespace trimmed; Unicode code points. Lists, tables, blockquotes, headings and code blocks are separate token types. Counts do not measure comprehension or semantic completeness.',
  documents,
}, null, 2) + '\n');
