#!/usr/bin/env python3
"""Check that published repairs have complete, source-linked review evidence.

This validates recorded decisions, hashes, and exact quotations. It does not
decide whether prose is natural or whether a quoted passage proves a claim.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from check import PACKAGE_FILES
from check_claims import (
    ROOT, Check, cli_path, evidence, validate_contract, validate_outputs,
    validate_reviews,
)


DEFAULT_RUN = "evaluations/runs/2026-11-03-v0.5.0"


def validate_decisions(reviews: list[dict], cases: dict, check: Check) -> None:
    """Integrity alone accepts honest failures; a repaired release must close them."""
    for review in reviews:
        for doc in review.get("documents", []):
            case_id = doc.get("case_id")
            known = cases.get(case_id, {})
            required = {r["id"] for r in known.get("requirements", []) if r["required"]}
            for row in doc.get("requirements", []):
                if row.get("requirement_id") in required and row.get("status") != "preserved":
                    check.error(case_id, f"unresolved required meaning: {row.get('requirement_id')}")
            for row in doc.get("questions", []):
                if row.get("answer_status") != "sufficient" or row.get("local_condition_gap"):
                    check.error(case_id, f"unresolved navigation question: {row.get('question_id')}")
            if doc.get("hard_fail", {}).get("value") is not False:
                check.error(case_id, "hard failure is not closed")
            if doc.get("open_issues") != []:
                check.error(case_id, "open_issues must explicitly be empty for a final repaired document")


def validate_repairs(criteria: dict, reviews: list[dict], texts: dict[str, str], check: Check) -> int:
    expected = {}
    for item, loc in check.objects(criteria, "checks", "repair_checks", nonempty=True):
        identifier = check.text(item, "id", loc)
        case_id = check.text(item, "case_id", loc)
        if identifier in expected:
            check.error(loc, "duplicate repair criterion")
        if case_id not in texts:
            check.error(loc, "repair criterion is outside the final document set")
        expected[identifier] = case_id
    seen = set()
    for index, review in enumerate(reviews):
        for row, loc in check.objects(review, "repair_checks", f"review[{index}]"):
            identifier = check.text(row, "id", loc)
            case_id = check.text(row, "case_id", loc)
            if identifier in seen:
                check.error(loc, "duplicate repair decision")
            seen.add(identifier)
            if identifier not in expected or expected[identifier] != case_id:
                check.error(loc, "unknown or mismatched repair criterion")
            if row.get("status") != "resolved":
                check.error(loc, "repair is not resolved")
            check.text(row, "resolution", loc)
            evidence(row, "evidence", texts.get(case_id), check, loc, needed=True)
    if set(expected) != seen:
        check.error("repairs", f"repair decision set mismatch: missing={sorted(set(expected)-seen)}, extra={sorted(seen-set(expected))}")
    return len(seen)


def validate_run(run: Path, check: Check) -> tuple[int, int]:
    manifest = check.json(run / "manifest.json")
    contract = check.json(ROOT / "evaluations/contracts/preservation-v1.json")
    criteria = check.json(run / "repair-checks.json")
    index = check.json(run / "output-index.json")
    for name, data in (("manifest", manifest), ("contract", contract),
                       ("repair_checks", criteria), ("output_index", index)):
        if data == {}:
            check.error(name, "required JSON object must not be empty")
    if not all((manifest, contract, criteria, index)):
        return 0, 0
    if manifest.get("status") != "completed":
        check.error("manifest", "status must be completed")
    cases = validate_contract(contract, check)
    documents, _ = validate_outputs(index, cases, check)
    paths = check.strings(manifest, "review_files", "manifest", nonempty=True)
    review_pairs = []
    for value in paths:
        path = check.relative_file(value, "manifest.review_files")
        data = check.json(path) if path else None
        if data:
            review_pairs.append((path, data))
    validate_reviews(review_pairs, documents, cases, check)
    reviews = [data for _, data in review_pairs]
    validate_decisions(reviews, cases, check)
    texts = {case_id: value["text"] for (case_id, _), value in documents.items()}
    manifest_cases = list(check.objects(manifest, "cases", "manifest", nonempty=True))
    expected_ids = [case["id"] for case, _ in manifest_cases]
    if set(expected_ids) != set(cases):
        check.error("manifest", "final release must include every preservation-contract case")
    if len(set(expected_ids)) != len(expected_ids) or set(expected_ids) != set(texts) or len(documents) != len(expected_ids):
        check.error("manifest", "exactly one final output is required for every case")
    output_paths = {doc["case_id"]: doc["path"] for doc in index["documents"]}
    hashes = manifest.get("artifact_hashes", {})
    for key in ("frozen_files", "artifact_hashes"):
        entries = manifest.get(key)
        if not isinstance(entries, dict) or not entries:
            check.error("manifest", f"{key} must be a nonempty hash map")
            continue
        for value, digest in entries.items():
            check.frozen_text(check.relative_file(value, key), digest, value)
    for case, loc in manifest_cases:
        latest = check.text(case, "latest", loc)
        example = check.text(case, "example", loc)
        if output_paths.get(case["id"]) != latest:
            check.error(loc, "output index does not point to the final output")
        if latest not in hashes or example not in hashes:
            check.error(loc, "final output and published example must both have hashes")
        left = check.relative_file(latest, loc)
        right = check.relative_file(example, loc)
        if left and right and check.read(left) != check.read(right):
            check.error(loc, "published example differs from the reviewed final output")
    snapshot = check.relative_file(check.text(manifest, "skill_snapshot_path", "manifest"), "manifest")
    skill_files = manifest.get("skill_files")
    if not isinstance(skill_files, dict):
        check.error("manifest", "skill_files must be a hash map")
        skill_files = {}
    if set(skill_files) != set(PACKAGE_FILES):
        check.error("manifest", "skill_files must include exactly the packaged skill resources")
    for relative in PACKAGE_FILES:
        if relative not in skill_files:
            continue
        digest = check.text(skill_files, relative, "manifest.skill_files")
        live = ROOT / "skills/korean-dev-writing" / relative
        if snapshot:
            check.frozen_text(snapshot / relative, digest, f"snapshot/{relative}")
        check.frozen_text(live, digest, f"installed skill/{relative}")
    return len(documents), validate_repairs(criteria, reviews, texts, check)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", default=DEFAULT_RUN)
    args = parser.parse_args()
    check = Check()
    documents, repairs = validate_run(cli_path(args.run), check)
    if check.errors:
        for error in check.errors:
            print(f"ERROR {error}", file=sys.stderr)
        return 1
    print(f"PASS: {documents} reviewed final documents, {repairs} resolved repairs, matching published examples.")
    print("Recorded review decisions and artifact integrity only; this is not an automated semantic judgment.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
