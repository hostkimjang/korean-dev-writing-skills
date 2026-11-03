#!/usr/bin/env python3
"""Validate this repository with Python's standard library only.

This is a deliberately limited structural checker, not a Markdown/YAML parser
or a writing-quality grader. The supported frontmatter is exactly two keys:
name and description, with single-line strings or an indented | / > description.
It checks the three required interface strings in the simple agents YAML.

Markdown scope: SKILL.md, allowlisted reference Markdown, README.md, docs/**/*.md, and
evaluations/protocol.md. Historical baselines and evaluation outputs are not
reformatted or linted. Fences at 0–3 spaces of indentation are checked; quoted
or list-nested fences, HTML, heading anchors, and shortcut reference links are
outside the scope. A md/markdown fence is recursively checked as a template.
Its outer fence must be longer than any same-character fence inside it (for
example, four backticks around a template containing three-backtick blocks).
ATX headings must be followed by a blank line. Ordinary single-line inline
links and reference definitions are checked for local path existence; external
URLs are not fetched. Use angle brackets around link paths containing spaces.
Nested bracket labels, escaped delimiters, and bare destinations containing
parentheses are not parsed. This is not a substitute for rendered review.

JSON checks validate structure, ID references, and scoring metadata only. They
do not run a model, score prose, count style words, or judge factual accuracy.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import unquote, urlsplit


SKILL_NAME = "korean-dev-writing"
SKILL_RELATIVE_PATH = Path("skills") / SKILL_NAME
# This exact allowlist is also imported by package.py. Adding a resource is a
# deliberate release change: add its path here as well as linking it in SKILL.md.
PACKAGE_FILES = (
    "LICENSE",
    "SKILL.md",
    "agents/openai.yaml",
    "references/before-after-guide.md",
    "references/document-types.md",
    "references/reading-flow.md",
)
CASE_FILES = (
    "01_cli_readme.json",
    "02_event_architecture.json",
    "03_investigation_pr.json",
    "04_incident_runbook.json",
    "05_storage_adr.json",
    "06_paragraph_edit.json",
)
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
HEADING = re.compile(r"^ {0,3}#{1,6}(?:[ \t]+\S|[ \t]*$)")
INLINE_CODE = re.compile(r"(`+)(.+?)\1")
# Intentionally limited to ordinary single-line links. Nested bracket labels,
# escaped delimiters, and parenthesized bare destinations are not parsed.
INLINE_LINK = re.compile(
    r"!?\[[^\]\n]*\]\(\s*(<[^>\n]+>|[^\s()]+)"
    r"(?:[ \t]+(?:\"[^\"\n]*\"|'[^'\n]*'))?[ \t]*\)"
)
LINK_DEFINITION = re.compile(r"^ {0,3}\[([^\]]+)\]:\s*(<[^>\n]+>|\S+)")
REFERENCE_LINK = re.compile(r"!?\[([^\]\n]*)\]\[([^\]\n]*)\]")


@dataclass
class Report:
    root: Path
    errors: list[str] = field(default_factory=list)
    markdown_count: int = 0
    case_count: int = 0

    def error(self, path: Path, message: str, line: int | None = None) -> None:
        try:
            name = path.relative_to(self.root).as_posix()
        except ValueError:
            name = str(path)
        suffix = f":{line}" if line else ""
        self.errors.append(f"{name}{suffix}: {message}")


def read_text(path: Path, report: Report) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        report.error(path, f"cannot read UTF-8 file: {exc}")
        return None


def scalar(value: str) -> str:
    """Read only the documented single-line YAML string subset."""
    value = value.strip()
    if not value:
        raise ValueError("empty string")
    if value.startswith('"'):
        decoded = json.loads(value)
        if not isinstance(decoded, str):
            raise ValueError("expected a quoted string")
        return decoded
    if value.startswith("'"):
        if len(value) < 2 or not value.endswith("'"):
            raise ValueError("unclosed single-quoted string")
        body = value[1:-1]
        if "'" in body.replace("''", ""):
            raise ValueError("single quotes inside a string must be doubled")
        return body.replace("''", "'")
    if value[0] in "[{}]&*!|>@`" or ": " in value or " #" in value:
        raise ValueError("quote this value; advanced YAML syntax is unsupported")
    if value.lower() in {"null", "true", "false", "~"}:
        raise ValueError("expected a string, not a YAML scalar literal")
    return value


def check_frontmatter(path: Path, text: str, report: Report) -> None:
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        report.error(path, "frontmatter must begin with --- on the first line")
        return
    try:
        end = lines.index("---", 1)
    except ValueError:
        report.error(path, "frontmatter is not closed")
        return
    values: dict[str, str] = {}
    index = 1
    while index < end:
        line = lines[index]
        if not line.strip() or line.startswith("#"):
            index += 1
            continue
        match = re.fullmatch(r"(name|description):[ \t]*(.*)", line)
        if not match:
            report.error(path, "only name and description are supported in frontmatter", index + 1)
            index += 1
            continue
        key, raw = match.groups()
        if key in values:
            report.error(path, f"duplicate frontmatter key: {key}", index + 1)
        start = index + 1
        index += 1
        try:
            if raw in {"|", "|-", "|+", ">", ">-", ">+"}:
                if key != "description":
                    raise ValueError("name must be a single-line string")
                block: list[str] = []
                while index < end and (not lines[index].strip() or lines[index].startswith("  ")):
                    block.append(lines[index][2:] if lines[index].strip() else "")
                    index += 1
                value = ("\n" if raw.startswith("|") else " ").join(block).strip()
            else:
                value = scalar(raw)
            if not value.strip():
                raise ValueError("value must not be empty")
            values[key] = value
        except (ValueError, json.JSONDecodeError) as exc:
            report.error(path, f"invalid {key}: {exc}", start)
    for key in ("name", "description"):
        if key not in values:
            report.error(path, f"missing valid frontmatter field: {key}")
    name = values.get("name", "")
    if name and (name != SKILL_NAME or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 64):
        report.error(path, f"name must be {SKILL_NAME!r}")
    if len(values.get("description", "")) > 1024:
        report.error(path, "description must contain 1–1024 characters")
    if not any(line.strip() for line in lines[end + 1 :]):
        report.error(path, "SKILL.md body is empty")


def check_agent_metadata(path: Path, text: str, report: Report) -> None:
    # This checks the required interface scalar fields, not arbitrary YAML.
    lines = text.splitlines()
    interface_positions = [i for i, line in enumerate(lines) if line == "interface:"]
    if len(interface_positions) != 1:
        report.error(path, "expected one interface: mapping")
        return
    fields: dict[str, str] = {}
    for i in range(interface_positions[0] + 1, len(lines)):
        line = lines[i]
        if line and not line.startswith(" ") and not line.startswith("#"):
            break
        match = re.fullmatch(r"  ([a-z_]+):[ \t]*(.*)", line)
        if not match:
            if line.strip() and not line.lstrip().startswith("#"):
                report.error(path, "use two-space indentation and single-line interface strings", i + 1)
            continue
        key, raw = match.groups()
        if key in fields:
            report.error(path, f"duplicate interface key: {key}", i + 1)
        try:
            fields[key] = scalar(raw)
        except ValueError as exc:
            report.error(path, f"invalid interface string {key}: {exc}", i + 1)
    for key in ("display_name", "short_description", "default_prompt"):
        if not fields.get(key, "").strip():
            report.error(path, f"missing nonempty interface string: {key}")
    if fields.get("default_prompt") and f"${SKILL_NAME}" not in fields["default_prompt"]:
        report.error(path, f"default_prompt must mention ${SKILL_NAME}")


def check_local_link(path: Path, destination: str, report: Report, line: int) -> None:
    destination = destination.strip("<>")
    if re.match(r"^[A-Za-z]:[\\/]", destination) or "\\" in destination:
        report.error(path, f"use portable relative paths in links: {destination}", line)
        return
    try:
        parsed = urlsplit(destination)
    except ValueError:
        report.error(path, f"invalid link destination: {destination}", line)
        return
    if parsed.scheme or parsed.netloc or not parsed.path:
        return  # Network URLs and fragment-only anchors are intentionally unchecked.
    decoded = unquote(parsed.path)
    if decoded.startswith("/"):
        report.error(path, f"use a relative path, not an absolute local path: {destination}", line)
        return
    target = (path.parent / decoded).resolve()
    skill = (report.root / SKILL_RELATIVE_PATH).resolve()
    boundary = skill if path.is_relative_to(skill) else report.root
    if not target.is_relative_to(boundary):
        report.error(path, f"link leaves its distributable boundary: {destination}", line)
    elif not target.exists():
        report.error(path, f"missing local link target: {destination}", line)
    elif boundary == skill:
        relative = target.relative_to(skill).as_posix()
        included = relative in PACKAGE_FILES or any(item.startswith(relative.rstrip("/") + "/") for item in PACKAGE_FILES)
        if relative != "." and not included:
            report.error(path, f"link target is absent from the release allowlist: {destination}", line)


def check_markdown(path: Path, text: str, report: Report, *, base_line: int = 0, template: bool = False) -> None:
    lines = text.splitlines()
    visible: list[tuple[int, str]] = []
    opened: tuple[str, int, str, int] | None = None
    contents: list[str] = []
    frontmatter_end = -1
    if not template and lines and lines[0] == "---" and "---" in lines[1:]:
        frontmatter_end = lines.index("---", 1)
    for index, line in enumerate(lines):
        number = base_line + index + 1
        if index <= frontmatter_end:
            continue
        fence = FENCE.match(line)
        if opened:
            marker, count, language, start = opened
            if fence and fence[1][0] == marker and len(fence[1]) >= count and not fence[2].strip():
                if language in {"md", "markdown"}:
                    check_markdown(path, "\n".join(contents), report, base_line=start, template=True)
                opened = None
                contents = []
            else:
                contents.append(line)
            continue
        if fence:
            if fence[1][0] == "`" and "`" in fence[2]:
                report.error(path, "backtick fence info string contains a backtick", number)
            info = fence[2].strip().split()
            opened = (fence[1][0], len(fence[1]), info[0].lower() if info else "", number)
            continue
        if HEADING.match(line) and index + 1 < len(lines) and lines[index + 1].strip():
            report.error(path, "put a blank line after an ATX heading", number)
        visible.append((number, INLINE_CODE.sub("", line)))
    if opened:
        where = "inside a Markdown template" if template else "in Markdown"
        report.error(path, f"unclosed {opened[0] * opened[1]} fence {where}", opened[3])
    if template:
        return  # Template placeholders and sample links need not be real files.
    definitions: set[str] = set()
    usages: list[tuple[str, int]] = []
    for number, line in visible:
        definition = LINK_DEFINITION.match(line)
        if definition:
            definitions.add(" ".join(definition[1].lower().split()))
            check_local_link(path, definition[2], report, number)
            continue
        for match in INLINE_LINK.finditer(line):
            check_local_link(path, match[1], report, number)
        for match in REFERENCE_LINK.finditer(line):
            label = " ".join((match[2] or match[1]).lower().split())
            usages.append((label, number))
    for label, number in usages:
        if label not in definitions:
            report.error(path, f"undefined reference-style link: [{label}]", number)


def load_json(path: Path, report: Report) -> dict | None:
    text = read_text(path, report)
    if text is None:
        return None

    def unique_object(pairs: list[tuple[str, object]]) -> dict:
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    def invalid_constant(value: str) -> None:
        raise ValueError(f"nonstandard JSON constant: {value}")

    try:
        data = json.loads(text, object_pairs_hook=unique_object, parse_constant=invalid_constant)
        if not isinstance(data, dict):
            raise ValueError("top-level value must be an object")
        return data
    except ValueError as exc:
        report.error(path, f"invalid JSON: {exc}")
        return None


def check_case(path: Path, data: dict, report: Report) -> None:
    def require(obj: dict, key: str, kind: type, prefix: str = "") -> object:
        value = obj.get(key)
        if not isinstance(value, kind) or (kind is str and not value.strip()):
            report.error(path, f"{prefix}{key} must be a nonempty string" if kind is str else f"{prefix}{key} must be {kind.__name__}")
            return {} if kind is dict else [] if kind is list else ""
        return value

    def strings(obj: dict, key: str, prefix: str = "") -> list:
        values = require(obj, key, list, prefix)
        if any(not isinstance(item, str) or not item.strip() for item in values):
            report.error(path, f"{prefix}{key} must contain nonempty strings")
        return values

    for key in ("case_id", "title", "document_type", "document_purpose", "user_prompt"):
        require(data, key, str)
    audience = require(data, "audience", dict)
    for key in ("primary", "prior_knowledge", "use_context"):
        require(audience, key, str, "audience.")
    if "source_draft" not in data or (data["source_draft"] is not None and not isinstance(data["source_draft"], str)):
        report.error(path, "source_draft must be a string or null")
    facts = require(data, "source_facts", list)
    fact_ids: set[str] = set()
    if not facts:
        report.error(path, "source_facts must not be empty")
    for i, fact in enumerate(facts):
        prefix = f"source_facts[{i}]."
        if not isinstance(fact, dict):
            report.error(path, f"{prefix[:-1]} must be an object")
            continue
        identifier = require(fact, "id", str, prefix)
        require(fact, "text", str, prefix)
        if identifier in fact_ids:
            report.error(path, f"duplicate fact ID: {identifier}")
        fact_ids.add(identifier)
        if not isinstance(fact.get("certainty"), str) or fact["certainty"] not in {"confirmed", "hypothesis", "unknown"}:
            report.error(path, f"{prefix}certainty must be confirmed, hypothesis, or unknown")
    claims = require(data, "verifiable_claims", list)
    claim_ids: set[str] = set()
    if not claims:
        report.error(path, "verifiable_claims must not be empty")
    for i, claim in enumerate(claims):
        prefix = f"verifiable_claims[{i}]."
        if not isinstance(claim, dict):
            report.error(path, f"{prefix[:-1]} must be an object")
            continue
        identifier = require(claim, "id", str, prefix)
        require(claim, "claim", str, prefix)
        if identifier in claim_ids:
            report.error(path, f"duplicate claim ID: {identifier}")
        claim_ids.add(identifier)
        refs = strings(claim, "source_refs", prefix)
        if not refs or any(not isinstance(ref, str) or ref not in fact_ids for ref in refs):
            report.error(path, f"{prefix}source_refs must reference existing fact IDs")
        if type(claim.get("required")) is not bool:
            report.error(path, f"{prefix}required must be a boolean")
        if not isinstance(claim.get("severity_if_wrong"), str) or claim["severity_if_wrong"] not in {"material", "minor"}:
            report.error(path, f"{prefix}severity_if_wrong must be material or minor")
    checks = require(data, "expected_checks", dict)
    for key in ("must_include", "forbidden_inventions", "hard_fail_if"):
        strings(checks, key, "expected_checks.")
    for i, identifier in enumerate(require(checks, "preserve_identifiers", list, "expected_checks.")):
        if not isinstance(identifier, dict):
            report.error(path, f"expected_checks.preserve_identifiers[{i}] must be an object")
            continue
        for key in ("value", "when"):
            require(identifier, key, str, f"expected_checks.preserve_identifiers[{i}].")
    length = require(data, "length_guidance", dict)
    if length.get("unit") != "Korean characters including spaces":
        report.error(path, "length_guidance.unit must be 'Korean characters including spaces'")
    minimum, maximum = length.get("suggested_min"), length.get("suggested_max")
    if type(minimum) is not int or type(maximum) is not int or minimum < 0 or maximum < minimum:
        report.error(path, "length_guidance requires nonnegative integer min <= max")
    if length.get("scoring") is not False:
        report.error(path, "length_guidance.scoring must be false; length is not a score")


def check_rubric(path: Path, data: dict, report: Report) -> None:
    for key in ("rubric_id", "language"):
        if not isinstance(data.get(key), str) or not data[key].strip():
            report.error(path, f"{key} must be a nonempty string")
    principles = data.get("scoring_principles")
    if not isinstance(principles, list) or not principles or any(not isinstance(item, str) or not item.strip() for item in principles):
        report.error(path, "scoring_principles must be a nonempty list of strings")
    dimensions = data.get("dimensions")
    if not isinstance(dimensions, list) or len(dimensions) != 5:
        report.error(path, "dimensions must contain five scoring dimensions")
        dimensions = []
    identifiers: set[str] = set()
    for i, dimension in enumerate(dimensions):
        if not isinstance(dimension, dict):
            report.error(path, f"dimensions[{i}] must be an object")
            continue
        for key in ("id", "title", "description"):
            value = dimension.get(key)
            if not isinstance(value, str) or not value.strip():
                report.error(path, f"dimensions[{i}].{key} must be a nonempty string")
        identifier = dimension.get("id")
        if isinstance(identifier, str):
            if identifier in identifiers:
                report.error(path, f"duplicate dimension ID: {identifier}")
            identifiers.add(identifier)
        if type(dimension.get("max_score")) is not int or dimension["max_score"] != 4:
            report.error(path, f"dimensions[{i}].max_score must be 4")
        if type(dimension.get("weight")) is not int or dimension["weight"] != 1:
            report.error(path, f"dimensions[{i}].weight must be 1")
        anchors = dimension.get("anchors")
        if not isinstance(anchors, dict) or set(anchors) != set("01234") or any(not isinstance(value, str) or not value.strip() for value in anchors.values()):
            report.error(path, f"dimensions[{i}].anchors must contain string anchors 0 through 4")
    hard_fail = data.get("hard_fail")
    if not isinstance(hard_fail, dict):
        report.error(path, "hard_fail must be an object")
    else:
        for key in ("definition", "handling"):
            if not isinstance(hard_fail.get(key), str) or not hard_fail[key].strip():
                report.error(path, f"hard_fail.{key} must be a nonempty string")
        triggers = hard_fail.get("not_automatic_triggers")
        if not isinstance(triggers, list) or any(not isinstance(item, str) for item in triggers):
            report.error(path, "hard_fail.not_automatic_triggers must be a list of strings")
        criteria = hard_fail.get("criteria")
        if not isinstance(criteria, list) or not criteria:
            report.error(path, "hard_fail.criteria must be a nonempty list")
        else:
            criterion_ids: set[str] = set()
            for i, criterion in enumerate(criteria):
                if not isinstance(criterion, dict) or any(not isinstance(criterion.get(key), str) or not criterion[key].strip() for key in ("id", "description")):
                    report.error(path, f"hard_fail.criteria[{i}] must contain string id and description")
                elif criterion["id"] in criterion_ids:
                    report.error(path, f"duplicate hard-fail criterion ID: {criterion['id']}")
                else:
                    criterion_ids.add(criterion["id"])
    if not isinstance(data.get("evaluation_record"), dict):
        report.error(path, "evaluation_record must be an object")


def validate_repository(root: Path, *, skill_only: bool = False) -> Report:
    root = root.resolve()
    report = Report(root)
    skill = root / SKILL_RELATIVE_PATH
    contents: dict[Path, str] = {}
    for relative in PACKAGE_FILES:
        path = skill / relative
        chain = [path, *path.parents]
        if any(item.is_symlink() for item in chain if item.is_relative_to(skill)):
            report.error(path, "release files and their parent directories must not be symlinks")
            continue
        if not path.is_file():
            report.error(path, "missing required release file")
            continue
        text = read_text(path, report)
        if text is not None:
            contents[path] = text
            if not text.strip():
                report.error(path, "required release file is empty")
    skill_md = skill / "SKILL.md"
    if skill_md in contents:
        check_frontmatter(skill_md, contents[skill_md], report)
    metadata = skill / "agents/openai.yaml"
    if metadata in contents:
        check_agent_metadata(metadata, contents[metadata], report)
    markdown = [path for path in contents if path.suffix == ".md"]
    if not skill_only:
        markdown += [path for path in (root / "README.md", root / "evaluations/protocol.md") if path.is_file()]
        markdown += list((root / "docs").rglob("*.md"))
    for path in sorted(set(markdown)):
        if not path.resolve().is_relative_to(root):
            report.error(path, "Markdown path leaves the repository")
            continue
        text = contents.get(path)
        if text is None:
            text = read_text(path, report)
        if text is not None:
            report.markdown_count += 1
            check_markdown(path, text, report)
    if not skill_only:
        cases_dir = root / "evaluations/cases"
        for name in CASE_FILES:
            if not (cases_dir / name).is_file():
                report.error(cases_dir / name, "missing required evaluation case")
        case_ids: set[str] = set()
        for path in sorted(cases_dir.glob("*.json")):
            data = load_json(path, report)
            if data is None:
                continue
            report.case_count += 1
            check_case(path, data, report)
            identifier = data.get("case_id")
            if isinstance(identifier, str):
                if identifier in case_ids:
                    report.error(path, f"duplicate case_id across files: {identifier}")
                case_ids.add(identifier)
        rubric_path = root / "evaluations/rubric.json"
        rubric = load_json(rubric_path, report)
        if rubric is not None:
            check_rubric(rubric_path, rubric, report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1], help="repository root (default: this script's repository)")
    parser.add_argument("--skill-only", action="store_true", help="check distributable skill files only; omit repository docs and evaluation JSON")
    args = parser.parse_args()
    report = validate_repository(args.repo_root, skill_only=args.skill_only)
    if report.errors:
        for error in report.errors:
            print(f"ERROR {error}", file=sys.stderr)
        print(f"FAIL: {len(report.errors)} structural error(s).", file=sys.stderr)
        return 1
    scope = "skill only" if args.skill_only else "repository"
    print(f"PASS ({scope}): {len(PACKAGE_FILES)} release files, {report.markdown_count} Markdown files, {report.case_count} evaluation cases.")
    print("Structural checks only; model execution, writing quality, and factual scoring are separate.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
