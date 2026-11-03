#!/usr/bin/env python3
"""Validate preservation contracts, frozen outputs, and source-linked review records.

Uses only the Python standard library. This checks structure, references, SHA-256,
verbatim evidence, and literal presence. It never judges meaning or writing quality.
Relative CLI paths and embedded file paths are resolved from the repository root.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT = "evaluations/contracts/preservation-v1.json"
STATUSES = {"preserved", "partial", "missing", "conflict"}
ANSWER_STATUSES = {"sufficient", "partial", "missing", "incorrect"}
SIGNAL_KINDS = {"identifier", "path", "command", "number", "unit", "service_name", "literal"}
SHA256 = re.compile(r"[0-9a-f]{64}")


class Check:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.read_paths: set[Path] = set()

    def error(self, where: str, message: str) -> None:
        self.errors.append(f"{where}: {message}")

    def text(self, obj: dict, key: str, where: str, *, empty: bool = False) -> str:
        value = obj.get(key)
        if not isinstance(value, str) or (not empty and not value.strip()):
            self.error(where, f"{key} must be a {'string' if empty else 'nonempty string'}")
            return ""
        return value

    def items(self, obj: dict, key: str, where: str, *, nonempty: bool = False) -> list:
        value = obj.get(key)
        if not isinstance(value, list) or (nonempty and not value):
            self.error(where, f"{key} must be a {'nonempty ' if nonempty else ''}list")
            return []
        return value

    def strings(self, obj: dict, key: str, where: str, *, nonempty: bool = False) -> list[str]:
        values = self.items(obj, key, where, nonempty=nonempty)
        if any(not isinstance(value, str) or not value.strip() for value in values):
            self.error(where, f"{key} must contain nonempty strings")
            return []
        if len(values) != len(set(values)):
            self.error(where, f"{key} contains duplicate entries")
        return values

    def objects(self, obj: dict, key: str, where: str, *, nonempty: bool = False):
        for index, value in enumerate(self.items(obj, key, where, nonempty=nonempty)):
            location = f"{where}.{key}[{index}]"
            if not isinstance(value, dict):
                self.error(location, "must be an object")
                continue
            yield value, location

    def read(self, path: Path) -> bytes | None:
        self.read_paths.add(path.resolve())
        try:
            return path.read_bytes()
        except OSError as exc:
            self.error(str(path), str(exc))
            return None

    def json(self, path: Path) -> dict | None:
        raw = self.read(path)
        if raw is None:
            return None

        def unique(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError(f"duplicate JSON key: {key}")
                result[key] = value
            return result

        def invalid_constant(value):
            raise ValueError(f"nonstandard JSON constant: {value}")

        try:
            value = json.loads(raw.decode("utf-8"), object_pairs_hook=unique, parse_constant=invalid_constant)
            if not isinstance(value, dict):
                raise ValueError("top-level value must be an object")
            return value
        except (UnicodeDecodeError, ValueError) as exc:
            self.error(str(path), f"invalid UTF-8 JSON: {exc}")
            return None

    def relative_file(self, value: str, where: str) -> Path | None:
        if not value:
            return None
        path = Path(value)
        if path.is_absolute() or "\\" in value or re.match(r"^[A-Za-z]:", value):
            self.error(where, "file path must be repository-relative with forward slashes")
            return None
        resolved = (ROOT / path).resolve()
        if not resolved.is_relative_to(ROOT):
            self.error(where, "file path leaves the repository")
            return None
        return resolved

    def frozen_text(self, path: Path | None, digest: str, where: str) -> str | None:
        if not SHA256.fullmatch(digest):
            self.error(where, "sha256 must be 64 lowercase hexadecimal characters")
        if path is None:
            return None
        raw = self.read(path)
        if raw is None:
            return None
        if hashlib.sha256(raw).hexdigest() != digest:
            self.error(where, "SHA-256 mismatch")
        try:
            value = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            self.error(where, f"file is not UTF-8: {exc}")
            return None
        if not value.strip():
            self.error(where, "file is empty")
        return value


def legacy_references(source: dict, check: Check, where: str) -> tuple[dict[str, tuple[bool, set[str]]], set[str]]:
    """Expose original obligations without editing or upgrading their scope."""
    facts = {}
    for fact, loc in check.objects(source, "source_facts", where, nonempty=True):
        identifier = check.text(fact, "id", loc)
        check.text(fact, "text", loc)
        if identifier in facts:
            check.error(loc, f"duplicate source fact: {identifier}")
        facts[identifier] = fact
    refs = {f"source_facts:{identifier}": (False, {identifier}) for identifier in facts}
    mandatory: set[str] = set()
    if "verifiable_claims" in source:
        for claim, loc in check.objects(source, "verifiable_claims", where, nonempty=True):
            identifier = check.text(claim, "id", loc)
            key = f"verifiable_claims:{identifier}"
            required = claim.get("required")
            if type(required) is not bool:
                check.error(loc, "required must be a boolean")
            source_refs = set(check.strings(claim, "source_refs", loc, nonempty=True))
            if not source_refs <= facts.keys():
                check.error(loc, "source_refs contains unknown source facts")
            if key in refs:
                check.error(loc, f"duplicate legacy claim: {identifier}")
            refs[key] = (required is True, source_refs)
            if required is True:
                mandatory.add(key)
    if "must_preserve" in source:
        for identifier in check.strings(source, "must_preserve", where, nonempty=True):
            if identifier not in facts:
                check.error(where, f"unknown must_preserve fact: {identifier}")
            key = f"must_preserve:{identifier}"
            refs[key] = (True, {identifier})
            mandatory.add(key)
    expected = source.get("expected_checks", {})
    if isinstance(expected, dict) and "must_include" in expected:
        for index, value in enumerate(check.strings(expected, "must_include", where)):
            key = f"must_include:{index}"
            refs[key] = (True, set(facts))
            mandatory.add(key)
    return refs, mandatory


def validate_contract(data: dict, check: Check) -> dict[str, dict]:
    check.text(data, "contract_id", "contract")
    check.text(data, "version", "contract")
    cases = {}
    for case, loc in check.objects(data, "cases", "contract", nonempty=True):
        case_id = check.text(case, "case_id", loc)
        if case_id in cases:
            check.error(loc, f"duplicate case_id: {case_id}")
        cases[case_id] = case
        source_path = check.relative_file(check.text(case, "source_path", loc), loc)
        check.frozen_text(source_path, check.text(case, "source_sha256", loc), f"{loc}.source")
        input_path = check.relative_file(check.text(case, "input_path", loc), loc)
        check.frozen_text(input_path, check.text(case, "input_sha256", loc), f"{loc}.input")
        source = check.json(source_path) if source_path else None
        legacy, mandatory = legacy_references(source, check, f"{loc}.source") if source else ({}, set())
        if source and source.get("case_id") != case_id:
            check.error(loc, "case_id differs from source case_id")
        facts = {key.split(":", 1)[1] for key in legacy if key.startswith("source_facts:")}
        requirements = {}
        covered: set[str] = set()
        for requirement, req_loc in check.objects(case, "requirements", loc, nonempty=True):
            identifier = check.text(requirement, "id", req_loc)
            if identifier in requirements:
                check.error(req_loc, f"duplicate requirement ID: {identifier}")
            requirements[identifier] = requirement
            source_refs = set(check.strings(requirement, "source_refs", req_loc, nonempty=True))
            if not source_refs <= facts:
                check.error(req_loc, f"unknown source_refs: {sorted(source_refs - facts)}")
            check.text(requirement, "meaning", req_loc)
            required = requirement.get("required")
            if type(required) is not bool:
                check.error(req_loc, "required must be a boolean")
            legacy_refs = check.strings(requirement, "legacy_refs", req_loc)
            if mandatory and required is True and not any(ref in mandatory for ref in legacy_refs):
                check.error(req_loc, "required obligation must link to an original required claim, must_preserve, or must_include")
            for ref in legacy_refs:
                if ref not in legacy:
                    check.error(req_loc, f"unknown legacy_ref: {ref}")
                    continue
                was_required, legacy_sources = legacy[ref]
                if not source_refs & legacy_sources:
                    check.error(req_loc, f"source_refs do not overlap legacy_ref {ref}")
                if required is True:
                    if ref.startswith("verifiable_claims:") and not was_required:
                        check.error(req_loc, f"optional legacy claim cannot become required: {ref}")
                    if was_required:
                        covered.add(ref)
            seen_signals = set()
            for signal, signal_loc in check.objects(requirement, "literal_signals", req_loc):
                kind = check.text(signal, "kind", signal_loc)
                value = check.text(signal, "value", signal_loc)
                if kind not in SIGNAL_KINDS:
                    check.error(signal_loc, f"kind must be one of {sorted(SIGNAL_KINDS)}")
                pair = (kind, value)
                if pair in seen_signals:
                    check.error(signal_loc, "duplicate literal signal")
                seen_signals.add(pair)
        if not any(req.get("required") is True for req in requirements.values()):
            check.error(loc, "at least one required requirement is needed")
        if mandatory - covered:
            check.error(loc, f"original required obligations are not covered: {sorted(mandatory - covered)}")
        questions = {}
        for question, qloc in check.objects(case, "questions", loc, nonempty=True):
            identifier = check.text(question, "id", qloc)
            if identifier in questions:
                check.error(qloc, f"duplicate question ID: {identifier}")
            questions[identifier] = question
            check.text(question, "question", qloc)
            check.text(question, "expected_answer", qloc)
            refs = set(check.strings(question, "requirement_refs", qloc, nonempty=True))
            if not refs <= requirements.keys():
                check.error(qloc, f"unknown requirement_refs: {sorted(refs - requirements.keys())}")
    return cases


def literal_present(value: str, kind: str, text: str) -> bool:
    # ASCII token edges prevent 1-in-1000 and option-name prefixes from matching.
    # Korean particles are not identifier characters. No semantic equivalence is inferred.
    edges = {
        "number": r"0-9.",
        "identifier": r"A-Za-z0-9_\-",
        "path": r"A-Za-z0-9_./\\\-",
    }
    if kind in edges:
        edge = edges[kind]
        return re.search(rf"(?<![{edge}]){re.escape(value)}(?![{edge}])", text) is not None
    return value in text


def validate_outputs(index: dict, cases: dict, check: Check) -> tuple[dict, list]:
    documents = {}
    signals = []
    for doc, loc in check.objects(index, "documents", "output_index", nonempty=True):
        case_id = check.text(doc, "case_id", loc)
        label = check.text(doc, "label", loc)
        key = (case_id, label)
        if key in documents:
            check.error(loc, f"duplicate output document: {key}")
        path_value = check.text(doc, "path", loc)
        path = check.relative_file(path_value, loc)
        digest = check.text(doc, "sha256", loc)
        output = check.frozen_text(path, digest, loc)
        documents[key] = {"text": output, "case_id": case_id, "label": label}
        if case_id not in cases:
            check.error(loc, f"unknown case_id: {case_id}")
            continue
        if output is None:
            continue
        items = []
        for requirement in cases[case_id].get("requirements", []):
            if not isinstance(requirement, dict):
                continue
            for signal in requirement.get("literal_signals", []):
                if not isinstance(signal, dict) or not isinstance(signal.get("value"), str):
                    continue
                items.append({
                    "requirement_id": requirement.get("id"),
                    "required": requirement.get("required"),
                    "kind": signal.get("kind"),
                    "value": signal["value"],
                    "present": literal_present(signal["value"], signal.get("kind"), output),
                })
        signals.append({"case_id": case_id, "label": label, "path": path_value,
                        "sha256": digest, "characters": len(output), "literal_signals": items})
    return documents, signals


def evidence(obj: dict, key: str, output: str | None, check: Check, where: str, *, needed: bool) -> None:
    quotes = check.strings(obj, key, where, nonempty=needed)
    if output is not None:
        for quote in quotes:
            if quote not in output:
                check.error(where, f"{key} quote is not an exact contiguous substring of the output: {quote[:80]!r}")


def validate_reviews(reviews: list[tuple[Path, dict]], documents: dict, cases: dict, check: Check) -> int:
    seen_documents = set()
    for path, data in reviews:
        for doc, loc in check.objects(data, "documents", str(path), nonempty=True):
            case_id = check.text(doc, "case_id", loc)
            label = check.text(doc, "label", loc)
            key = (case_id, label)
            if key in seen_documents:
                check.error(loc, f"duplicate review document across submitted files: {key}")
            seen_documents.add(key)
            if key not in documents:
                check.error(loc, f"review document is absent from output_index: {key}")
                continue
            if case_id not in cases:
                continue
            output = documents[key]["text"]
            known = {req["id"]: req for req in cases[case_id]["requirements"]}
            seen_requirements = set()
            for row, rloc in check.objects(doc, "requirements", loc):
                identifier = check.text(row, "requirement_id", rloc)
                if identifier in seen_requirements:
                    check.error(rloc, f"duplicate requirement review: {identifier}")
                seen_requirements.add(identifier)
                if identifier not in known:
                    check.error(rloc, f"unknown requirement_id: {identifier}")
                status = check.text(row, "status", rloc)
                if status not in STATUSES:
                    check.error(rloc, f"status must be one of {sorted(STATUSES)}")
                check.text(row, "reason", rloc)
                evidence(row, "evidence", output, check, rloc, needed=status in STATUSES - {"missing"})
            required_ids = {identifier for identifier, req in known.items() if req["required"]}
            if required_ids - seen_requirements:
                check.error(loc, f"missing required review rows: {sorted(required_ids - seen_requirements)}")
            known_questions = {q["id"] for q in cases[case_id]["questions"]}
            seen_questions = set()
            for row, qloc in check.objects(doc, "questions", loc):
                identifier = check.text(row, "question_id", qloc)
                if identifier in seen_questions:
                    check.error(qloc, f"duplicate question review: {identifier}")
                seen_questions.add(identifier)
                if identifier not in known_questions:
                    check.error(qloc, f"unknown question_id: {identifier}")
                status = check.text(row, "answer_status", qloc)
                if status not in ANSWER_STATUSES:
                    check.error(qloc, f"answer_status must be one of {sorted(ANSWER_STATUSES)}")
                check.text(row, "entry_location", qloc)
                check.strings(row, "additional_locations", qloc)
                check.text(row, "local_condition_gap", qloc, empty=True)
                check.text(row, "reason", qloc)
                evidence(row, "answer_evidence", output, check, qloc,
                         needed=status in ANSWER_STATUSES - {"missing"})
            if known_questions - seen_questions:
                check.error(loc, f"missing question review rows: {sorted(known_questions - seen_questions)}")
            hard_fail = doc.get("hard_fail")
            if not isinstance(hard_fail, dict):
                check.error(loc, "hard_fail must be an object")
            else:
                if type(hard_fail.get("value")) is not bool:
                    check.error(loc, "hard_fail.value must be a boolean")
                check.text(hard_fail, "reason", f"{loc}.hard_fail")
                evidence(hard_fail, "evidence", output, check, f"{loc}.hard_fail",
                         needed=hard_fail.get("value") is True)
    if set(documents) - seen_documents:
        check.error("reviews", f"documents missing from submitted review files: {sorted(set(documents) - seen_documents)}")
    return len(seen_documents)


def cli_path(value: str) -> Path:
    path = Path(value)
    return (path if path.is_absolute() else ROOT / path).resolve()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", default=DEFAULT_CONTRACT)
    parser.add_argument("--output-index", help="JSON with documents: case_id, label, path, sha256")
    parser.add_argument("--reviews", nargs="+", help="review JSON files; the union must cover the output index")
    parser.add_argument("--write-signals", help="write literal-presence signals and Unicode character counts")
    args = parser.parse_args()
    if (args.reviews or args.write_signals) and not args.output_index:
        parser.error("--reviews and --write-signals require --output-index")
    check = Check()
    contract_path = cli_path(args.contract)
    contract = check.json(contract_path)
    cases = validate_contract(contract, check) if contract else {}
    documents, signals = {}, []
    index_path = cli_path(args.output_index) if args.output_index else None
    if index_path:
        index = check.json(index_path)
        if index and not check.errors:
            documents, signals = validate_outputs(index, cases, check)
    reviewed = 0
    if args.reviews:
        reviews = []
        for value in args.reviews:
            path = cli_path(value)
            data = check.json(path)
            if data is not None:
                reviews.append((path, data))
        if not check.errors:
            reviewed = validate_reviews(reviews, documents, cases, check)
    destination = cli_path(args.write_signals) if args.write_signals else None
    if destination and destination in check.read_paths:
        check.error(str(destination), "signals must not overwrite a contract, source, input, output, index, or review file")
    if check.errors:
        for error in check.errors:
            print(f"ERROR {error}", file=sys.stderr)
        print(f"FAIL: {len(check.errors)} contract/integrity error(s).", file=sys.stderr)
        return 1
    if destination:
        result = {
            "contract_id": contract["contract_id"],
            "contract_sha256": hashlib.sha256(contract_path.read_bytes()).hexdigest(),
            "output_index_sha256": hashlib.sha256(index_path.read_bytes()).hexdigest(),
            "measurement": "Unicode code points including whitespace, Markdown, and final newline",
            "automatic_scope": "Literal presence and character counts only; no semantic verdict, quality score, or hard_fail.",
            "documents": signals,
        }
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        except OSError as exc:
            print(f"ERROR {destination}: {exc}", file=sys.stderr)
            return 1
    print(f"PASS: {len(cases)} contract cases, {len(documents)} frozen outputs, {reviewed} review records.")
    print("Structure, references, hashes, and exact quotations only. Literal presence/absence is not a semantic verdict or hard_fail.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
