#!/usr/bin/env python3
"""Print the six-pass public-source search ladder for a company, in the right language and venues.

Queries are built from three inputs, so no jurisdiction or language is hard-coded here:
  assets/jurisdictions.json  - filing venues, registries and local document names
  assets/search_terms.json   - the search vocabulary per language
  the company name           - detected language when --language is not given

Every pass is emitted twice when the local language is not English: filings are indexed under
their local names, but analyst coverage and cross-border databases are indexed in English.

Usage:
  search_plan.py "小米集团" --jurisdiction hk --year 2025 [--ticker 1810] [--location 北京]
  search_plan.py "Siemens AG" --year 2024            # language and jurisdiction inferred
  search_plan.py "Sony" --language ja --jurisdiction jp --json
"""
import argparse, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import i18n

SKILL = Path(__file__).resolve().parent.parent

# Language-neutral query shapes. {c} company, {y} year, {loc} location, {t} a term key.
PASSES = {
    "1_identity_charter": ["{c} {articles}", "{c} {share_classes_voting}", "{c} {prospectus}", "{c} {registry}"],
    "2_business_economics": ["{c} {y} {annual_report}", "{c} {segment_gross_profit} {y}", "{c} {largest_customer}"],
    "3_workforce_payroll": ["{c} {employees_headcount} {y}", "{c} {rnd_headcount} {y}",
                            "{c} {employee_benefit_expense} {y}", "{c} {share_based_comp} {y}"],
    "4_compensation_equity": ["{c} {equity_incentive_grant} {y}", "{c} {level_system} {salary_total_comp}",
                              "{c} {director_remuneration} {y}", "{c} {executive_comp} {y}",
                              "{c} {job_posting_salary} {loc}"],
    "5_organization_roles": ["{c} {org_structure}", "{c} {business_unit_head}", "{c} {level_system}"],
    "6_career_transitions": ["{c} {promoted_to_vp}", "{c} {appointment} {y}", "{c} {executive_bio}"],
}

STOP_RULES = {
    "1_identity_charter": "stop when legal form, listing venue, share classes and charter status are all evidenced",
    "2_business_economics": "stop when revenue, gross profit and at least one segment profit measure are fetched from the filing itself",
    "3_workforce_payroll": "stop when headcount and the payroll envelope line are read from the statements, not a summary",
    "4_compensation_equity": "stop when you have Tier A grant/remuneration evidence plus at least one independent pay range",
    "5_organization_roles": "stop when the major business units and their leaders are named from official sources",
    "6_career_transitions": "stop at >=8 transitions, or record that the sample is too small for shares",
}


def load_terms(language: str) -> dict:
    data = json.loads((SKILL / 'assets/search_terms.json').read_text(encoding='utf-8'))["terms"]
    en = data["en"]
    tag = i18n.normalize_tag(language)
    for candidate in (tag, i18n.CHROME_ALIASES.get(tag.lower(), ""), tag.split("-")[0]):
        if candidate in data:
            return {"_lang": candidate, **{k: data[candidate].get(k, en[k]) for k in en}}
    return {"_lang": "en", **en}


def build(company, language, jur, year, location, ticker):
    local = load_terms(language)
    english = load_terms("en")
    plan, langs = {}, [local] if local["_lang"] == "en" else [local, english]

    for name, shapes in PASSES.items():
        seen, queries = set(), []
        for terms in langs:
            for shape in shapes:
                q = shape.format(c=f'"{company}"', y=year, loc=location, **terms)
                q = " ".join(q.split())
                if q not in seen:
                    seen.add(q)
                    queries.append(q)
        plan[name] = queries

    venue = []
    for domain in jur.get("filing_venues", []):
        for doc in jur.get("key_documents", [])[:4]:
            venue.append(f'site:{domain} "{company}" {doc}')
    for reg in jur.get("registry", []):
        dom = reg.split(" ")[0]
        venue.append(f'site:{dom} "{company}"' if "." in dom else f'"{company}" {reg}')
    if ticker:
        venue.append(f'"{ticker}" {year} {local["annual_report"]}')
        if local["_lang"] != "en":
            venue.append(f'"{ticker}" {year} annual report')
    if not jur.get("filing_venues"):
        venue.append(f'"{company}" {local["registry"]}  '
                     f'<- no venue mapped for this jurisdiction: find the national registry and regulator first')
    plan["0_venue_specific"] = venue
    return plan, local["_lang"]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('company')
    ap.add_argument('--jurisdiction', default=None, help="registry code or alias; inferred when omitted")
    ap.add_argument('--language', default=None, help="BCP-47 tag; inferred from the company name when omitted")
    ap.add_argument('--ticker', default='')
    ap.add_argument('--year', default='')
    ap.add_argument('--location', default='')
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args()

    lang = i18n.resolve(a.language, a.company)
    jur = i18n.jurisdiction(a.jurisdiction or lang.get("jurisdiction_hint"))
    plan, term_lang = build(a.company, lang["language"], jur, a.year, a.location, a.ticker)

    if a.json:
        print(json.dumps({"company": a.company, "language": lang["language"], "term_language": term_lang,
                          "jurisdiction": jur["code"], "plan": plan}, ensure_ascii=False, indent=1))
        return

    print(f"# search plan: {a.company}")
    print(f"  jurisdiction : {jur['code']} - {jur['name']}")
    print(f"  language     : {lang['language']} ({lang['confidence']}: {lang['signal']})")
    print(f"  query terms  : {term_lang}" + ("" if term_lang == lang["language"]
                                             else "  <- no term set for this language; English terms used"))
    if jur.get("notes"):
        print(f"  note         : {jur['notes']}")
    for key in sorted(plan):
        print(f"\n## {key}")
        for i, q in enumerate(plan[key], 1):
            print(f"  {i:02d}. {q}")
        if key in STOP_RULES:
            print(f"  -> {STOP_RULES[key]}")
    print("\nFetch the primary document in full; a search snippet is never a source. "
          "Log every pass in source_manifest.csv, including sources searched but not found.")


if __name__ == '__main__':
    main()
