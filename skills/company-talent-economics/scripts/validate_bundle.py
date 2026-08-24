#!/usr/bin/env python3
"""Validate an output bundle before rendering: report.json sections, evidence.jsonl fields,
manifest columns, terminology, and the payroll-envelope identity when the numbers exist.

Language-aware: claim types may be written either as canonical English keys (observed_fact,
derived_metric, assumption, inference, reconstruction) or as the report locale's display labels,
and terminology traps are read from that locale's forbidden_terms.

Usage:
  validate_bundle.py <bundle_dir>
  validate_bundle.py <bundle_dir> --benefit-expense 30470 --sbc 5365 --social-rate 0.18 --tc-total 24700
All amounts in millions. Omit --benefit-expense when it was never disclosed: the envelope identity is
then skipped and the substitute affordability ratio recorded by build_model.py is reported instead.
"""
import argparse, csv, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import i18n

REQ_SECTIONS = ["meta", "executive", "business", "talent_pnl", "organization", "compensation",
                "high_compensation", "role_pay", "career", "governance", "sensitivity", "evidence"]
CLAIM_TYPES = {"observed_fact", "derived_metric", "assumption", "inference", "reconstruction"}
TIERS = set("ABCDE")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('bundle')
    ap.add_argument('--benefit-expense', type=float)
    ap.add_argument('--sbc', type=float, default=0.0)
    ap.add_argument('--social-rate', type=float, default=None)
    ap.add_argument('--tc-total', type=float, help='headcount-weighted modelled TC total, same unit as benefit expense')
    ap.add_argument('--language', default=None)
    a = ap.parse_args()
    b = Path(a.bundle)
    problems = []

    run = json.loads((b / 'run.json').read_text(encoding='utf-8')) if (b / 'run.json').exists() else {}
    rp = b / 'report.json'
    report = json.loads(rp.read_text(encoding='utf-8')) if rp.exists() else None

    language = (a.language or (report or {}).get('meta', {}).get('language') or run.get('language') or 'en')
    L = i18n.load_locale(language)
    allowed_types = i18n.claim_type_values(L)

    if report is None:
        problems.append('report.json missing')
    else:
        if 'constitution' in report and 'charter' not in report:
            problems.append("report.json: rename key 'constitution' -> 'charter'")
        for s in REQ_SECTIONS:
            if s not in report:
                problems.append(f'report.json: missing section {s}')
        if not report.get('meta', {}).get('language'):
            problems.append('report.json: meta.language missing; the renderer cannot pick a locale')
        for m in report.get('business', {}).get('metrics', []):
            if m.get('type') not in allowed_types:
                problems.append(f"business.metrics '{m.get('metric')}': type must be one of "
                                f"{sorted(CLAIM_TYPES)} or their {L['_chrome']} labels, got {m.get('type')!r}")
        txt = json.dumps(report, ensure_ascii=False)
        for bad, good in L.get('forbidden_terms', []):
            if bad in txt:
                problems.append(f"report.json: use '{good}' not '{bad}'")
        if run.get('provisional') and report.get('meta', {}).get('confidence') != L['labels']['provisional_confidence']:
            problems.append("run is provisional but report.json meta.confidence does not say so: "
                            "rerun compile_report.py")

    ep = b / 'evidence.jsonl'
    if not ep.exists():
        problems.append('evidence.jsonl missing')
    else:
        seen = set()
        for i, line in enumerate(ep.read_text(encoding='utf-8').splitlines(), 1):
            if not line.strip():
                continue
            try:
                e = json.loads(line)
            except json.JSONDecodeError as exc:
                problems.append(f'evidence.jsonl line {i}: not valid JSON ({exc.msg})')
                continue
            for k in ('claim', 'source', 'claim_type', 'source_tier', 'confidence'):
                if k not in e:
                    problems.append(f'evidence.jsonl line {i}: missing {k}')
            if e.get('claim_type') not in CLAIM_TYPES:
                problems.append(f'evidence.jsonl line {i}: bad claim_type {e.get("claim_type")!r} '
                                f'(use the canonical English key)')
            if e.get('source_tier') not in TIERS:
                problems.append(f'evidence.jsonl line {i}: bad tier {e.get("source_tier")!r}')
            seen.add(e.get('claim_type'))
        if 'observed_fact' not in seen:
            problems.append('evidence.jsonl: no observed_fact entries')

    mp = b / 'source_manifest.csv'
    if not mp.exists():
        problems.append('source_manifest.csv missing')
    else:
        with open(mp, newline='', encoding='utf-8') as f:
            cols = set(csv.DictReader(f).fieldnames or [])
        for c in ('source', 'url', 'date', 'source_type', 'tier', 'status'):
            if c not in cols:
                problems.append(f'source_manifest.csv: missing column {c}')

    tc_total = a.tc_total if a.tc_total is not None else run.get('checks', {}).get('modelled_tc_total_million')
    social = a.social_rate if a.social_rate is not None else run.get('assumptions', {}).get('employer_social_rate', 0.18)
    benefit = a.benefit_expense
    if benefit is None and run:
        benefit = run.get('facts', {}).get('employee_benefit_expense', {}).get('value')
        if a.sbc == 0.0:
            a.sbc = run.get('facts', {}).get('sbc_expense', {}).get('value') or 0.0

    if benefit and tc_total:
        cash = (benefit - a.sbc) / (1 + social)
        target = cash + a.sbc
        dev = (tc_total - target) / target
        print(f'Payroll envelope: implied cash+equity target = {target:,.0f}; '
              f'modelled TC total = {tc_total:,.0f}; deviation = {dev:+.1%}')
        if abs(dev) > 0.10:
            problems.append(f'payroll envelope deviation {dev:+.1%} exceeds +/-10%: revise buckets or level pay')
    else:
        ratio = run.get('checks', {}).get('tc_total_over_revenue')
        if ratio is not None:
            print(f'Payroll envelope not checkable (employee benefit expense not disclosed). '
                  f'Substitute check: modelled TC total / revenue = {ratio:.1%}')
            if ratio > 1.0:
                problems.append(f'modelled TC total is {ratio:.0%} of revenue: impossible')
        else:
            print('Payroll envelope not checked: no employee benefit expense and no substitute ratio recorded.')

    if problems:
        print('\n'.join('[!!] ' + p for p in problems))
        sys.exit(1)
    print(f'[ok] bundle validates (language {language}, chrome {L["_chrome"]})')


if __name__ == '__main__':
    main()
