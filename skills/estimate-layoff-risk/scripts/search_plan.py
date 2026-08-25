#!/usr/bin/env python3
"""Generate a company-, role-, and jurisdiction-aware public search plan."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


LOCAL_TERMS = {
    "china": ["裁员", "人员优化", "组织调整", "降本增效", "不续签", "业务收缩"],
    "united states": ["WARN notice", "reduction in force", "RIF", "position elimination", "facility closure"],
    "germany": ["Stellenabbau", "Massenentlassungsanzeige", "Betriebsrat", "Sozialplan", "Standortschließung"],
    "japan": ["人員削減", "希望退職", "早期退職", "事業再編", "雇い止め"],
    "united kingdom": ["redundancy consultation", "collective redundancy", "role at risk", "site closure"]
}


def q(*parts: str) -> str:
    return " ".join(f'"{part}"' if " " in part else part for part in parts if part)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("case")
    parser.add_argument("-o", "--output")
    args = parser.parse_args()
    case = json.loads(Path(args.case).read_text(encoding="utf-8"))
    company = case.get("company", "")
    bu = case.get("business_unit", "")
    product = case.get("product", "")
    site = case.get("worksite", "")
    role = case.get("role", "")
    country = case.get("country", "").strip().lower()
    local = LOCAL_TERMS.get(country, ["layoff", "restructuring", "non-renewal", "workforce reduction"])
    context = [company, bu, product, site]
    passes = [
        {"id": 1, "name": "entity_scope", "queries": [q(company, "legal entity subsidiaries business unit"), q(company, product, "owner organization")]},
        {"id": 2, "name": "solvency_financing", "queries": [q(company, "cash flow debt maturity covenant financing"), q(company, "working capital capex liquidity")]},
        {"id": 3, "name": "profit_pools", "queries": [q(company, bu, "segment revenue gross profit operating profit"), q(company, product, "sales orders margin market share inventory")]},
        {"id": 4, "name": "management_targets", "queries": [q(company, "restructuring severance cost savings productivity margin target"), q(company, "synergy shared services delayering footprint optimization")]},
        {"id": 5, "name": "product_lifecycle", "queries": [q(product or bu or company, "roadmap launch discontinued strategic review"), q(company, bu, "executive departure investment customer contract")]},
        {"id": 6, "name": "workforce_demand", "queries": [q(company, role, "jobs careers hiring freeze outsourcing automation"), q(company, site, "office factory closure relocation headcount")]},
        {"id": 7, "name": "leadership_allocation", "queries": [q(company, "CEO CFO interview capital allocation headcount"), q(company, "previous restructuring which departments")]},
        {"id": 8, "name": "contradictions_base_rates", "queries": [q(company, bu, role, "hiring expansion new budget"), q(company, product, "new contract launch investment"), q(company, "layoff history workforce")]}]
    passes.append({"id": 9, "name": "local_notice_terms", "queries": [q(*(context + [term])) for term in local]})
    payload = {"case_alias": case.get("case_alias", "candidate"), "reference_date": case.get("reference_date", ""), "passes": passes, "source_priority": ["regulator/government", "audited filing", "official company", "credible independent media", "aggregate labor/recruiting data", "anonymous leads"]}
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
