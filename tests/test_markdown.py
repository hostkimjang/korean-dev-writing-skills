"""Behavioral regressions for links, scope, language findings and preservation."""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import check_markdown as checker


class MarkdownTests(unittest.TestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def audit(self, base=None):
        return checker.audit(self.root, base=base, require_rules=False)

    def prose(self, text, patterns=None):
        self.write("sample.md", text)
        report = checker.Audit()
        parsed = checker.parse_markdown({"sample.md":text})["sample.md"]
        patterns = patterns or [("DEV-E01",checker.re.compile(checker.PLAIN_ENDING))]
        value = checker.prose_text(self.root,"sample.md",text,parsed,report,patterns)
        return value, report

    def commit(self):
        subprocess.run(["git","init","-q"],cwd=self.root,check=True)
        subprocess.run(["git","add","."],cwd=self.root,check=True)
        subprocess.run(["git","-c","user.name=Fixture","-c","user.email=fixture@example.invalid","commit","-qm","fixture"],cwd=self.root,check=True)
        return subprocess.check_output(["git","rev-parse","HEAD"],cwd=self.root,text=True).strip()

    def kinds(self, report):
        return Counter(f.kind for f in report.findings)

    def test_inline_reference_image_and_encoded_destinations(self):
        self.write("other (copy).md", "# 한국어 안내\n\n## A & B\n")
        self.write("asset.png", "image fixture")
        self.write("README.md", "[참조](<other (copy).md#한국어-안내>)\n\n[상세][reference]\n\n![이미지](asset.png)\n\n[reference]: other%20(copy).md#a--b\n")
        self.assertEqual([], self.audit().findings)

    def test_missing_target_and_fragment_are_separate_failures(self):
        self.write("other.md", "# 존재하는 제목\n")
        self.write("README.md", "[누락](missing.md) [잘못된 절](other.md#missing)\n")
        self.assertEqual({"link":1,"anchor":1}, self.kinds(self.audit()))

    def test_undefined_explicit_reference_is_not_plain_text(self):
        self.write("README.md", "[실제 링크][missing]\n\n[그냥 대괄호 문장]\n")
        findings = self.audit().findings
        self.assertEqual(1,len(findings))
        self.assertIn("Undefined explicit",findings[0].message)

    def test_parenthesis_destination_is_parsed_without_regex_truncation(self):
        self.write("example(v1).md", "# 실행\n")
        self.write("README.md", "[예시](example(v1).md#실행)\n")
        self.assertEqual([],self.audit().findings)

    def test_root_relative_path_and_escape_detection(self):
        self.write("README.md", "# 시작\n")
        self.write("docs/guide.md", "[시작](/README.md#시작) [범위 밖](../../outside.md)\n")
        findings=self.audit().findings
        self.assertEqual(1,len(findings))
        self.assertIn("escapes",findings[0].message)

    def test_setext_formatting_duplicate_headings_and_html_alias(self):
        self.write("README.md", "시작\n====\n\n## **검사** `API`\n\n## 반복\n\n## 반복\n\n<a id=\"old-name\"></a>\n\n[시작](#시작) [형식](#검사-api) [중복](#반복-1) [이전](#old-name)\n")
        self.assertEqual([],self.audit().findings)

    def test_html_href_and_image_sources_checked(self):
        self.write("README.md", '<a id="here"></a>\n\n<a href="#here">이동</a>\n\n<img src="missing.png">\n')
        self.assertEqual({"link":1},self.kinds(self.audit()))

    def test_code_block_links_are_literal_not_real_references(self):
        self.write("README.md", "```markdown\n[예시](not-a-real-file.md#none)\n```\n\n    [명령 출력](also-not-real.md)\n")
        self.assertEqual([],self.audit().findings)

    def test_annotation_example_inside_code_is_not_an_active_exemption(self):
        self.write("README.md", "```html\n<!-- lint:example-start -->\n```\n\n정상적인 본문입니다.\n")
        self.assertEqual([],self.audit().findings)

    def test_fences_inside_ordered_unordered_and_quoted_lists_are_code(self):
        fixtures = (
            "1. ```text\n   본문이다.\n   ```\n",
            "- ```text\n  본문이다.\n  ```\n",
            "> - ```text\n>   본문이다.\n>   ```\n",
            "1. > - ```text\n   >   본문이다.\n   >   ```\n",
        )
        for text in fixtures:
            with self.subTest(text=text):
                self.write("README.md", text)
                self.assertEqual([], self.audit().findings)

    def test_nested_before_tables_exempt_only_the_before_cells(self):
        fixtures = (
            "> | 교정 전 | 교정 후 |\n> | --- | --- |\n> | 저장한다. | 저장합니다. |\n",
            "- first\n\n  | 교정 전 | 교정 후 |\n  | --- | --- |\n  | 저장한다. | 저장합니다. |\n",
            "> - first\n>\n>   | 교정 전 | 교정 후 |\n>   | --- | --- |\n>   | 저장한다. | 저장합니다. |\n",
        )
        for text in fixtures:
            with self.subTest(text=text):
                self.write("README.md", text + "\n설명한다.\n")
                report = self.audit()
                self.assertEqual({"DEV-E01": 1}, self.kinds(report))
                self.assertEqual(1, report.counters["literal_before_cells"])
                self.write("README.md", text.replace("저장합니다.", "저장한다."))
                self.assertEqual({"DEV-E01": 1}, self.kinds(self.audit()))

    def test_resolved_escaped_reference_label_is_not_reported_undefined(self):
        self.write("README.md", "[x][a\\]b]\n\n[a\\]b]: #ok\n\n# ok\n")
        self.assertEqual([], self.audit().findings)
        self.write("README.md", "[x][a\\]b]\n\n# ok\n")
        report = self.audit()
        self.assertEqual({"link": 1}, self.kinds(report))
        self.assertEqual(r"a\]b", report.findings[0].match)

    def test_comment_and_pre_examples_are_not_unresolved_links_or_footnotes(self):
        self.write("README.md", "<!-- [example][missing] -->\n\n<pre>\n[^missing]\n[example][missing]\n</pre>\n")
        self.assertEqual([], self.audit().findings)
        self.write("README.md", "<!-- [example][missing] -->\n\n<pre><a href=\"missing.md\">실제 HTML 링크</a></pre>\n")
        self.assertEqual({"link": 1}, self.kinds(self.audit()))

    def test_footnotes_resolve_and_missing_footnotes_fail(self):
        self.write("README.md", "본문입니다.[^note]\n\n[^note]: 근거입니다.\n")
        self.assertEqual([],self.audit().findings)
        self.write("README.md", "본문입니다.[^missing]\n")
        self.assertEqual({"anchor":1},self.kinds(self.audit()))

    def test_plain_endings_checked_in_inline_korean_but_not_commands(self):
        self.write("README.md", "본문을 확인한다. `내용을 저장한다.`\n\n```text\n출력 원문이다.\n```\n\n정상적으로 저장합니다.\n")
        self.assertEqual({"DEV-E01":2},self.kinds(self.audit()))

    def test_before_table_column_only_is_exempt(self):
        text="| 교정 전 | 교정 후 |\n| --- | --- |\n| 저장한다. | 저장한다. |\n"
        self.write("README.md",text)
        report=self.audit()
        self.assertEqual({"DEV-E01":1},self.kinds(report))
        self.assertEqual(1,report.counters["literal_before_cells"])

    def test_escaped_pipe_inside_code_does_not_shift_before_column(self):
        text="| 교정 전 | 교정 후 |\n| --- | --- |\n| `a|b` 확인한다. | 확인한다. |\n"
        value,report=self.prose(text)
        self.assertEqual(1,len(checker.re.findall(checker.PLAIN_ENDING,value)))
        self.assertEqual(1,report.counters["literal_before_cells"])

    def test_narrow_example_and_mutable_framing_are_separate(self):
        self.write("README.md","도입한다.\n\n<!-- lint:example-start 교정 전 문장 -->\n예시를 저장한다.\n<!-- lint:example-end -->\n\n설명을 계속한다.\n")
        report=self.audit()
        self.assertEqual({"DEV-E01":2},self.kinds(report))
        self.assertEqual(1,report.counters["literal_example_regions"])

    def test_unclosed_unmatched_empty_and_nested_exemptions_fail(self):
        for content in (
            "<!-- lint:example-start 교정 전 -->\n문장이다.\n",
            "<!-- lint:example-end -->\n",
            "<!-- lint:example-start -->\n<!-- lint:example-end -->\n",
            "<!-- lint:example-start 첫 예시 -->\n<!-- lint:example-start 중첩 -->\n<!-- lint:example-end -->\n",
        ):
            with self.subTest(content=content):
                self.write("README.md",content)
                self.assertIn("exemption",self.kinds(self.audit()))

    def test_source_copy_bytes_and_digest_verified(self):
        raw="# 보존 기록\n\n저장했다.\n"
        self.write("evaluations/runs/raw/source.md",raw)
        digest=hashlib.sha256(raw.encode()).hexdigest()
        page=f"# 보고서\n\n<!-- BEGIN SOURCE evaluations/runs/raw/source.md SHA256 {digest} -->\n{raw}<!-- END SOURCE -->\n\n설명합니다.\n"
        self.write("README.md",page)
        self.assertEqual([],self.audit().findings)
        self.write("README.md",page.replace("저장했다.","삭제했다."))
        self.assertIn("integrity",self.kinds(self.audit()))

    def test_links_inside_preserved_source_still_checked(self):
        raw="[실제 손상 링크](missing.md)\n"
        self.write("evaluations/runs/raw/source.md",raw)
        digest=hashlib.sha256(raw.encode()).hexdigest()
        self.write("README.md",f"<!-- BEGIN SOURCE evaluations/runs/raw/source.md SHA256 {digest} -->\n{raw}<!-- END SOURCE -->\n")
        report=self.audit()
        self.assertEqual(2,self.kinds(report)["link"])

    def test_frozen_copied_fragment_is_reported_without_claiming_zero_raw_links(self):
        for key in ("path", "source"):
            relative = checker.FROZEN_REFERENCE[key]
            self.write(relative, (ROOT / relative).read_text())
        report = self.audit()
        self.assertEqual({"archived_reference": 1}, self.kinds(report))
        self.assertEqual(1, report.counters["preserved_broken_copy_references"])
        self.assertEqual(0, report.counters["active_broken_links"])

    def test_frozen_reference_exception_rejects_changed_archive_bytes(self):
        for key in ("path", "source"):
            relative = checker.FROZEN_REFERENCE[key]
            self.write(relative, (ROOT / relative).read_text())
        archive = self.root / checker.FROZEN_REFERENCE["path"]
        archive.write_text(archive.read_text() + "\n")
        report = self.audit()
        self.assertEqual(0, self.kinds(report)["archived_reference"])
        self.assertGreater(self.kinds(report)["anchor"], 0)

    def test_frozen_reference_exception_requires_unchanged_source_and_anchor(self):
        for key in ("path", "source"):
            relative = checker.FROZEN_REFERENCE[key]
            self.write(relative, (ROOT / relative).read_text())
        source = self.root / checker.FROZEN_REFERENCE["source"]
        source.write_text(source.read_text().replace("## 입력 오류 처리", "## 다른 절"))
        report = self.audit()
        self.assertEqual(0, self.kinds(report)["archived_reference"])
        self.assertGreater(self.kinds(report)["anchor"], 0)

    def test_all_files_are_inventoried_including_immutable_history(self):
        self.write("README.md","현재 안내입니다.\n")
        self.write("docs/nested/deep.md","깊은 안내입니다.\n")
        self.write("evaluations/runs/raw/output.md","원문이다.\n")
        self.write("archive/log.md","기록이다.\n")
        report=self.audit()
        self.assertEqual(4,report.counters["markdown_files"])
        self.assertEqual(2,report.counters["immutable_markdown_files"])
        self.assertEqual([],report.findings)
        self.assertEqual(4,len(report.inventory))

    def test_baseline_heading_rename_requires_explicit_alias(self):
        self.write("README.md","# 이전 제목\n\n내용입니다.\n")
        base=self.commit()
        self.write("README.md","# 새 제목\n\n내용입니다.\n")
        self.assertEqual({"legacy_anchor":1},self.kinds(self.audit(base)))
        self.write("README.md",'<a id="이전-제목"></a>\n\n# 새 제목\n\n내용입니다.\n')
        self.assertEqual([],self.audit(base).findings)

    def test_skill_frontmatter_is_not_a_setext_heading(self):
        self.write("SKILL.md", "---\nname: example\ndescription: 원래 안내입니다.\n---\n\n# 안내\n")
        base = self.commit()
        self.write("SKILL.md", "---\nname: example\ndescription: 보완한 안내입니다.\n---\n\n# 안내\n")
        self.assertEqual([], self.audit(base).findings)

    def test_baseline_immutable_history_cannot_be_rewritten(self):
        self.write("archive/result.md","실행했다.\n")
        base=self.commit()
        self.write("archive/result.md","실행했습니다.\n")
        self.assertIn("integrity",self.kinds(self.audit(base)))

    def test_archive_crlf_change_is_detected_and_inventory_hash_uses_raw_bytes(self):
        path = self.write("archive/result.md", "# Result\n\nOriginal record.\n")
        base = self.commit()
        raw = b"# Result\r\n\r\nOriginal record.\r\n"
        path.write_bytes(raw)
        report = self.audit(base)
        self.assertIn("integrity", self.kinds(report))
        self.assertEqual(hashlib.sha256(raw).hexdigest(), report.inventory[0]["sha256"])

    def test_crlf_parser_offsets_preserve_code_and_nested_table_scope(self):
        text = "😀 도입입니다.\r\n\r\n1. ```text\r\n   명령 원문이다.\r\n   ```\r\n\r\n> | 교정 전 | 교정 후 |\r\n> |---|---|\r\n> | 원문이다. | 결과입니다. |\r\n\r\n본문이다.\r\n"
        (self.root / "README.md").write_bytes(text.encode())
        report = self.audit()
        self.assertEqual({"DEV-E01": 1}, self.kinds(report))
        self.assertEqual(1, report.counters["literal_before_cells"])
        self.assertEqual(11, report.findings[0].line)

    def test_source_copy_with_crlf_retains_exact_original_bytes(self):
        raw = b"# Source\r\n\r\nOriginal record.\r\n"
        source = self.root / "archive/source.md"
        source.parent.mkdir()
        source.write_bytes(raw)
        digest = hashlib.sha256(raw).hexdigest()
        page = f"<!-- BEGIN SOURCE archive/source.md SHA256 {digest} -->\r\n".encode() + raw + b"<!-- END SOURCE -->\r\n"
        (self.root / "README.md").write_bytes(page)
        self.assertEqual([], self.audit().findings)

    def test_baseline_command_and_numeric_value_changes_detected(self):
        self.write("README.md","# 실행\n\n포트 8012를 사용합니다.\n\n```bash\nserve --port 8012\n```\n")
        base=self.commit()
        self.write("README.md","# 실행\n\n포트 9012를 사용합니다.\n\n```bash\nserve --port 9012\n```\n")
        report=self.audit(base)
        self.assertGreaterEqual(self.kinds(report)["integrity"],2)

    def test_unrelated_old_archive_cannot_hide_lost_guide_literal(self):
        self.write("README.md","설정은 `API_TOKEN`을 읽습니다.\n")
        self.write("archive/old.md","`API_TOKEN`\n")
        base=self.commit()
        self.write("README.md","설정을 읽습니다.\n")
        self.assertIn("integrity",self.kinds(self.audit(base)))

    def test_inline_command_with_korean_argument_is_preserved(self):
        self.write("README.md", '실행 명령은 `echo "시작"`입니다.\n')
        base = self.commit()
        self.write("README.md", '실행 명령은 `echo "중단"`입니다.\n')
        report = self.audit(base)
        self.assertIn("integrity", self.kinds(report))
        self.assertTrue(any('echo "시작"' in finding.match for finding in report.findings))

    def test_inline_command_output_is_protected_but_korean_examples_are_editable(self):
        self.write("README.md", '출력 명령은 `echo "원문이다."`입니다.\n예문은 `저장한다`입니다.\n')
        base = self.commit()
        self.write("README.md", '출력 명령은 `echo "원문이다."`입니다.\n예문은 `저장합니다`입니다.\n')
        self.assertEqual([], self.audit(base).findings)

    def test_unquoted_environment_variable_and_cli_option_changes_are_detected(self):
        self.write("README.md", "환경 변수 API_TOKEN을 읽고 --output 옵션을 사용합니다.\n")
        base = self.commit()
        self.write("README.md", "환경 변수 SECRET_TOKEN을 읽고 --destination 옵션을 사용합니다.\n")
        report = self.audit(base)
        self.assertEqual(2, self.kinds(report)["integrity"])
        self.assertEqual({"API_TOKEN", "--output"}, {finding.match for finding in report.findings})

    def test_scientific_numeric_literal_change_is_detected(self):
        self.write("README.md", "기준값은 1e6입니다. 오차는 2.5E-3입니다.\n")
        base = self.commit()
        self.write("README.md", "기준값은 2e6입니다. 오차는 2.5E-4입니다.\n")
        report = self.audit(base)
        self.assertEqual(2, self.kinds(report)["integrity"])
        self.assertEqual({"1e6", "2.5E-3"}, {finding.match for finding in report.findings})

    def test_exact_code_can_move_to_explicit_evidence_file(self):
        block="```bash\nserve --port 8012\n```\n"
        self.write("README.md","# 안내\n\n"+block)
        base=self.commit()
        self.write("README.md","# 안내\n\n[실행 기록](docs/evidence/run.md)\n")
        self.write("docs/evidence/run.md","# 실행 기록\n\n"+block)
        self.assertEqual([],self.audit(base).findings)

    def test_historical_example_marker_cannot_relabel_changed_quote(self):
        self.write("README.md","기록을 보관했다.\n")
        base=self.commit()
        self.write("README.md","<!-- lint:example-start 이전 원문 보존 -->\n다른 내용을 보관했다.\n<!-- lint:example-end -->\n")
        self.assertIn("integrity",self.kinds(self.audit(base)))

    def test_unicode_before_code_and_table_does_not_shift_offsets(self):
        self.write("README.md","😀 정상적인 도입입니다.\n\n```text\n명령 원문이다.\n```\n\n| 교정 전 | 교정 후 |\n|---|---|\n| 원문이다. | 결과입니다. |\n\n본문이다.\n")
        self.assertEqual({"DEV-E01":1},self.kinds(self.audit()))

    def test_compression_and_session_terms_do_not_hide_in_backticks(self):
        patterns=[("DEV-S01",checker.re.compile(r"(?:POST|GET)\d{3}|exit\d|(?:행|총|최근)\d|사용자별관리")),
                  ("DEV-C02",checker.re.compile(r"turn_context|model=|blocked by policy"))]
        value,report=self.prose("`v1` `sha256` `fwrun6` `rcfield4` `POST200` `GET401` `exit0` `turn_context`\n",patterns)
        self.assertNotIn("sha256",value)
        self.assertIn("POST200",value)
        self.assertIn("turn_context",value)
        self.assertEqual(3,len(list(patterns[0][1].finditer(value))))

    def test_emphasis_does_not_hide_function_verbs_or_change_error_line(self):
        patterns=[("DEV-A03",checker.re.compile(r"를\s+수행합니다")),
                  ("DEV-C02",checker.re.compile(r"turn_context"))]
        text="첫 문장은 **안내**입니다.\n\n검사를 **수행합니다**.\n\n`turn_context`를 설명합니다.\n"
        value,report=self.prose(text,patterns)
        match=patterns[0][1].search(value)
        self.assertIsNotNone(match)
        self.assertEqual(3,checker.line_at(value,match.start()))
        self.assertIn("turn_context",value)

    def test_real_canonical_rule_mapping_and_required_regressions(self):
        report=checker.Audit()
        config,patterns=checker.load_rules(ROOT,report)
        self.assertEqual([],report.findings)
        self.assertEqual(list(checker.REQUIRED_RULE_IDS),config["rule_ids"])
        for value in ("v1","sha256","fwrun6","rcfield4"):
            self.assertFalse(any(p.search(value) for name,p in patterns if name=="DEV-S01"))

    def test_mapping_failure_when_document_omits_one_checklist_id(self):
        config=json.loads((ROOT/checker.RULE_PATH).read_text())
        self.write(checker.RULE_PATH,json.dumps(config,ensure_ascii=False))
        for relative in checker.RULE_DOCS:
            self.write(relative," ".join(checker.REQUIRED_RULE_IDS)+"\n")
        self.write(checker.RULE_DOCS[-1]," ".join(checker.REQUIRED_RULE_IDS[:-1])+"\n")
        report=checker.Audit()
        checker.load_rules(self.root,report)
        self.assertEqual(1,len(report.findings))
        self.assertEqual("mapping",report.findings[0].kind)

    def test_mapping_failure_when_required_pattern_is_removed(self):
        config=json.loads((ROOT/checker.RULE_PATH).read_text())
        config=deepcopy(config)
        next(rule for rule in config["rules"] if rule["id"]=="DEV-S01")["patterns"]=[r"행\d+"]
        self.write(checker.RULE_PATH,json.dumps(config,ensure_ascii=False))
        for relative in checker.RULE_DOCS:
            self.write(relative," ".join(checker.REQUIRED_RULE_IDS)+"\n")
        report=checker.Audit()
        checker.load_rules(self.root,report)
        self.assertTrue(any("POST200" in f.match for f in report.findings))

    def test_mapping_failure_when_dictionary_entry_disappears(self):
        config=json.loads((ROOT/checker.RULE_PATH).read_text())
        config["translation_coinages"].pop()
        self.write(checker.RULE_PATH,json.dumps(config,ensure_ascii=False))
        for relative in checker.RULE_DOCS:
            self.write(relative," ".join(checker.REQUIRED_RULE_IDS)+"\n")
        report=checker.Audit()
        checker.load_rules(self.root,report)
        self.assertTrue(any("fourteen" in finding.message for finding in report.findings))

    def test_mapping_failure_when_spacing_example_and_detector_diverge(self):
        config=json.loads((ROOT/checker.RULE_PATH).read_text())
        config["spacing_patterns"][0]["examples"][0]["after"]="행19"
        self.write(checker.RULE_PATH,json.dumps(config,ensure_ascii=False))
        for relative in checker.RULE_DOCS:
            self.write(relative," ".join(checker.REQUIRED_RULE_IDS)+"\n")
        report=checker.Audit()
        checker.load_rules(self.root,report)
        self.assertTrue(any("example does not agree" in finding.message for finding in report.findings))


if __name__ == "__main__":
    unittest.main()
