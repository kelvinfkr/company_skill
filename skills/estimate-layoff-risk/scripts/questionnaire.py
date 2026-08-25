#!/usr/bin/env python3
"""Select core and adaptive interview questions from the bundled bank."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("case")
    parser.add_argument("-o", "--output")
    args = parser.parse_args()

    case = json.loads(Path(args.case).read_text(encoding="utf-8"))
    bank_path = Path(__file__).resolve().parents[1] / "assets" / "question_bank.json"
    bank = json.loads(bank_path.read_text(encoding="utf-8"))
    employment = case.get("employment_type", "employee")
    role = case.get("role_family", "general")
    if role == "operations":
        role = "general"
    questions = list(bank["core"])
    questions.extend(bank.get("employment", {}).get(employment, []))
    questions.extend(bank.get("roles", {}).get(role, bank["roles"]["general"]))
    payload = {
        "case_alias": case.get("case_alias", "candidate"),
        "employment_type": employment,
        "role_family": case.get("role_family", "general"),
        "instructions": "Ask in two short rounds. Accept unknown or prefer_not_to_answer. Record date, provenance, confidence, and report consent.",
        "questions": questions
    }
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
