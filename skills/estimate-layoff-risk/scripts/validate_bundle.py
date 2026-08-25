#!/usr/bin/env python3
"""Validate required files and basic invariants in a layoff-risk case bundle."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


REQUIRED = ["case.json", "candidate_answers.json", "public_evidence.jsonl", "source_manifest.csv", "profit_pools.json", "dependency_graph.json", "model.json", "report.json"]


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_bundle.py CASE_DIR", file=sys.stderr)
        return 2
    root = Path(sys.argv[1])
    errors = []
    for name in REQUIRED:
        if not (root / name).is_file():
            errors.append(f"missing {name}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    case = load_json(root / "case.json")
    for key in ["case_alias", "company", "role", "country", "employment_type", "reference_date", "horizons_months"]:
        if key not in case:
            errors.append(f"case.json missing {key}")

    for line_no, line in enumerate((root / "public_evidence.jsonl").read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
            for key in ["claim_id", "claim", "claim_type", "level", "direction", "confidence"]:
                if key not in item:
                    errors.append(f"public_evidence.jsonl line {line_no} missing {key}")
        except json.JSONDecodeError as exc:
            errors.append(f"public_evidence.jsonl line {line_no}: {exc}")

    with (root / "source_manifest.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    expected = ["source_id", "title", "url", "source_type", "tier", "published_date", "accessed_date", "status", "notes"]
    if not rows or rows[0] != expected:
        errors.append("source_manifest.csv header mismatch")

    model = load_json(root / "model.json")
    for horizon, values in model.get("horizons", {}).items():
        for field, tri in values.items():
            if isinstance(tri, dict) and {"low", "mode", "high"}.issubset(tri):
                low, mode, high = tri["low"], tri["mode"], tri["high"]
                if not (0 <= low <= mode <= high <= 1):
                    errors.append(f"model {horizon}.{field} invalid triangular range")

    report = load_json(root / "report.json")
    for key in ["meta", "executive", "company_pressure", "profit_pools", "dependency_graph", "scenarios", "limitations"]:
        if key not in report:
            errors.append(f"report.json missing {key}")

    pdf = root / "report.pdf"
    if pdf.exists():
        content = pdf.read_bytes()
        if len(content) < 1000 or not content.startswith(b"%PDF"):
            errors.append("report.pdf is not a valid-looking PDF")

    if errors:
        print("INVALID")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print("VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
