#!/usr/bin/env python3
"""Audit every Markdown file, preserving evidence and exact technical literals.

The already-vendored marked parser supplies GFM links, headings and code blocks.
Python performs local-reference, prose, exemption, rule-mapping and preservation
checks. No network request is made. The prose result is deliberately separate
from literal examples and immutable historical records; a raw grep is not a
zero-findings prose audit.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict, dataclass, field
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import sys
import unicodedata
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
BASE = "371682457527462305d13b75641045b7c16ffdb1"
RULE_PATH = "skills/humanize-korean/references/development-rules.json"
RULE_DOCS = (
    "skills/humanize-korean/SKILL.md",
    "skills/humanize-korean/references/quick-rules.md",
    "skills/humanize-korean/references/rewriting-playbook.md",
    "skills/humanize-korean/references/ai-tell-taxonomy.md",
)
REQUIRED_RULE_IDS = (
    "DEV-A01", "DEV-A02", "DEV-A03", "DEV-A04",
    "DEV-C01", "DEV-C02", "DEV-E01", "DEV-S01",
)
BEFORE_COLUMNS = {"교정 전", "탐지 표현", "원문", "주어진 정보"}
IGNORED_DIRECTORIES = {".git", "node_modules", ".venv", "venv", "__pycache__", ".pytest_cache"}
PLAIN_ENDING = r"(?<![니시])다\."
SOURCE_START = re.compile(r"<!-- BEGIN SOURCE ([^\r\n]+?) SHA256 ([a-f0-9]{64}) -->")
SOURCE_END = "<!-- END SOURCE -->"
EXAMPLE_START = re.compile(r"<!--\s*lint:example-start\s+([^\r\n]+?)\s*-->")
EXAMPLE_END = re.compile(r"<!--\s*lint:example-end\s*-->")
INLINE_CODE = re.compile(r"(?<!`)(`+)(?!`)(.*?)\1(?!`)", re.S)
NUMBER = re.compile(r"(?<![A-Za-z0-9_])(?:[+-]?\d+(?:[.,:/-]\d+)*(?:[eE][+-]?\d+)?(?:%|ms|[KMGT]?[Bb])?)(?![A-Za-z0-9_])")
# Numeric suffixes inside identifiers are preserved by the identifier check.
TECHNICAL = re.compile(r"^[^\u3131-\u318e\uac00-\ud7a3\s]+(?:[ \t]+[^\u3131-\u318e\uac00-\ud7a3]+)*$")
REFERENCE_USE = re.compile(r"(?<![!\\])!?\[((?:\\.|[^\]\\\n])+)\]\[((?:\\.|[^\]\\\n])*)\]")
BARE_ENV = re.compile(r"(?<![A-Za-z0-9_])[A-Z][A-Z0-9]*_[A-Z0-9_]+(?![A-Za-z0-9_])")
BARE_OPTION = re.compile(r"(?<![A-Za-z0-9_])--[a-z][a-z0-9-]*")
COMMAND_WITH_ARGUMENTS = re.compile(r"^(?:[a-z][a-z0-9_.+-]*|(?:\./|/)[^\s]+)\s+[^\r\n]+$")
CONTAINER_PREFIX = re.compile(r"^[ \t]*(?:(?:>[ \t]?|(?:[-+*]|\d{1,9}[.)])[ \t]+)[ \t]*)*$")
FROZEN_REFERENCE = {
    "path": "evaluations/runs/2026-11-03-v0.4.0/reviews/review-core.md",
    "sha256": "fd7d2129e31895583cc9a4af3308ef31ef6137466ea2e2aac3daaf8a6291c690",
    "destination": "#입력-오류-처리",
    "quote": "> 이 명령은 `error` 항목을 표준 출력으로 내보냅니다. 입력 파일을 읽을 수 없거나 JSON 구문이 잘못된 행이 있을 때의 동작은 [입력 오류 처리](#입력-오류-처리)에서 확인할 수 있습니다.",
    "source": "evaluations/runs/2026-11-03-v0.4.0/outputs/latest/01_cli_readme.md",
    "source_sha256": "deb61dc932ef4c1c41dcee7914f41662428096dad035018a4ac038bfb9b38c4a",
}

PARSER = r'''
import { readFileSync } from 'node:fs';
const { Lexer, walkTokens } = await import(process.argv[1]);
const files = JSON.parse(readFileSync(0, 'utf8'));
const plain = tokens => (tokens || []).map(t => t.tokens ? plain(t.tokens) : t.text || t.raw || '').join('');
const result = {};
for (const [name, source] of Object.entries(files)) {
  const markdown = source.replace(/^---\r?\n[\s\S]*?\r?\n---(?=\r?\n|$)/, value => value.replace(/[^\n]/g, ' '));
  const tokens = Lexer.lex(markdown, {gfm:true, breaks:false});
  const out = {headings:[], links:[], code:[], html:[], tables:[], definitions:[]};
  const positions = new Map();
  const location = raw => {
    const from = positions.get(raw) || 0;
    let start = source.indexOf(raw, from);
    if (start < 0) start = source.indexOf(raw);
    if (start < 0) return {start:-1, end:-1, line:1};
    positions.set(raw, start + raw.length);
    return {start:[...source.slice(0,start)].length, end:[...source.slice(0,start+raw.length)].length, line:source.slice(0,start).split('\n').length};
  };
  walkTokens(tokens, t => {
    if (t.type === 'heading') out.headings.push({text:plain(t.tokens), raw:t.raw, ...location(t.raw)});
    if ((t.type === 'link' || t.type === 'image') && !/^\[\^[^\]]+\]/.test(t.raw)) out.links.push({href:t.href, raw:t.raw, ...location(t.raw)});
    if (t.type === 'code') out.code.push({text:t.text, raw:t.raw, ...location(t.raw)});
    if (t.type === 'html') out.html.push({raw:t.raw, ...location(t.raw)});
    if (t.type === 'table') out.tables.push({raw:t.raw, headers:t.header.map(x=>plain(x.tokens)), ...location(t.raw)});
  });
  for (const [label, value] of Object.entries(tokens.links || {})) {
    // marked also recognizes [^n]: prose as a link definition; footnotes are handled separately.
    if (!label.startsWith('^')) out.definitions.push({label, href:value.href});
  }
  result[name] = out;
}
process.stdout.write(JSON.stringify(result));
'''


@dataclass
class Finding:
    kind: str
    path: str
    line: int
    message: str
    match: str = ""


@dataclass
class Audit:
    findings: list[Finding] = field(default_factory=list)
    inventory: list[dict] = field(default_factory=list)
    exemptions: list[dict] = field(default_factory=list)
    counters: Counter = field(default_factory=Counter)
    base: str | None = None
    review_candidates: list[dict] = field(default_factory=list)

    def add(self, kind: str, path: str, line: int, message: str, match: str = "") -> None:
        self.findings.append(Finding(kind, path, line, message, match))

    def data(self) -> dict:
        return {
            "schema_version": 1,
            "base": self.base,
            "scope": "All Markdown links; mutable prose only for language rules. Explicit literal examples, commands and immutable evidence are reported separately.",
            "counts": dict(sorted(self.counters.items())),
            "finding_counts": dict(sorted(Counter(x.kind for x in self.findings).items())),
            "findings": [asdict(x) for x in self.findings],
            "inventory": self.inventory,
            "exemptions": self.exemptions,
            "review_candidates": self.review_candidates,
        }


def discover(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*.md")
                  if not any(part in IGNORED_DIRECTORIES for part in p.relative_to(root).parts))


def immutable_reason(relative: str) -> str | None:
    path = Path(relative)
    if relative.startswith("evaluations/runs/"):
        return "immutable evaluation inputs, outputs, reviews or skill snapshots"
    if relative.startswith("scripts/vendor/"):
        return "third-party source documentation"
    if any(part.lower() in {"archive", "archives"} for part in path.parts[:-1]):
        return "explicit archive directory"
    if re.fullmatch(r"docs/examples/(?:0[1-9]|1[0-4])_[^/]+\.md", relative):
        return "byte-identical published historical evaluation output"
    return None


def parse_markdown(texts: dict[str, str], parser_root: Path = ROOT) -> dict:
    if not texts:
        return {}
    module = parser_root / "scripts/vendor/marked/marked.esm.mjs"
    if not module.is_file():
        raise ValueError(f"Vendored Markdown parser is missing: {module}")
    # marked normalizes CRLF/CR. Keep untouched strings for byte verification,
    # and map parser offsets back to their positions in those original strings.
    normalized = {name: text.replace("\r\n", "\n").replace("\r", "\n") for name,text in texts.items()}
    result = subprocess.run(
        ["node", "--input-type=module", "--eval", PARSER, module.as_uri()],
        input=json.dumps(normalized, ensure_ascii=False), capture_output=True, text=True,
        encoding="utf-8", timeout=120, check=False,
    )
    if result.returncode:
        raise ValueError(f"Markdown parser failed: {result.stderr.strip()}")
    parsed = json.loads(result.stdout)
    for name, text in texts.items():
        if "\r" not in text:
            continue
        offsets = []
        index = 0
        while index < len(text):
            offsets.append(index)
            index += 2 if text[index:index+2] == "\r\n" else 1
        offsets.append(len(text))
        for kind in ("headings", "links", "code", "html", "tables"):
            for item in parsed[name][kind]:
                if item["start"] >= 0:
                    item["start"], item["end"] = offsets[item["start"]], offsets[item["end"]]
    return parsed


def mask_span(text: str, start: int, end: int) -> str:
    return text[:start] + re.sub(r"[^\n]", " ", text[start:end]) + text[end:]


def line_at(text: str, offset: int) -> int:
    return text.count("\n", 0, max(offset, 0)) + 1


def block_lines(text: str, item: dict, claimed=()) -> list[tuple[int, int, str]]:
    """Map lexer block lines to original offsets, including list/quote prefixes."""
    if item["start"] >= 0:
        offset = item["start"]
        lines = []
        for line in text[item["start"]:item["end"]].splitlines(keepends=True):
            lines.append((offset, offset, line))
            offset += len(line)
        return lines
    wanted = item["raw"].rstrip("\n").splitlines()
    physical = text.splitlines(keepends=True)
    offsets = []
    offset = 0
    for line in physical:
        offsets.append(offset)
        offset += len(line)
    for first in range(len(physical)-len(wanted)+1):
        if any(a <= offsets[first] < b for a,b in claimed):
            continue
        mapped = []
        for index, expected in enumerate(wanted):
            line = physical[first+index]
            actual = line.rstrip("\r\n")
            content = expected.lstrip()
            if content:
                if not actual.endswith(content):
                    break
                prefix = actual[:-len(content)]
            else:
                prefix = actual
            if not CONTAINER_PREFIX.fullmatch(prefix):
                break
            start = offsets[first+index]
            mapped.append((start, start+len(prefix), line[len(prefix):]))
        else:
            if mapped:
                return mapped
    return []


def block_spans(text: str, items: list[dict]) -> list[tuple[int, int]]:
    spans = []
    for item in items:
        mapped = block_lines(text, item, spans)
        if mapped:
            start = mapped[0][0]
            end = mapped[-1][1]+len(mapped[-1][2])
            spans.append((start,end))
    return spans


def code_spans(text: str, parsed: dict) -> list[tuple[int, int]]:
    return block_spans(text, parsed.get("code", []))


class HtmlReferences(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attributes: list[tuple[str, str | None]]) -> None:
        for key, value in attributes:
            if value is None:
                continue
            if key == "id" or (tag == "a" and key == "name"):
                self.ids.append(value)
            if key in {"href", "src"}:
                self.links.append(value)


def github_slug(text: str) -> str:
    # GFM heading text is already parsed by marked. GitHub removes punctuation,
    # keeps underscores/hyphens, and replaces each space (not each run) with '-'.
    text = html.unescape(re.sub(r"<[^>]*>", "", text)).lower()
    text = "".join(c for c in text if c in " _-" or unicodedata.category(c)[0] in "LNM")
    return text.replace(" ", "-")


def anchors(parsed: dict) -> set[str]:
    seen: set[str] = set()
    headings: set[str] = set()
    for heading in parsed.get("headings", []):
        base = github_slug(heading["text"])
        value = base
        suffix = 0
        while value in seen:
            suffix += 1
            value = f"{base}-{suffix}"
        seen.add(value)
        headings.add(value)
    for raw in parsed.get("html", []):
        parser = HtmlReferences()
        parser.feed(raw["raw"])
        headings.update(parser.ids)
    return headings


def normal_reference(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip()).casefold()


def frozen_reference_verified(root: Path, relative: str, text: str, destination: str,
                              all_anchors: dict[str, set[str]]) -> bool:
    """Recognize one existing broken copied link without concealing its status."""
    known = FROZEN_REFERENCE
    if relative != known["path"] or destination != known["destination"]:
        return False
    if hashlib.sha256(text.encode()).hexdigest() != known["sha256"] or known["quote"] not in text.splitlines():
        return False
    source = root / known["source"]
    if not source.is_file():
        return False
    raw = source.read_bytes()
    return (hashlib.sha256(raw).hexdigest() == known["source_sha256"]
            and known["quote"].removeprefix("> ") in raw.decode("utf-8")
            and known["destination"].removeprefix("#") in all_anchors.get(known["source"], set()))


def local_links(root: Path, relative: str, text: str, parsed: dict,
                all_anchors: dict[str, set[str]], report: Audit) -> None:
    links = [(item["href"], item["line"]) for item in parsed.get("links", [])]
    links += [(item["href"], 1) for item in parsed.get("definitions", [])]
    for item in parsed.get("html", []):
        parser = HtmlReferences()
        parser.feed(item["raw"])
        links.extend((href, item["line"]) for href in parser.links)
    for destination, line in links:
        destination = html.unescape(destination)
        try:
            parts = urlsplit(destination)
        except ValueError:
            report.add("link", relative, line, "Invalid link destination", destination)
            continue
        if parts.scheme or parts.netloc:
            continue
        report.counters["local_links_checked"] += 1
        decoded = unquote(parts.path)
        if "\\" in decoded:
            report.add("link", relative, line, "Use a portable local path", destination)
            continue
        target = (root / relative).parent / decoded if decoded else root / relative
        if decoded.startswith("/"):
            target = root / decoded.lstrip("/")
        target = target.resolve()
        try:
            target_relative = target.relative_to(root.resolve()).as_posix()
        except ValueError:
            report.add("link", relative, line, "Local link escapes the repository", destination)
            continue
        if not target.exists():
            report.add("link", relative, line, "Local target does not exist", destination)
            continue
        if not parts.fragment:
            continue
        report.counters["fragment_links_checked"] += 1
        fragment = unquote(parts.fragment)
        ids = all_anchors.get(target_relative)
        if ids is None and target.is_file() and target.suffix.lower() in {".html", ".htm"}:
            parser = HtmlReferences()
            parser.feed(target.read_text(encoding="utf-8"))
            ids = set(parser.ids)
        if ids is not None:
            if fragment not in ids:
                if frozen_reference_verified(root, relative, text, destination, all_anchors):
                    report.add("archived_reference", relative, line,
                               "Pre-existing copied fragment remains broken in the frozen review; the exact quote and destination were verified in its original source",
                               destination)
                    report.counters["preserved_broken_copy_references"] += 1
                else:
                    report.add("anchor", relative, line, "Fragment is not a heading or explicit anchor in target", destination)
        elif re.fullmatch(r"L\d+(?:-L\d+)?", fragment) and target.is_file():
            numbers = [int(n) for n in re.findall(r"\d+", fragment)]
            count = len(target.read_text(encoding="utf-8").splitlines())
            if min(numbers) < 1 or max(numbers) > count or numbers != sorted(numbers):
                report.add("anchor", relative, line, "Source line anchor is outside target", destination)
        else:
            report.add("anchor", relative, line, "Cannot resolve a fragment on this local target", destination)
    visible = text
    for start, end in code_spans(text, parsed):
        visible = mask_span(visible, start, end)
    # The parser already resolves valid reference links, including escaped
    # labels. Only unresolved visible syntax needs a secondary diagnostic pass.
    for item in parsed.get("links", []):
        for match in re.finditer(re.escape(item["raw"]), visible):
            visible = mask_span(visible, *match.span())
    for match in INLINE_CODE.finditer(visible):
        visible = mask_span(visible, *match.span())
    # Comments and raw HTML blocks (notably <pre>) contain literal examples,
    # not unresolved Markdown references. Real HTML href/src were checked above.
    for start,end in block_spans(text, parsed.get("html", [])):
        visible = mask_span(visible,start,end)
    definitions = {normal_reference(x["label"]) for x in parsed.get("definitions", [])}
    for match in REFERENCE_USE.finditer(visible):
        first, second = match.groups()
        label = second or first
        if normal_reference(label or "") not in definitions:
            report.add("link", relative, line_at(text, match.start()), "Undefined explicit reference label", label or "")
    footnotes = set(re.findall(r"^ {0,3}\[\^([^\]\n]+)\]:", visible, re.M))
    for match in re.finditer(r"\[\^([^\]\n]+)\](?!:)", visible):
        if match.group(1) not in footnotes:
            report.add("anchor", relative, line_at(text, match.start()), "Undefined footnote reference", match.group(1))


def source_regions(root: Path, relative: str, text: str, report: Audit, ignored=()) -> list[tuple[int, int]]:
    spans = []
    cursor = 0
    for start in SOURCE_START.finditer(text):
        if any(a <= start.start() < b for a,b in ignored):
            continue
        if start.start() < cursor:
            report.add("exemption", relative, line_at(text, start.start()), "Nested source marker")
            continue
        end = text.find(SOURCE_END, start.end())
        if end < 0:
            report.add("exemption", relative, line_at(text, start.start()), "Unclosed source marker")
            continue
        source, digest = start.groups()
        target = (root / source).resolve()
        try:
            target.relative_to(root.resolve())
            raw = target.read_bytes()
        except (OSError, ValueError):
            report.add("integrity", relative, line_at(text, start.start()), "Source marker target is absent or outside repository", source)
            raw = None
        following = text[start.end():]
        content_start = start.end() + (2 if following.startswith("\r\n") else 1 if following.startswith(("\n","\r")) else 0)
        content = text[content_start:end]
        if raw is not None and (hashlib.sha256(raw).hexdigest() != digest or content.encode("utf-8") != raw):
            report.add("integrity", relative, line_at(text, start.start()), "Source copy differs from its recorded bytes or SHA-256", source)
        spans.append((start.start(), end + len(SOURCE_END)))
        report.exemptions.append({"path":relative,"kind":"source_copy","line":line_at(text,start.start()),
                                  "end_line":line_at(text,end),"reason":source,"sha256":digest})
        report.counters["source_copy_regions"] += 1
        cursor = end + len(SOURCE_END)
    end_count = sum(not any(a <= match.start() < b for a,b in ignored) for match in re.finditer(re.escape(SOURCE_END),text))
    if end_count != len(spans):
        report.add("exemption", relative, 1, "Unmatched source end marker")
    return spans


def example_regions(relative: str, text: str, report: Audit, ignored=()) -> list[tuple[int, int]]:
    spans = []
    active = None
    markers = sorted([(m.start(), "start", m) for m in EXAMPLE_START.finditer(text)] +
                     [(m.start(), "end", m) for m in EXAMPLE_END.finditer(text)])
    for offset, kind, match in markers:
        if any(a <= offset < b for a,b in ignored):
            continue
        if kind == "start":
            if active is not None:
                report.add("exemption", relative, line_at(text, offset), "Example regions must not nest")
            else:
                active = match
        elif active is None:
            report.add("exemption", relative, line_at(text, offset), "Unmatched example end marker")
        else:
            spans.append((active.start(), match.end()))
            report.exemptions.append({"path":relative,"kind":"literal_example","line":line_at(text,active.start()),
                                      "end_line":line_at(text,match.end()),"reason":active.group(1)})
            report.counters["literal_example_regions"] += 1
            active = None
    if active is not None:
        report.add("exemption", relative, line_at(text, active.start()), "Unclosed example region")
    # Malformed starts cannot silently disable validation.
    declared_starts = [m for m in re.finditer(r"<!--\s*lint:example-start",text) if not any(a <= m.start() < b for a,b in ignored)]
    valid_starts = [m for m in EXAMPLE_START.finditer(text) if not any(a <= m.start() < b for a,b in ignored)]
    if len(declared_starts) != len(valid_starts):
        report.add("exemption", relative, 1, "Example start marker requires a nonempty reason")
    return spans


def table_cell_spans(line: str) -> list[tuple[int, int]]:
    separators = []
    ticks = 0
    i = 0
    while i < len(line):
        if line[i] == "\\":
            i += 2
            continue
        if line[i] == "`":
            j = i
            while j < len(line) and line[j] == "`": j += 1
            run = j - i
            if ticks == 0: ticks = run
            elif ticks == run: ticks = 0
            i = j
            continue
        if line[i] == "|" and not ticks:
            separators.append(i)
        i += 1
    edges = [-1, *separators, len(line)]
    spans = [(a + 1, b) for a, b in zip(edges, edges[1:])]
    if spans and not line[spans[0][0]:spans[0][1]].strip(): spans.pop(0)
    if spans and not line[spans[-1][0]:spans[-1][1]].strip(): spans.pop()
    return spans


def prose_text(root: Path, relative: str, text: str, parsed: dict, report: Audit,
               diagnostic_patterns: list[tuple[str, re.Pattern]]) -> str:
    visible = text
    code = code_spans(text, parsed)
    spans = source_regions(root, relative, text, report, code) + example_regions(relative, text, report, code)
    for start, end in spans + code:
        visible = mask_span(visible, start, end)
    claimed_tables = []
    for table in parsed.get("tables", []):
        exempt = [i for i, label in enumerate(table["headers"]) if html.unescape(label).strip() in BEFORE_COLUMNS]
        if not exempt:
            continue
        mapped = block_lines(text, table, claimed_tables)
        if mapped:
            claimed_tables.append((mapped[0][0], mapped[-1][1]+len(mapped[-1][2])))
        for index, (line_start, position, line) in enumerate(mapped):
            if index >= 2:
                cells = table_cell_spans(line.rstrip("\r\n"))
                for column in exempt:
                    if column < len(cells):
                        start, end = cells[column]
                        visible = mask_span(visible, position+start, position+end)
                        report.counters["literal_before_cells"] += 1
                        report.exemptions.append({"path":relative,"kind":"before_cell","line":line_at(text,position),
                                                  "column":column+1,"reason":table["headers"][column]})
    # Genuine code identifiers are protected; merely wrapping Korean prose or
    # known compression/session phrases in backticks must not hide a finding.
    for match in list(INLINE_CODE.finditer(visible)):
        content = match.group(2)
        technical = is_technical_literal(content)
        diagnostic = any(pattern.search(content) for rule, pattern in diagnostic_patterns if rule != "DEV-E01")
        if technical and not diagnostic:
            visible = mask_span(visible, *match.span())
    # Link destinations/HTML attributes are not prose; preserve visible labels.
    visible = re.sub(r"\]\((?:<[^>\n]*>|[^\n]*?)\)", lambda m: "]"+" "*(len(m.group(0))-1), visible)
    visible = re.sub(r"^ {0,3}\[(?!\^)[^\]\n]+\]:[^\n]*", lambda m:" "*len(m.group(0)), visible, flags=re.M)
    visible = re.sub(r"<!--.*?-->", lambda m:re.sub(r"[^\n]"," ",m.group(0)), visible, flags=re.S)
    visible = re.sub(r"<[^>\n]+>", lambda m:" "*len(m.group(0)), visible)
    # Common emphasis and inline-code delimiters must not interrupt a phrase
    # detector. Real code identifiers were masked above; snake_case stays intact.
    visible = re.sub(r"`+", "", visible)
    visible = re.sub(r"(?<![\w\\])[_*~]{1,3}(?=\S)|(?<=\S)[_*~]{1,3}(?!\w)", "", visible)
    return visible


def load_rules(root: Path, report: Audit, required: bool = True) -> tuple[dict, list[tuple[str, re.Pattern]]]:
    path = root / RULE_PATH
    if not path.is_file():
        if required:
            report.add("mapping", RULE_PATH, 1, "Canonical development rule file is missing")
        return {}, [("DEV-E01", re.compile(PLAIN_ENDING))]
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        report.add("mapping", RULE_PATH, 1, f"Cannot read rule configuration: {error}")
        return {}, []
    declared = config.get("rule_ids", [])
    ids = [rule.get("id") for rule in config.get("rules", [])]
    if declared != list(REQUIRED_RULE_IDS) or set(ids) != set(REQUIRED_RULE_IDS) or len(ids) != len(set(ids)):
        report.add("mapping", RULE_PATH, 1, "Canonical rule IDs must match all eight required IDs exactly")
    patterns = []
    for rule in config.get("rules", []):
        if not all(isinstance(rule.get(key), str) and rule[key].strip() for key in ("title", "checklist", "context")):
            report.add("mapping", RULE_PATH, 1, "Every rule needs a title, checklist and context", str(rule.get("id")))
        if not isinstance(rule.get("patterns"), list) or not rule["patterns"]:
            report.add("mapping", RULE_PATH, 1, "Every rule needs explicit detection patterns", str(rule.get("id")))
        for expression in rule.get("patterns", []):
            try:
                patterns.append((rule["id"], re.compile(expression)))
            except (TypeError, re.error) as error:
                report.add("mapping", RULE_PATH, 1, f"Invalid rule regular expression: {error}", str(rule.get("id")))
    ending = [pattern.pattern for rule, pattern in patterns if rule == "DEV-E01"]
    if PLAIN_ENDING not in ending:
        report.add("mapping", RULE_PATH, 1, "DEV-E01 must include the requested exact ending expression")
    for relative in RULE_DOCS:
        file = root / relative
        if not file.is_file():
            report.add("mapping", relative, 1, "Rule mapping document is missing")
            continue
        raw = file.read_text(encoding="utf-8")
        actual = set(re.findall(r"\bDEV-[ACES]\d{2}\b", raw))
        if actual != set(REQUIRED_RULE_IDS):
            report.add("mapping", relative, 1, "Rule/checklist IDs are missing or inconsistent", ", ".join(sorted(set(REQUIRED_RULE_IDS)^actual)))
    for token in ("v1", "sha256", "fwrun6", "rcfield4"):
        if token not in config.get("protected_token_examples", []):
            report.add("mapping", RULE_PATH, 1, "Required protected token example is absent", token)
    coinages = config.get("translation_coinages", [])
    expected_coinages = {f"DEV-A01-{index:02d}" for index in range(1, 15)}
    if len(coinages) != 14 or {item.get("id") for item in coinages} != expected_coinages:
        report.add("mapping", RULE_PATH, 1, "All fourteen distinct translation dictionary entries are required")
    coinage_patterns = [pattern for rule, pattern in patterns if rule == "DEV-A01"]
    for item in coinages:
        if not item.get("before") or not item.get("after") or not item.get("context") or not item.get("preserve"):
            report.add("mapping", RULE_PATH, 1, "Dictionary entries need before/after, context and preservation guidance", str(item.get("id")))
        for before in item.get("before", []):
            if not any(pattern.search(before) for pattern in coinage_patterns):
                report.add("mapping", RULE_PATH, 1, "A dictionary spelling is absent from the detection patterns", before)
    spacing = config.get("spacing_patterns", [])
    if len(spacing) != 4 or {item.get("id") for item in spacing} != {f"DEV-S01-{index:02d}" for index in range(1, 5)}:
        report.add("mapping", RULE_PATH, 1, "All four spacing pattern entries are required")
    if {item.get("pattern") for item in spacing} != {pattern.pattern for rule, pattern in patterns if rule == "DEV-S01"}:
        report.add("mapping", RULE_PATH, 1, "Spacing entry expressions and the DEV-S01 checklist expressions diverged")
    for item in spacing:
        try:
            matcher = re.compile(item.get("pattern", ""))
        except (TypeError, re.error):
            continue  # The corresponding main rule already reports invalid regexes.
        for example in item.get("examples", []):
            if not matcher.search(example.get("before", "")) or matcher.search(example.get("after", "")):
                report.add("mapping", RULE_PATH, 1, "Spacing example does not agree with its detector", str(item.get("id")))
    # This is coverage of the listed user regressions, not a claim that regexes
    # establish semantic equivalence or detect every possible bad sentence.
    samples = {
        "DEV-A01": ["자동반입", "자격 반입", "반입 스크립트", "보호저장", "영속화", "영속 저장", "영속 볼륨", "권위 입력", "권위 있는 출처", "권위 있는 조회값", "적격 후보", "적격 소프트웨어", "음성 검증", "음성 런타임 시험", "단조·멱등", "생존 워커", "워커 생존", "회로가 열리면", "회로 열림", "고아 파일", "고아 임시 데이터", "카디널리티", "명시화되다", "비편집 설치", "수명주기"],
        "DEV-S01": ["행19", "자산100", "POST200", "GET401", "종료0", "exit0", "총5건", "문맥6개", "최근100", "시도1회", "사용자별관리"],
    }
    for rule_id, values in samples.items():
        matchers = [pattern for rule, pattern in patterns if rule == rule_id]
        for sample in values:
            if not any(p.search(sample) for p in matchers):
                report.add("mapping", RULE_PATH, 1, "Required regression expression is not detected", f"{rule_id}: {sample}")
    for token in ("v1", "sha256", "fwrun6", "rcfield4"):
        if any(p.search(token) for rule, p in patterns if rule == "DEV-S01"):
            report.add("mapping", RULE_PATH, 1, "Spacing expression incorrectly matches a protected identifier", token)
    return config, patterns


def baseline_texts(root: Path, base: str) -> dict[str, str]:
    result = subprocess.run(["git","ls-tree","-r","--name-only",base], cwd=root, capture_output=True, text=True, check=False)
    if result.returncode:
        raise ValueError("Cannot read preservation base; fetch its commit or use --base with a locally available revision")
    paths = [line for line in result.stdout.splitlines() if line.endswith(".md")]
    values = {}
    for relative in paths:
        data = subprocess.check_output(["git","show",f"{base}:{relative}"], cwd=root)
        values[relative] = data.decode("utf-8")
    return values


def technical_literals(text: str) -> set[str]:
    values = {m.group(2) for m in INLINE_CODE.finditer(text)
              if is_technical_literal(m.group(2))}
    values.update(BARE_ENV.findall(text))
    values.update(BARE_OPTION.findall(text))
    return values


def is_technical_literal(content: str) -> bool:
    if not content.strip():
        return False
    if TECHNICAL.fullmatch(content):
        return True
    # Command names remain ASCII while their arguments or filenames can be
    # Korean. Ordinary Korean examples and dictionary headwords do not match.
    if COMMAND_WITH_ARGUMENTS.fullmatch(content):
        return True
    if content.startswith(("/", "./", "../")):
        return True
    return bool(re.match(r"^[A-Z][A-Z0-9_]*=", content))


def preservation(current: dict[str,str], old: dict[str,str], parsed: dict, old_parsed: dict, report: Audit) -> None:
    def codes(document):
        return Counter(item["text"] for item in document.get("code", []))

    # A moved literal must be newly present in an explicitly designated evidence
    # destination; an unrelated old archive cannot conceal its loss from a guide.
    moves = {"code": Counter(), "inline": Counter(), "number": Counter()}
    for destination, text in current.items():
        if destination.startswith("docs/evidence/") or Path(destination).name == "work_history.md":
            previous = old.get(destination, "")
            moves["code"].update(codes(parsed[destination])-codes(old_parsed.get(destination, {})))
            moves["inline"].update(Counter(technical_literals(text))-Counter(technical_literals(previous)))
            moves["number"].update(Counter(NUMBER.findall(text))-Counter(NUMBER.findall(previous)))

    for relative, old_text in old.items():
        if relative not in current:
            report.add("integrity", relative, 1, "Existing Markdown file was removed; preserve its path/anchors or provide an explicit migration")
            continue
        text = current[relative]
        if immutable_reason(relative) and old_text != text:
            report.add("integrity", relative, 1, "Immutable historical/third-party Markdown changed")
        missing = anchors(old_parsed[relative]) - anchors(parsed[relative])
        for anchor in sorted(missing):
            report.add("legacy_anchor", relative, 1, "Existing heading anchor disappeared; retain an explicit alias", anchor)
        for kind, missing_values in (
            ("code", codes(old_parsed[relative])-codes(parsed[relative])),
            ("inline", Counter(technical_literals(old_text))-Counter(technical_literals(text))),
            ("number", Counter(NUMBER.findall(old_text))-Counter(NUMBER.findall(text))),
        ):
            for value, count in missing_values.items():
                moved = min(count, moves[kind][value])
                moves[kind][value] -= moved
                if moved:
                    report.counters["protected_literals_moved_to_evidence"] += moved
                if count > moved:
                    report.add("integrity", relative, 1,
                               f"Protected {kind} literal changed or disappeared ({count-moved} occurrence(s))", value[:200])
    # Marked historical excerpts must quote the existing file, not introduce an
    # unrestricted escape hatch for newly written prose.
    for relative, text in current.items():
        previous = old.get(relative, "")
        for start in EXAMPLE_START.finditer(text):
            end = EXAMPLE_END.search(text, start.end())
            if not end:
                continue
            reason = start.group(1)
            if re.search(r"(?:원문|인용|보존|기록|historical|source)", reason, re.I):
                excerpt = text[start.end():end.start()].strip("\n")
                if previous and excerpt not in previous:
                    report.add("integrity", relative, line_at(text,start.start()), "Historical example region is not an unchanged excerpt of this file's baseline", reason)
    report.counters["baseline_markdown_files"] = len(old)
    report.counters["protected_code_blocks"] = sum(len(value.get("code", [])) for value in old_parsed.values())
    report.counters["legacy_anchors_checked"] = sum(len(anchors(x)) for x in old_parsed.values())


def audit(root: Path, *, base: str | None = BASE, require_rules: bool = True, parser_root: Path = ROOT) -> Audit:
    root = root.resolve()
    report = Audit(base=base)
    files = discover(root)
    current = {p.relative_to(root).as_posix():p.read_bytes().decode("utf-8") for p in files}
    old = baseline_texts(root, base) if base else {}
    combined = dict(current)
    combined.update({"@base/"+key:value for key,value in old.items()})
    result = parse_markdown(combined, parser_root)
    parsed = {key:result[key] for key in current}
    old_parsed = {key:result["@base/"+key] for key in old}
    all_anchors = {key:anchors(value) for key,value in parsed.items()}
    config, patterns = load_rules(root, report, require_rules)
    for relative, text in current.items():
        parsed_file = parsed[relative]
        reason = immutable_reason(relative)
        report.counters["markdown_files"] += 1
        local_links(root, relative, text, parsed_file, all_anchors, report)
        report.inventory.append({"path":relative,"sha256":hashlib.sha256(text.encode()).hexdigest(),
                                 "role":"immutable" if reason else "mutable","reason":reason,
                                 "lines":len(text.splitlines()),"headings":len(parsed_file.get("headings",[]))})
        for rule_id, pattern in patterns:
            report.counters["raw_pattern_matches"] += len(list(pattern.finditer(text)))
        if reason:
            report.counters["immutable_markdown_files"] += 1
            continue
        report.counters["mutable_markdown_files"] += 1
        visible = prose_text(root, relative, text, parsed_file, report, patterns)
        seen = set()
        for rule_id, pattern in patterns:
            # C01 is deliberately a document-role review candidate, not an
            # automatic ban on dates, paths or historical evidence in reports.
            if rule_id == "DEV-C01":
                for candidate in pattern.finditer(visible):
                    report.counters["history_review_candidates"] += 1
                    report.review_candidates.append({"kind":rule_id,"path":relative,"line":line_at(visible,candidate.start()),"match":candidate.group(0)})
                continue
            for match in pattern.finditer(visible):
                key = (rule_id, match.start(), match.end())
                if key in seen: continue
                seen.add(key)
                report.add(rule_id, relative, line_at(visible,match.start()), "Review this mutable prose against the mapped rule", match.group(0))
        report.counters["mutable_prose_lines"] += sum(bool(line.strip()) for line in visible.splitlines())
    if old:
        preservation(current, old, parsed, old_parsed, report)
    report.counters["findings"] = len(report.findings)
    report.counters["active_findings"] = sum(f.kind != "archived_reference" for f in report.findings)
    report.counters["active_broken_links"] = sum(f.kind in {"link", "anchor"} for f in report.findings)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--base", default=BASE, help="Preservation revision; use 'none' only for independent fixtures")
    parser.add_argument("--json", type=Path, help="Write complete per-file inventory, exemptions and findings")
    parser.add_argument("--limit", type=int, default=40, help="Maximum findings printed; JSON always contains all findings")
    args = parser.parse_args(argv)
    try:
        report = audit(args.root, base=None if args.base == "none" else args.base)
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(f"Markdown audit could not complete: {error}", file=sys.stderr)
        return 2
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report.data(),ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"counts":dict(report.counters),"finding_counts":dict(Counter(x.kind for x in report.findings))},ensure_ascii=False))
    for finding in report.findings[:max(0,args.limit)]:
        print(f"{finding.path}:{finding.line}: {finding.kind}: {finding.message}: {finding.match}")
    if len(report.findings)>args.limit:
        print(f"{len(report.findings)-args.limit} additional findings; use --json for the complete list.")
    return 1 if report.counters["active_findings"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
