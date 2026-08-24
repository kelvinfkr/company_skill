#!/usr/bin/env python3
"""Create a run directory with every template pre-filled, in the right language and jurisdiction.

Usage:
  init_run.py "<company>" --out <dir> --year <FY> [--jurisdiction <code>] [--language <tag>]
              [--threshold <amount>] [--currency <ISO>]

Language: resolved from the company name unless --language (or $CTE_LANG) is given, so
"init_run.py '小米集团'" produces a Chinese run and "init_run.py 'Siemens AG'" a German one.
Jurisdiction: any code or alias in assets/jurisdictions.json ('us', 'japan', 'hkex', ...);
inferred from the company name when omitted. Currency, high-pay threshold and employer social
rate default to that jurisdiction's priors and are always overridable.
"""
import argparse, csv, json, shutil, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import i18n

SKILL = Path(__file__).resolve().parent.parent

PASSES = ["1_identity_charter", "2_business_economics", "3_workforce_payroll",
          "4_compensation_equity", "5_organization_roles", "6_career_transitions"]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('company')
    ap.add_argument('--out', required=True)
    ap.add_argument('--year', required=True)
    ap.add_argument('--jurisdiction', default=None,
                    help="registry code or alias; run `i18n.py jurisdictions` for the list")
    ap.add_argument('--language', default=None, help="BCP-47 tag; default: inferred from the company name")
    ap.add_argument('--threshold', type=float, default=None)
    ap.add_argument('--currency', default=None)
    a = ap.parse_args()

    lang = i18n.resolve(a.language, a.company)
    jcode = a.jurisdiction or lang.get("jurisdiction_hint") or "other"
    jur = i18n.jurisdiction(jcode)
    if a.jurisdiction and jur["code"] == "other" and str(a.jurisdiction).lower() not in ("other", ""):
        print(f"[!!] jurisdiction '{a.jurisdiction}' is not in assets/jurisdictions.json; using 'other'. "
              f"Add it there once you have located its filing venues.")

    currency = a.currency or jur.get("currency")
    threshold = a.threshold if a.threshold is not None else jur.get("threshold_default")
    d = json.loads((SKILL / 'assets/defaults.json').read_text(encoding='utf-8'))
    social = jur.get("employer_social_rate")
    if social is None:
        social = d["employer_social_rate"].get(jur["code"], d["employer_social_rate"]["other"])

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    unit = f"{currency}_million" if currency else "million"

    run = {
        "company": a.company,
        "language": lang["language"],
        "language_confidence": lang["confidence"],
        "language_signal": lang["signal"],
        "chrome_locale": lang["chrome"],
        "jurisdiction": jur["code"],
        "jurisdiction_name": jur["name"],
        "fiscal_year": a.year,
        "reference_date": f"{a.year}-12-31",
        "currency": currency,
        "threshold": threshold,
        "phase_completed": 0,
        "provisional": False,
        "provisional_facts": [],
        "entity": {"legal_name": "", "ticker": "", "domicile": "", "listing_venue": "",
                   "company_type": "", "charter_status": ""},
        "facts": {k: {"value": None, "unit": unit, "evidence_id": ""} for k in
                  ["revenue", "gross_profit", "operating_profit", "net_profit", "rnd_expense",
                   "sales_expense", "admin_expense", "employee_benefit_expense", "sbc_expense",
                   "cash_paid_to_employees"]},
        "facts_count": {k: {"value": None, "evidence_id": ""} for k in
                        ["headcount", "domestic_headcount", "overseas_headcount", "rnd_headcount",
                         "equity_award_holders", "person_grants_last_12m"]},
        "segments": [{"name": "", "revenue": None, "gross_profit": None, "growth_pct": None, "evidence_id": ""}],
        "assumptions": {"employer_social_rate": social,
                        "equity_vesting_years": d["equity_vesting_years"],
                        "equity_price_basis": d["equity_price_basis"]},
        "_instructions": (
            "Write the report and all prose in run.language. Fill facts from fetched Tier A/B documents only; "
            "amounts in millions of the reporting currency. If a fact is genuinely not public, leave value null "
            "and write a line 'NOT AVAILABLE: <fact> - <what you searched>' in analysis_notes.md; for an unlisted "
            "entity that satisfies the Phase 1 gate and marks the run provisional."),
    }
    if threshold is None:
        run["_instructions"] += (
            f" No default high-pay threshold exists for '{jur['code']}': set run.threshold and run.currency "
            "explicitly (state the FX date if you convert) before Phase 5.")
    (out / 'run.json').write_text(json.dumps(run, ensure_ascii=False, indent=1), encoding='utf-8')

    notes = (SKILL / 'assets/analysis_notes_template.md').read_text(encoding='utf-8')
    notes = (notes.replace('{company}', a.company).replace('{year}', a.year)
                  .replace('{language}', lang["language"]).replace('{jurisdiction}', jur["name"]))
    (out / 'analysis_notes.md').write_text(notes, encoding='utf-8')
    shutil.copy(SKILL / 'assets/CHECKLIST.md', out / 'CHECKLIST.md')

    with open(out / 'source_manifest.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(["pass", "source", "url", "date", "source_type", "tier", "status"])
        for p in PASSES:
            w.writerow([p, "", "", "", "", "", "pending"])
    (out / 'evidence.jsonl').write_text('', encoding='utf-8')
    with open(out / 'career_transitions.csv', 'w', newline='', encoding='utf-8') as f:
        csv.writer(f).writerow(["from_state", "to_state", "transition_type", "months", "evidence_tier", "note"])

    levels = {
        "tc_uncertainty_pct": 0.15,
        "_doc": ("tc_uncertainty_pct = epistemic +/-% applied to each tc triangle to widen p_exceed. One entry "
                 "per function. Optional per band: cash / equity display strings. share = fraction of that "
                 "function's headcount in the band; tc = annual pre-tax TC triangle in reporting currency units "
                 "(not millions). Bands must be listed entry->exec. Use defaults.json pyramid shares if no "
                 "better evidence exists."),
        "functions": [
            {"name": "R&D", "headcount": {"low": None, "mode": None, "high": None},
             "native_bands": ["entry", "mid", "senior", "director", "exec"],
             "shares": d["pyramid_share_by_band"]["R&D"],
             "tc": [{"low": None, "mode": None, "high": None} for _ in range(5)]},
            {"name": "Non-R&D professional", "headcount": {"low": None, "mode": None, "high": None},
             "native_bands": ["entry", "mid", "senior", "director", "exec"],
             "shares": d["pyramid_share_by_band"]["Non-R&D professional"],
             "tc": [{"low": None, "mode": None, "high": None} for _ in range(5)]},
            {"name": "Frontline", "headcount": {"low": None, "mode": None, "high": None},
             "native_bands": ["frontline"], "shares": [1.0],
             "tc": [{"low": None, "mode": None, "high": None}]},
            {"name": "Overseas", "headcount": {"low": None, "mode": None, "high": None},
             "native_bands": ["mixed"], "shares": [1.0],
             "tc": [{"low": None, "mode": None, "high": None}]},
        ]}
    (out / 'levels.json').write_text(json.dumps(levels, ensure_ascii=False, indent=1), encoding='utf-8')
    (out / 'pay_bands.json').write_text(json.dumps(
        {"roles": [{"role": "", "market": [None, None], "economic": [None, None], "internal": [None, None]}]},
        ensure_ascii=False, indent=1), encoding='utf-8')

    fb = " (chrome falls back to English; prose stays in this language)" if lang["chrome_is_fallback"] else ""
    print(f"Initialised {out}")
    print(f"  language     {lang['language']}{fb}  [{lang['confidence']}: {lang['signal']}]")
    print(f"  jurisdiction {jur['code']} - {jur['name']}")
    print(f"  currency     {currency or 'NOT SET - choose one and state the FX date'}"
          f"   threshold {threshold if threshold is not None else 'NOT SET - required before Phase 5'}")
    print(f"  social rate  {social:.0%} (prior; override with a disclosed number)")
    if lang["confidence"] in ("low", "ambiguous", "none"):
        print(f"  [!!] language is a guess. Write in the language the user used, or rerun with --language <tag>.")
    if jur.get("notes"):
        print(f"  note: {jur['notes']}")
    print(f"\nNext: python {SKILL / 'scripts/check_phase.py'} {out} --next")


if __name__ == '__main__':
    main()
