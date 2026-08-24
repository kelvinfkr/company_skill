#!/usr/bin/env python3
"""Fill the numeric sections of report.json from run.json, model.json and population.json.

Usage: compile_report.py <run_dir> [--language <tag>]

Writes/updates: meta, executive.metrics, business.metrics, business.profit_pools, compensation,
high_compensation. Prose sections (executive.diagnosis, charter, talent_pnl, organization, role_pay,
career, governance, sensitivity, evidence) are kept if present, otherwise created with TODO markers.

Everything numeric is labelled and formatted in the run's language: metric names come from the
locale pack, and amounts are scaled the way that language actually says them (1.2 亿 / 120M / 1,2 Mrd.).
Claim types are written as canonical English keys (observed_fact, derived_metric, ...) so validation
is language-independent; render_report.py turns them into local labels.

When run.provisional is set - an unlisted entity where a required public figure genuinely does not
exist - meta.confidence is forced to the locale's provisional wording and a note naming the missing
facts is placed on the cover. A provisional run may not present itself as a measured result.
"""
import argparse, json, random, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import i18n

SKILL = Path(__file__).resolve().parent.parent


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('run_dir')
    ap.add_argument('--language', default=None, help='override run.language')
    a = ap.parse_args()

    d = Path(a.run_dir)
    run = json.loads((d / 'run.json').read_text(encoding='utf-8'))
    model = json.loads((d / 'model.json').read_text(encoding='utf-8'))
    pop = json.loads((d / 'population.json').read_text(encoding='utf-8'))

    language = a.language or run.get('language') or 'en'
    L = i18n.load_locale(language)
    money = lambda v: i18n.fmt_money(v, run.get('currency'), L)
    mil = lambda m: money(m * 1e6) if m is not None else L['labels']['dash']
    people = lambda n: i18n.fmt_people(n, L)

    rp = d / 'report.json'
    r = (json.loads(rp.read_text(encoding='utf-8')) if rp.exists()
         else json.loads((SKILL / 'assets/report_spec.json').read_text(encoding='utf-8')))
    F = {k: v['value'] for k, v in run['facts'].items()}
    C = {k: v['value'] for k, v in run['facts_count'].items()}
    thr = run['threshold']

    # TC quantiles by sampling the modelled mixture
    random.seed(1)
    samples = []
    for b in model['buckets']:
        n = max(1, int(b['headcount']['mode'] / 10))
        t = b['tc']
        samples += [random.triangular(t['low'], t['high'], t['mode']) for _ in range(n)]
    samples.sort()
    q = lambda p: samples[int(p * (len(samples) - 1))]

    r.setdefault('meta', {})
    r['meta'].update({
        "company": run['company'],
        "language": language,
        "reference_date": run['reference_date'],
        "threshold": (L['threshold_sentence'].format(
            amount=i18n.fmt_int(thr, L), currency=run.get('currency') or '',
            basis=run['assumptions']['equity_price_basis']) if thr is not None else "TODO"),
    })
    for k in ("entity_type", "scope", "confidence"):
        if not r['meta'].get(k) or str(r['meta'][k]).startswith('{'):
            r['meta'][k] = "TODO"
    if not r['meta'].get('subtitle') or str(r['meta']['subtitle']).startswith('{'):
        r['meta']['subtitle'] = L['cover']['subtitle_default']

    if run.get('provisional'):
        missing = ", ".join(run.get('provisional_facts') or ["required public figures"])
        r['meta']['confidence'] = L['labels']['provisional_confidence']
        r['meta']['provisional_note'] = L['labels']['provisional_note'].format(facts=missing)
    else:
        r['meta'].pop('provisional_note', None)

    pc = (F['employee_benefit_expense'] * 1e6 / C['headcount']
          if F.get('employee_benefit_expense') and C.get('headcount') else None)
    K, TODO = L['kpi'], "TODO"
    ex = r.setdefault('executive', {})
    ex['metrics'] = [
        {"label": K['headcount'], "value": people(C['headcount']) if C.get('headcount') else TODO},
        {"label": K['rnd_headcount'],
         "value": (f"{people(C['rnd_headcount'])} / {i18n.fmt_pct(C['rnd_headcount'] / C['headcount'], L)}"
                   if C.get('rnd_headcount') and C.get('headcount') else TODO)},
        {"label": K['payroll_per_head'], "value": money(pc) if pc else TODO},
        {"label": K['tc_median'], "value": money(q(0.5))},
        {"label": K['tc_p90'], "value": money(q(0.9))},
        {"label": K['above_p50'], "value": people(pop['estimated_above_threshold']['p50'])},
        {"label": K['above_range'],
         "value": f"{i18n.fmt_int(pop['estimated_above_threshold']['p05'], L)}-"
                  f"{people(pop['estimated_above_threshold']['p95'])}"},
        {"label": K['above_share'], "value": i18n.fmt_pct(pop['share_above_threshold']['p50'], L, 1)},
    ]
    if not ex.get('diagnosis') or str(ex['diagnosis']).startswith('{'):
        ex['diagnosis'] = "TODO: one-sentence diagnosis of the pay structure"

    M = L['metrics']
    bus = r.setdefault('business', {})
    metrics = []

    def add(key, claim="observed_fact"):
        v = F.get(key)
        if v is not None:
            metrics.append({"metric": M[key], "value": mil(v), "type": claim,
                            "evidence": run['facts'][key].get('evidence_id') or "TODO"})

    for key in ("revenue", "gross_profit", "operating_profit", "net_profit", "rnd_expense",
                "sales_expense", "admin_expense", "employee_benefit_expense", "sbc_expense"):
        add(key)
    if F.get('gross_profit') and C.get('headcount'):
        metrics.append({"metric": M['gross_profit_per_head'], "value": money(F['gross_profit'] * 1e6 / C['headcount']),
                        "type": "derived_metric", "evidence": M['note_gp_per_head']})
    if F.get('gross_profit') and F.get('employee_benefit_expense'):
        metrics.append({"metric": M['benefit_over_gp'],
                        "value": i18n.fmt_pct(F['employee_benefit_expense'] / F['gross_profit'], L, 1),
                        "type": "derived_metric", "evidence": M['note_notes']})
    bus['metrics'] = metrics
    bus['profit_pools'] = [
        {"segment": s['name'],
         "revenue": mil(s['revenue']) if s.get('revenue') else TODO,
         "gross_profit": mil(s['gross_profit']) if s.get('gross_profit') else TODO,
         "growth": (i18n.fmt_float(s['growth_pct'], L, 1) + "%" if s.get('growth_pct') is not None else TODO),
         "dependency": s.get('dependency', TODO)}
        for s in run['segments'] if s.get('name')]

    pb = {b['name']: b for b in pop['buckets']}
    mode_label = L['labels']['mode']
    r['compensation'] = [
        {"bucket": b['name'],
         "headcount": i18n.fmt_people(b['headcount']['mode'], L),
         "cash": b.get("cash") or L['labels']['dash'],
         "equity": b.get("equity") or L['labels']['dash'],
         "total": f"{i18n.fmt_compact(b['tc']['low'], L)}-{i18n.fmt_compact(b['tc']['high'], L)} "
                  f"({mode_label} {i18n.fmt_compact(b['tc']['mode'], L)})",
         "probability": (i18n.fmt_pct(pb[b['name']]['above_threshold_p50'] / max(b['headcount']['mode'], 1), L)
                         if b['name'] in pb else L['labels']['na']),
         "confidence": "inference"}
        for b in model['buckets']]

    tot = pop['estimated_above_threshold']['p50']
    r['high_compensation'] = {
        "headline": (f"p05 {i18n.fmt_int(pop['estimated_above_threshold']['p05'], L)} / "
                     f"p50 {i18n.fmt_int(tot, L)} / "
                     f"p95 {i18n.fmt_people(pop['estimated_above_threshold']['p95'], L, approx=False)} "
                     f"({i18n.fmt_pct(pop['share_above_threshold']['p50'], L, 1)})"),
        "rows": [{"bucket": b['name'], "count": i18n.fmt_people(b['above_threshold_p50'], L),
                  "contribution": i18n.fmt_pct(b['above_threshold_p50'] / tot, L) if tot else L['labels']['na'],
                  "uncertainty": TODO}
                 for b in sorted(pop['buckets'], key=lambda x: -x['above_threshold_p50'])
                 if b['above_threshold_p50'] >= 1]}

    for sec, default in [("charter", {"summary": [], "timeline": []}), ("talent_pnl", []), ("organization", []),
                         ("role_pay", []),
                         ("career", {"internal_path": [], "external_path": [], "first_threshold_state": TODO,
                                     "promotion_tenure": TODO, "senior_hire_mix": TODO}),
                         ("governance", []), ("sensitivity", []), ("evidence", [])]:
        if sec not in r or r[sec] in ([], {}, None):
            r[sec] = default
    r.pop('constitution', None)

    rp.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding='utf-8')
    todo = json.dumps(r, ensure_ascii=False).count('TODO')
    print(f"report.json updated in '{language}'"
          + (f" (chrome falls back to {L['_chrome']})" if L.get('_chrome_is_fallback') else "")
          + f"; {todo} TODO fields remain (fill the prose sections: diagnosis, charter, talent_pnl, "
            "organization, role_pay, career, governance, sensitivity, evidence).")
    if run.get('provisional'):
        print(f"[provisional] confidence forced to '{r['meta']['confidence']}'; "
              f"missing: {', '.join(run.get('provisional_facts') or [])}. "
              "Do not present any number here as measured.")


if __name__ == '__main__':
    main()
