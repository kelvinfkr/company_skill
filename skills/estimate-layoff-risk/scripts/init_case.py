#!/usr/bin/env python3
"""Initialize an auditable layoff-risk case directory."""
from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--company", required=True)
    parser.add_argument("--role", required=True)
    parser.add_argument("--country", required=True)
    parser.add_argument("--employment-type", default="employee", choices=["employee", "intern", "probation", "fixed_term", "contractor"])
    parser.add_argument("--role-family", default="general", choices=["product", "sales", "engineering", "research", "manufacturing", "operations", "services", "corporate", "public_service", "general"])
    parser.add_argument("--alias", default="candidate")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    today = date.today().isoformat()
    case = {
        "case_alias": args.alias,
        "company": args.company,
        "legal_employer": "",
        "parent_company": "",
        "business_unit": "",
        "product": "",
        "role": args.role,
        "role_family": args.role_family,
        "country": args.country,
        "worksite": "",
        "employment_type": args.employment_type,
        "company_type": "",
        "reference_date": today,
        "horizons_months": [3, 6, 12],
        "outcomes": ["structural_layoff", "contract_or_nonrenewal", "performance_exit", "redeployment", "any_involuntary_exit"]
    }
    write_json(out / "case.json", case)
    write_json(out / "candidate_answers.json", {"case_alias": args.alias, "answers": []})
    (out / "public_evidence.jsonl").write_text("", encoding="utf-8")
    with (out / "source_manifest.csv").open("w", newline="", encoding="utf-8") as handle:
        csv.writer(handle).writerow(["source_id", "title", "url", "source_type", "tier", "published_date", "accessed_date", "status", "notes"])
    write_json(out / "profit_pools.json", {"company": args.company, "profit_pools": []})
    write_json(out / "dependency_graph.json", {"nodes": [], "edges": []})
    write_json(out / "model.json", {"calibration_status": "scenario_only", "confidence": "low", "horizons": {}})
    write_json(out / "report.json", {"meta": case, "executive": {}, "company_pressure": {}, "profit_pools": [], "dependency_graph": [], "scenarios": [], "limitations": []})
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
