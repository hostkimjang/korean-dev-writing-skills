#!/usr/bin/env python3
"""Prepare a reproducible review packet after all raw outputs exist.

This does not call models or score documents. Give judges only review-packet.json;
keep label-map.json and this command's seed out of their context until scoring is
saved. Raw generated text is copied byte-for-byte after UTF-8 decoding.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import random


ARMS = ("baseline", "original", "revised")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", default="2026-11-03")
    parser.add_argument("--seed", type=int, required=True)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    run = repo / "evaluations" / "runs" / args.run
    if not run.resolve().is_relative_to((repo / "evaluations/runs").resolve()):
        raise SystemExit("Run path must stay inside evaluations/runs.")
    cases = sorted((repo / "evaluations/cases").glob("*.json"))
    if len(cases) != 6:
        raise SystemExit("This protocol expects six cases.")
    output_paths = [run / "outputs" / arm / f"{case.stem}.md" for case in cases for arm in ARMS]
    missing = [str(p.relative_to(repo)) for p in output_paths if not p.is_file() or not p.read_text(encoding="utf-8").strip()]
    if missing:
        raise SystemExit("Missing complete outputs:\n" + "\n".join(missing))
    packet_path = run / "review-packet.json"
    mapping_path = run / "label-map.json"
    if packet_path.exists() or mapping_path.exists():
        raise SystemExit("Review packet already exists; preserve the frozen packet or use a new run.")
    rng = random.Random(args.seed)
    packet = {"rubric": json.loads((repo / "evaluations/rubric.json").read_text(encoding="utf-8")), "cases": []}
    mapping = {"seed": args.seed, "run": args.run, "labels": []}
    used_labels: set[str] = set()
    for case_path in cases:
        case = json.loads(case_path.read_text(encoding="utf-8"))
        candidates = []
        order = list(ARMS)
        rng.shuffle(order)
        for arm in order:
            path = run / "outputs" / arm / f"{case_path.stem}.md"
            raw = path.read_bytes()
            label = f"doc-{rng.getrandbits(32):08x}"
            while label in used_labels:
                label = f"doc-{rng.getrandbits(32):08x}"
            used_labels.add(label)
            candidates.append({"output_id": label, "text": raw.decode("utf-8")})
            mapping["labels"].append({
                "case_id": case["case_id"], "case_file": case_path.name,
                "output_id": label, "condition": arm,
                "output_file": str(path.relative_to(run)),
                "sha256": hashlib.sha256(raw).hexdigest(), "characters": len(raw.decode("utf-8")),
            })
        packet["cases"].append({"case": case, "candidates": candidates})
    packet_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    mapping_path.write_text(json.dumps(mapping, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Created {packet_path.relative_to(repo)} with 18 unchanged outputs.")
    print("Keep label-map.json private from judges until their evaluations are saved.")


if __name__ == "__main__":
    main()
