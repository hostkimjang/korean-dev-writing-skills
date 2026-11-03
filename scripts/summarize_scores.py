#!/usr/bin/env python3
"""Validate two frozen blind reviews and produce descriptive summary metrics.

The script does not generate scores. It requires every judge to cover every
anonymous output and preserves judge disagreement. Scores are ordinal rubric
ratings, not calibrated probabilities or a percentage quality improvement.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean


DIMENSIONS = ("factual_accuracy", "information_completeness", "audience_purpose_structure", "korean_naturalness", "actionability_format")
ARMS = ("baseline", "original", "revised")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", default="2026-11-03")
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    run = repo / "evaluations/runs" / args.run
    if not run.resolve().is_relative_to((repo / "evaluations/runs").resolve()):
        raise SystemExit("Run path must stay inside evaluations/runs.")
    labels = json.loads((run / "label-map.json").read_text(encoding="utf-8"))["labels"]
    lookup = {x["output_id"]: x for x in labels}
    expected = {(x["case_id"], x["output_id"]) for x in labels}
    if len(expected) != 18:
        raise SystemExit("Expected 18 unique outputs.")
    review_paths = sorted((run / "reviews").glob("judge-*.json"))
    if len(review_paths) != 2:
        raise SystemExit("Expected exactly two frozen blind judge files.")
    reviews = []
    flat = []
    for path in review_paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        records = data["records"]
        actual = {(x["case_id"], x["output_id"]) for x in records}
        if len(records) != 18 or actual != expected:
            raise SystemExit(f"Incomplete or duplicate review: {path.name}")
        for record in records:
            scores = record["dimension_scores"]
            if set(scores) != set(DIMENSIONS) or any(type(v) is not int or not 0 <= v <= 4 for v in scores.values()):
                raise SystemExit(f"Invalid dimension scores: {path.name} {record['output_id']}")
            if sum(scores.values()) != record["total_score"]:
                raise SystemExit(f"Arithmetic mismatch: {path.name} {record['output_id']}")
            if type(record["hard_fail"]) is not bool:
                raise SystemExit("hard_fail must be a boolean.")
            if record["hard_fail"] and not record.get("hard_fail_evidence"):
                raise SystemExit("hard_fail requires explicit evidence.")
            if not record.get("dimension_evidence"):
                raise SystemExit("Each score record needs evidence.")
            flat.append({**record, "condition": lookup[record["output_id"]]["condition"], "judge_file": path.name})
        reviews.append({"file": path.name, "reviewer": data.get("reviewer"), "record_count": len(records)})
    summary = {"run_id": args.run, "reviewers": reviews, "scale": {"dimension_max": 4, "total_max": 20}, "conditions": {}, "cases": []}
    for arm in ARMS:
        rows = [x for x in flat if x["condition"] == arm]
        summary["conditions"][arm] = {
            "documents": 6, "ratings": len(rows),
            "mean_total": mean(x["total_score"] for x in rows),
            "mean_dimensions": {d: mean(x["dimension_scores"][d] for x in rows) for d in DIMENSIONS},
            "hard_fail_ratings": sum(x["hard_fail"] for x in rows),
            "documents_flagged_by_any_judge": len({x["case_id"] for x in rows if x["hard_fail"]}),
        }
    for case_id in dict.fromkeys(x["case_id"] for x in labels):
        case = {"case_id": case_id, "conditions": {}}
        for arm in ARMS:
            rows = [x for x in flat if x["condition"] == arm and x["case_id"] == case_id]
            case["conditions"][arm] = {"mean_total": mean(x["total_score"] for x in rows), "judge_totals": [x["total_score"] for x in rows], "hard_fail_flags": [x["hard_fail"] for x in rows]}
        case["revised_minus_baseline"] = case["conditions"]["revised"]["mean_total"] - case["conditions"]["baseline"]["mean_total"]
        case["revised_minus_original"] = case["conditions"]["revised"]["mean_total"] - case["conditions"]["original"]["mean_total"]
        summary["cases"].append(case)
    summary["interpretation_limit"] = "One run, six synthetic paired cases, two model judges sharing a model family. Descriptive ordinal scores; no statistical significance or cross-model efficacy claim."
    destination = run / "summary.json"
    destination.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"conditions": summary["conditions"], "cases": summary["cases"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
