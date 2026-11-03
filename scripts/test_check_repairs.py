#!/usr/bin/env python3
"""Regression checks for stale or incomplete repair release decisions."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from check import PACKAGE_FILES
import check_claims
import check_repairs
from check_claims import Check
from check_repairs import validate_decisions, validate_repairs, validate_run


class RepairGateTests(unittest.TestCase):
    def setUp(self):
        self.criteria = {"checks": [{"id": "fix-local-condition", "case_id": "sample"}]}
        self.texts = {"sample": "실행 전에 조건을 확인하고, 실패하면 중단한다."}
        self.reviews = [{"repair_checks": [{
            "id": "fix-local-condition", "case_id": "sample", "status": "resolved",
            "resolution": "조건과 실패 대응을 실행 위치에 함께 배치했다.",
            "evidence": ["실행 전에 조건을 확인하고, 실패하면 중단한다."],
        }]}]

    def errors(self, reviews=None):
        check = Check()
        validate_repairs(self.criteria, self.reviews if reviews is None else reviews, self.texts, check)
        return check.errors

    def test_complete_evidence_passes(self):
        self.assertEqual([], self.errors())

    def test_missing_decision_fails(self):
        self.assertTrue(self.errors([{"repair_checks": []}]))

    def test_duplicate_decision_fails(self):
        self.assertTrue(self.errors(self.reviews + deepcopy(self.reviews)))

    def test_stale_quote_fails(self):
        self.reviews[0]["repair_checks"][0]["evidence"] = ["실패해도 계속한다."]
        self.assertTrue(self.errors())

    def test_wrong_case_fails(self):
        self.reviews[0]["repair_checks"][0]["case_id"] = "other"
        self.assertTrue(self.errors())

    def test_no_evidence_fails(self):
        self.reviews[0]["repair_checks"][0]["evidence"] = []
        self.assertTrue(self.errors())

    def test_open_repair_fails(self):
        self.reviews[0]["repair_checks"][0]["status"] = "open"
        self.assertTrue(self.errors())

    def test_preservation_and_navigation_cannot_pass_with_open_findings(self):
        cases = {"sample": {"requirements": [{"id": "fact", "required": True}]}}
        doc = {"case_id": "sample", "requirements": [{"requirement_id": "fact", "status": "preserved"}],
               "questions": [{"question_id": "nav", "answer_status": "sufficient", "local_condition_gap": ""}],
               "hard_fail": {"value": False}, "open_issues": []}
        check = Check()
        validate_decisions([{"documents": [doc]}], cases, check)
        self.assertEqual([], check.errors)
        for field in ("required", "navigation", "local_gap", "hard_fail", "open_issues"):
            with self.subTest(field=field):
                changed = deepcopy(doc)
                if field == "required":
                    changed["requirements"][0]["status"] = "partial"
                elif field == "navigation":
                    changed["questions"][0]["answer_status"] = "partial"
                elif field == "local_gap":
                    changed["questions"][0]["local_condition_gap"] = "실행 위치에 기한이 없음"
                elif field == "hard_fail":
                    changed["hard_fail"]["value"] = True
                else:
                    changed["open_issues"] = ["수정되지 않은 의미 누락"]
                check = Check()
                validate_decisions([{"documents": [changed]}], cases, check)
                self.assertTrue(check.errors)


class RepairRunTests(unittest.TestCase):
    """Exercise the release gate with files, rather than only individual helpers."""

    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        for module in (check_claims, check_repairs):
            replacement = patch.object(module, "ROOT", self.root)
            replacement.start()
            self.addCleanup(replacement.stop)
        self.run_path = "evaluations/runs/test-repairs"
        self.run = self.root / self.run_path
        self.manifest = {
            "status": "completed", "cases": [], "frozen_files": {},
            "artifact_hashes": {}, "skill_files": {},
            "skill_snapshot_path": self.run_path + "/snapshots/v0.5.0",
            "review_files": [self.run_path + f"/reviews/{i}.json" for i in range(3)],
        }
        self.contract = {"contract_id": "preservation-v1", "version": "1", "cases": []}
        self.index = {"documents": []}
        self.criteria = {"checks": []}
        self.reviews = [{"documents": [], "repair_checks": []} for _ in range(3)]
        self.texts = {}
        for relative in PACKAGE_FILES:
            raw = ("Skill resource: " + relative + "\n").encode()
            self.write("skills/korean-dev-writing/" + relative, raw)
            self.write(self.manifest["skill_snapshot_path"] + "/" + relative, raw)
            self.manifest["skill_files"][relative] = hashlib.sha256(raw).hexdigest()
        for i in range(10):
            case_id = f"case-{i}"
            text = f"문서 {i}: 실행 전에 조건을 확인하고, 실패하면 중단한다.\n"
            self.texts[case_id] = text
            source = f"evaluations/cases/{case_id}.json"
            input_path = self.run_path + f"/inputs/{case_id}.md"
            latest = self.run_path + f"/outputs/revised/{case_id}.md"
            example = f"docs/examples/{case_id}.md"
            source_sha = self.write_json(source, {
                "case_id": case_id, "source_facts": [{"id": "F1", "text": text}],
                "must_preserve": ["F1"],
            })
            input_sha = self.write(input_path, text.encode())
            output_sha = self.write(latest, text.encode())
            self.write(example, text.encode())
            self.manifest["frozen_files"].update({source: source_sha, input_path: input_sha})
            self.manifest["artifact_hashes"].update({latest: output_sha, example: output_sha})
            self.manifest["cases"].append({"id": case_id, "latest": latest, "example": example})
            self.contract["cases"].append({
                "case_id": case_id, "source_path": source, "source_sha256": source_sha,
                "input_path": input_path, "input_sha256": input_sha,
                "requirements": [{
                    "id": "fact", "source_refs": ["F1"], "meaning": text,
                    "required": True, "legacy_refs": ["must_preserve:F1"], "literal_signals": [],
                }],
                "questions": [{
                    "id": "nav", "question": "실패하면 어떻게 하는가?",
                    "expected_answer": "중단한다.", "requirement_refs": ["fact"],
                }],
            })
            self.index["documents"].append({
                "case_id": case_id, "label": "final", "path": latest, "sha256": output_sha,
            })
            self.reviews[i % 3]["documents"].append({
                "case_id": case_id, "label": "final", "requirements": [{
                    "requirement_id": "fact", "status": "preserved", "reason": "조건과 조치를 보존했다.",
                    "evidence": [text.strip()],
                }], "questions": [{
                    "question_id": "nav", "answer_status": "sufficient",
                    "entry_location": "첫 문단", "additional_locations": [], "local_condition_gap": "",
                    "reason": "조건과 행동을 함께 읽을 수 있다.", "answer_evidence": [text.strip()],
                }], "hard_fail": {"value": False, "reason": "확인한 오류 없음", "evidence": []},
                "open_issues": [],
            })
        # Some documents have no separate repair finding, but still require review.
        for i in range(11):
            case_id = f"case-{i % 6}"
            criterion = {"id": f"fix-{i}", "case_id": case_id}
            self.criteria["checks"].append(criterion)
            self.reviews[i % 3]["repair_checks"].append({
                **criterion, "status": "resolved", "resolution": "실행 위치에 중단 조건을 함께 두었다.",
                "evidence": [self.texts[case_id].strip()],
            })
        contract_path = "evaluations/contracts/preservation-v1.json"
        criteria_path = self.run_path + "/repair-checks.json"
        self.manifest["frozen_files"][contract_path] = self.write_json(contract_path, self.contract)
        self.manifest["frozen_files"][criteria_path] = self.write_json(criteria_path, self.criteria)
        self.save_run()

    def write(self, relative, raw):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        return hashlib.sha256(raw).hexdigest()

    def write_json(self, relative, data):
        return self.write(relative, (json.dumps(data, ensure_ascii=False) + "\n").encode())

    def save_run(self):
        for path, review in zip(self.manifest["review_files"], self.reviews):
            self.manifest["artifact_hashes"][path] = self.write_json(path, review)
        index_path = self.run_path + "/output-index.json"
        self.manifest["artifact_hashes"][index_path] = self.write_json(index_path, self.index)
        self.write_json(self.run_path + "/manifest.json", self.manifest)

    def validate(self):
        check = Check()
        counts = validate_run(self.run, check)
        return counts, check.errors

    def test_complete_ten_document_release_passes(self):
        counts, errors = self.validate()
        self.assertEqual((10, 11), counts)
        self.assertEqual([], errors)

    def test_case_omitted_from_manifest_outputs_and_reviews_still_fails(self):
        self.manifest["cases"] = [c for c in self.manifest["cases"] if c["id"] != "case-9"]
        self.index["documents"] = [d for d in self.index["documents"] if d["case_id"] != "case-9"]
        for review in self.reviews:
            review["documents"] = [d for d in review["documents"] if d["case_id"] != "case-9"]
        self.save_run()
        _, errors = self.validate()
        self.assertTrue(errors, "A final release cannot silently reduce the preservation contract's case set")

    def test_empty_or_incomplete_skill_file_map_fails(self):
        complete = deepcopy(self.manifest["skill_files"])
        for selected in ({}, {key: value for key, value in complete.items() if key != "references/reading-flow.md"}):
            with self.subTest(files=list(selected)):
                self.manifest["skill_files"] = selected
                self.save_run()
                _, errors = self.validate()
                self.assertTrue(errors, "Every packaged skill resource must be compared with the snapshot")

    def test_empty_required_json_cannot_report_zero_document_success(self):
        paths = [
            self.run_path + "/manifest.json", "evaluations/contracts/preservation-v1.json",
            self.run_path + "/repair-checks.json", self.run_path + "/output-index.json",
        ]
        for relative in paths:
            with self.subTest(path=relative):
                path = self.root / relative
                original = path.read_bytes()
                try:
                    self.write_json(relative, {})
                    _, errors = self.validate()
                    self.assertTrue(errors, "An empty required JSON object must not count as a successful release")
                finally:
                    path.write_bytes(original)


if __name__ == "__main__":
    unittest.main()
