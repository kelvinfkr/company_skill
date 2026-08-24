#!/usr/bin/env python3
"""Phase gate + next-step instructions. Run after every phase.

Usage: check_phase.py <run_dir> [--phase N] [--next]
  --phase N : verify gate N (default: run['phase_completed']+1); on pass, records phase_completed=N
  --next    : print the exact instructions for the next phase

Gate 1 has one escape hatch, for unlisted entities only: a figure that genuinely is not public can
be declared with a line 'NOT AVAILABLE: <fact> - <what you searched>' in analysis_notes.md. The gate
then passes, the run is flagged provisional, and compile_report.py forces the report's confidence to
the locale's provisional wording. The escape buys an honest label, never a licence to invent a number.
"""
import argparse, csv, json, re, subprocess, sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
S = lambda p: str(SKILL / 'scripts' / p)

# A real unticked item is a list bullet, not the literal characters '[ ]' inside a heading or a
# sentence about checkboxes.
UNTICKED = re.compile(r'^[ \t]*(?:[-*+]|\d+[.)])[ \t]*\[[ \t]\]', re.M)

ESCAPABLE = ("revenue", "gross_profit", "employee_benefit_expense", "headcount")

INSTRUCTIONS = {
0: """PHASE 0 - Resolve entity. Do exactly this:
  1. Read references/company_type_router.md, references/localization.md and references/glossary.md.
  2. Confirm run.json -> language is the language you will write in (it is inferred from the company
     name; if the user wrote to you in another language, theirs wins - fix it now, not at Phase 10).
  3. Confirm run.json -> jurisdiction, currency and threshold. `python {sp} "<company>" --json` shows
     which venues that jurisdiction maps to.
  4. Web-search the annual report, the articles/charter and the listing status in the run language.
  5. Fill run.json -> entity (legal_name, ticker, domicile, listing_venue, company_type, charter_status).
  6. Fill analysis_notes.md 'Phase 0' lines.""",
1: """PHASE 1 - Six-pass search. Do exactly this:
  1. Run: python {sp} "<company>" --jurisdiction <j> --year <FY>   and execute each query, top to bottom.
  2. For every filing found: FETCH the full document (not the snippet). Write one row per document in
     source_manifest.csv with the pass name and status = used | calibration only | searched, not found.
  3. Every number you will use gets one line in evidence.jsonl (fields: id E01.., claim, source,
     published_date, claim_type, source_tier, confidence). claim_type must be observed_fact for
     anything read from a filing.
  4. Fill run.json -> facts (millions), facts_count, segments, each with evidence_id.
  Stop rule: all six passes have at least one non-pending row; facts.revenue, gross_profit,
  employee_benefit_expense and facts_count.headcount are filled.
  UNLISTED ENTITIES: when one of those four genuinely is not public, leave it null and write
  'NOT AVAILABLE: <fact> - <what you searched>' in analysis_notes.md. The gate then passes and marks
  the run provisional. You still need revenue or headcount - without either there is no scale anchor.""",
2: """PHASE 2 - Payroll envelope & profit pools. Do exactly this:
  1. Compute Chain 1 in analysis_notes.md using run.json numbers and assumptions.employer_social_rate.
  2. Rank segments by gross_profit; for the top 3 write Chain 4 lines (process -> role -> dependency -> evidence id).
  3. Add a 'dependency' string to each segment in run.json -> segments.""",
3: """PHASE 3 - Organisation & levels. Do exactly this:
  1. Search the company's level system, org restructurings and business-unit heads (search_plan pass 5).
  2. Write the native level ladder and its band mapping (entry/mid/senior/director/exec) in analysis_notes.md.
  3. Note the organization and talent_pnl rows in analysis_notes.md; they go into report.json after Phase 8.""",
4: """PHASE 4 - Compensation evidence. Do exactly this:
  1. Collect level-pay tables (often Tier E), grant announcements (Tier A), director pay (Tier A).
     Add each to evidence.jsonl. Tier E may calibrate, never carry a headline on its own.
  2. Fill Chain 3 in analysis_notes.md: ageing adjustment, equity annualisation formula, threshold-crossing level.
  3. Fill levels.json: headcount triangle per function (Chain 2), shares per band (defaults.json unless
     evidence says otherwise), tc triangle per band in currency units.""",
5: """PHASE 5 - Build & run the population model. Do exactly this:
  1. python {bm} <run_dir>        (fix any [!!] until it prints OK)
  2. python {ep} <run_dir>/model.json --samples 50000 --json-out <run_dir>/population.json
  3. Write bucket p50 contributions and the affordability check in analysis_notes.md Chain 9.
     If the payroll envelope was not checkable, record the TC/revenue ratio build_model printed
     and say why that level of payroll intensity is plausible for this sector.""",
6: """PHASE 6 - Role pay bands. Do exactly this:
  1. Fill pay_bands.json for 3-7 critical roles (from Chain 4) with market/economic/internal [low, high]
     in currency units. economic = pool_at_risk x dependency_factor(defaults.json) / expected_tenure_years,
     capped by operating profit.
  2. python {pd} <run_dir>/pay_bands.json  -> copy diagnostics into report.json -> role_pay after Phase 8.""",
7: """PHASE 7 - Career graph. Do exactly this:
  1. Search executive bios and appointment announcements; add >=8 rows to career_transitions.csv.
  2. python {cg} <run_dir>/career_transitions.csv
  3. If any origin state has n < 10, write the paths qualitatively; never print a percentage as a
     promotion probability.""",
8: """PHASE 8 - Charter & equity. Do exactly this:
  1. From Pass 1/4 documents fill Chain 7 in analysis_notes.md.
  2. python {cr} <run_dir>   -> report.json now has all numeric sections, in the run language.
  3. Fill every TODO in report.json prose sections (charter.summary/timeline, talent_pnl, organization,
     role_pay, career, governance, sensitivity, evidence). Write them in run.json -> language.
     For claim types use the canonical keys observed_fact / derived_metric / assumption / inference /
     reconstruction, or this locale's labels; render_report.py localises them either way.""",
9: """PHASE 9 - Cross-checks. Do exactly this:
  1. python {vb} <run_dir> --benefit-expense <E> --sbc <S> --tc-total <run.json checks.modelled_tc_total_million>
     (omit --benefit-expense when it was never disclosed; the bundle checks still run)
  2. Compare modelled >=first-equity-level headcount with facts_count.equity_award_holders; write the
     deviation in Chain 9.
  3. If any deviation > 10%: revise levels.json, rerun Phase 5, rerun compile_report.py.
  4. Fill Chain 8 sensitivity lines and report.json -> sensitivity.""",
10: """PHASE 10 - Render & deliver. Do exactly this:
  1. python {rr} <run_dir>/report.json -o <run_dir>/report.pdf
  2. Open the PDF (or rasterise pages) and check: no clipped tables, no tofu boxes in the report's
     script, no orphaned headings, page numbers present.
  3. Tick every line in CHECKLIST.md. Present report.pdf to the user, then the bundle path.
     Speak to the user in the run language.""",
}


def unticked(text: str) -> list:
    return UNTICKED.findall(text or "")


def is_unlisted(run: dict) -> bool:
    ent = run.get('entity', {})
    if ent.get('listing_venue'):
        return False
    ctype = (ent.get('company_type') or '').lower()
    if run.get('jurisdiction') == 'private':
        return True
    return (not ent.get('ticker')) or any(w in ctype for w in
                                          ('private', 'unlisted', 'llc', 'gmbh', '非上市', '未上市', '有限责任'))


def declared_unavailable(notes: str, key: str) -> bool:
    """True when analysis_notes.md declares this fact unavailable AND says what was searched."""
    for line in (notes or "").splitlines():
        if 'NOT AVAILABLE' in line.upper() and key in line:
            rest = line.split(':', 1)[1] if ':' in line else ''
            return len(rest.replace(key, '').strip(' -—\t')) >= 12
    return False


def gate(d, n):
    run = json.loads((d / 'run.json').read_text(encoding='utf-8'))
    problems = []
    ev = ([json.loads(l) for l in (d / 'evidence.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()]
          if (d / 'evidence.jsonl').exists() else [])
    notes = (d / 'analysis_notes.md').read_text(encoding='utf-8') if (d / 'analysis_notes.md').exists() else ''

    def notes_filled(section):
        for block in notes.split('## '):
            if block.startswith(section):
                return not unticked(block)
        return False

    if n == 0:
        for k in ('legal_name', 'company_type', 'charter_status'):
            if not run['entity'].get(k):
                problems.append(f"run.json entity.{k} empty")
        if not run.get('language'):
            problems.append("run.json language empty: set the language the report will be written in")
        if not notes_filled('Phase 0'):
            problems.append("analysis_notes.md Phase 0 has unfilled [ ] lines")

    if n == 1:
        with open(d / 'source_manifest.csv', newline='', encoding='utf-8') as f:
            rows = list(csv.DictReader(f))
        for ps in ["1_identity_charter", "2_business_economics", "3_workforce_payroll",
                   "4_compensation_equity", "5_organization_roles", "6_career_transitions"]:
            if not any(r['pass'] == ps and r['status'] != 'pending' for r in rows):
                problems.append(f"manifest: pass {ps} still pending")

        unlisted, escaped = is_unlisted(run), []
        present = {k: (run['facts'][k]['value'] if k in run['facts'] else run['facts_count'][k]['value'])
                   for k in ESCAPABLE}
        for k, v in present.items():
            if v is not None:
                continue
            where = 'facts' if k in run['facts'] else 'facts_count'
            if unlisted and declared_unavailable(notes, k):
                escaped.append(k)
            elif unlisted:
                problems.append(
                    f"{where}.{k} missing: for an unlisted entity, either fill it or write "
                    f"'NOT AVAILABLE: {k} - <what you searched>' in analysis_notes.md")
            else:
                problems.append(f"{where}.{k} missing")
        if escaped and present['revenue'] is None and present['headcount'] is None:
            problems.append("both revenue and headcount are unavailable: there is no scale anchor, so no "
                            "company-wide distribution may be produced. Deliver a provisional map and an "
                            "evidence wanted-list instead of running Phase 5.")

        observed = [e for e in ev if e.get('claim_type') == 'observed_fact']
        strong = [e for e in observed if e.get('source_tier') in ('A', 'B')]
        if not observed:
            problems.append("evidence.jsonl has no observed_fact entries")
        elif not strong:
            if unlisted:
                escaped.append("no Tier A/B source")
            else:
                problems.append("evidence.jsonl has no Tier A/B observed_fact")
        for k, v in list(run['facts'].items()) + list(run['facts_count'].items()):
            if v['value'] is not None and not v.get('evidence_id'):
                problems.append(f"{k} filled without evidence_id")

        if not problems and escaped:
            run['provisional'] = True
            run['provisional_facts'] = sorted(set(run.get('provisional_facts', []) + escaped))

    if n == 2:
        if not notes_filled('Chain 1'):
            problems.append("Chain 1 not filled")
        if not notes_filled('Chain 4'):
            problems.append("Chain 4 not filled")
        if not any(s.get('dependency') for s in run['segments']):
            problems.append("segments lack dependency strings")

    if n == 3 and 'level' not in notes.lower():
        problems.append("no level ladder written in analysis_notes.md")

    if n == 4:
        if not notes_filled('Chain 3'):
            problems.append("Chain 3 not filled")
        lv = json.loads((d / 'levels.json').read_text(encoding='utf-8'))
        if (any(t[k] is None for fn in lv['functions'] for t in fn['tc'] for k in t)
                or any(fn['headcount'][k] is None for fn in lv['functions'] for k in fn['headcount'])):
            problems.append("levels.json has null values")

    if n == 5:
        if not (d / 'population.json').exists():
            problems.append("population.json missing (run estimate_population.py)")
        checks = run.get('checks', {})
        kind = checks.get('envelope_check')
        if kind is None:
            problems.append("build_model.py not run (no affordability check recorded)")
        elif kind == 'payroll_envelope':
            dev = checks.get('payroll_envelope_deviation')
            if dev is None:
                problems.append("payroll envelope check incomplete: rerun build_model.py")
            elif abs(dev) > 0.10:
                problems.append(f"payroll envelope deviation {dev:+.1%} > 10%")
        elif kind == 'tc_over_revenue':
            ratio = checks.get('tc_total_over_revenue')
            if ratio is None:
                problems.append("substitute affordability check incomplete: rerun build_model.py")
            elif ratio > 1.0:
                problems.append(f"modelled TC total is {ratio:.0%} of revenue: impossible, revise levels.json")
            elif ratio > 0.6 and 'payroll' not in notes.lower() and 'TC/revenue' not in notes:
                problems.append(f"modelled TC total is {ratio:.0%} of revenue: justify that payroll intensity "
                                f"in analysis_notes.md Chain 9 or revise levels.json")
        elif kind == 'none':
            if not run.get('provisional'):
                problems.append("no affordability check was possible and the run is not marked provisional")

    if n == 6:
        pbj = json.loads((d / 'pay_bands.json').read_text(encoding='utf-8'))
        if (len([r for r in pbj['roles'] if r.get('role')]) < 3
                or any(x is None for r in pbj['roles'] for k in ('market', 'economic', 'internal') for x in r[k])):
            problems.append("pay_bands.json needs >=3 complete roles")

    if n == 7:
        with open(d / 'career_transitions.csv', newline='', encoding='utf-8') as f:
            rows = list(csv.DictReader(f))
        if len(rows) < 8:
            problems.append(f"career_transitions.csv has {len(rows)} rows, need >=8")

    if n == 8:
        if not (d / 'report.json').exists():
            problems.append("report.json missing (run compile_report.py)")
        else:
            txt = (d / 'report.json').read_text(encoding='utf-8')
            if 'TODO' in txt:
                problems.append(f"report.json still has {txt.count('TODO')} TODO fields")
            if '"constitution"' in txt:
                problems.append("report.json uses key 'constitution'; use 'charter'")
            rj = json.loads(txt)
            if not rj.get('meta', {}).get('language'):
                problems.append("report.json meta.language missing (rerun compile_report.py)")
        if not notes_filled('Chain 7'):
            problems.append("Chain 7 not filled")

    if n == 9:
        if not notes_filled('Chain 8') or not notes_filled('Chain 9'):
            problems.append("Chain 8/9 not filled")
        r = subprocess.run([sys.executable, S('validate_bundle.py'), str(d)], capture_output=True, text=True)
        if r.returncode != 0:
            problems.append("validate_bundle.py failed:\n" + r.stdout)

    if n == 10:
        if not (d / 'report.pdf').exists():
            problems.append("report.pdf missing")
        left = unticked((d / 'CHECKLIST.md').read_text(encoding='utf-8'))
        if left:
            problems.append(f"CHECKLIST.md has {len(left)} unticked items")

    return run, problems


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('run_dir')
    ap.add_argument('--phase', type=int)
    ap.add_argument('--next', action='store_true')
    a = ap.parse_args()
    d = Path(a.run_dir)
    run = json.loads((d / 'run.json').read_text(encoding='utf-8'))
    fmt = dict(sp=S('search_plan.py'), bm=S('build_model.py'), ep=S('estimate_population.py'),
               pd=S('pay_band_diagnostic.py'), cg=S('career_graph.py'), cr=S('compile_report.py'),
               vb=S('validate_bundle.py'), rr=S('render_report.py'))

    if a.next and a.phase is None:
        nxt = (run['phase_completed'] if run['phase_completed'] == 0 and not run['entity'].get('company_type')
               else run['phase_completed'] + 1)
        print(INSTRUCTIONS[min(nxt, 10)].format(**fmt))
        return

    n = a.phase if a.phase is not None else run['phase_completed'] + 1
    run, problems = gate(d, n)
    if problems:
        print(f"PHASE {n} GATE FAILED:\n" + '\n'.join('  [!!] ' + x for x in problems))
        print("\nFix these, then rerun. Instructions:\n" + INSTRUCTIONS[n].format(**fmt))
        sys.exit(1)
    run['phase_completed'] = max(run['phase_completed'], n)
    (d / 'run.json').write_text(json.dumps(run, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f"PHASE {n} GATE PASSED.")
    if run.get('provisional'):
        print(f"  [provisional] {', '.join(run.get('provisional_facts', []))} not public. "
              f"The report must be labelled a provisional estimate; compile_report.py enforces it.")
    if n < 10:
        print("\nNEXT:\n" + INSTRUCTIONS[n + 1].format(**fmt))


if __name__ == '__main__':
    main()
