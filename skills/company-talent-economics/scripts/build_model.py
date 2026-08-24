#!/usr/bin/env python3
"""levels.json -> model.json (estimator input) + envelope check.

Usage: build_model.py <run_dir>
Reads run.json (threshold, headcount, payroll facts, assumptions) and levels.json; writes model.json and prints the
headcount-weighted modelled TC total against the payroll envelope target.
"""
import json, sys
from pathlib import Path

def tri_mean(t): return (t['low']+t['mode']+t['high'])/3

def tri_cdf(x, a, c, b):
    if x <= a: return 0.0
    if x >= b: return 1.0
    if x <= c: return ((x-a)**2)/((b-a)*(c-a)) if (b-a)*(c-a) else 0.0
    return 1 - ((b-x)**2)/((b-a)*(b-c)) if (b-a)*(b-c) else 1.0

def p_exceed(tc, thr, scale=1.0):
    return 1 - tri_cdf(thr, tc['low']*scale, tc['mode']*scale, tc['high']*scale)

def main():
    d = Path(sys.argv[1]); run = json.loads((d/'run.json').read_text(encoding='utf-8')); lv = json.loads((d/'levels.json').read_text(encoding='utf-8'))
    buckets=[]; tc_total=0.0; hc_total=0.0; problems=[]
    for fn in lv['functions']:
        hc = fn['headcount']
        if any(hc[k] is None for k in ('low','mode','high')): problems.append(f"{fn['name']}: headcount not filled"); continue
        if abs(sum(fn['shares'])-1) > 0.01: problems.append(f"{fn['name']}: shares sum to {sum(fn['shares']):.2f}, must be 1")
        for band, sh, tc in zip(fn['native_bands'], fn['shares'], fn['tc']):
            if sh == 0: continue
            if any(tc[k] is None for k in ('low','mode','high')): problems.append(f"{fn['name']}/{band}: tc not filled"); continue
            if not (tc['low'] <= tc['mode'] <= tc['high']): problems.append(f"{fn['name']}/{band}: need low<=mode<=high")
            u = lv.get('tc_uncertainty_pct', 0.15); thr = run['threshold']
            pe = {"low": round(p_exceed(tc, thr, 1-u),4), "mode": round(p_exceed(tc, thr, 1.0),4), "high": round(p_exceed(tc, thr, 1+u),4)}
            b = {"name": f"{fn['name']} {band}", "function": fn['name'], "level": band,
                 "headcount": {k: round(hc[k]*sh) for k in ('low','mode','high')}, "tc": tc, "p_exceed": pe,
                 "cash": (fn.get('cash') or [None]*len(fn['tc']))[fn['native_bands'].index(band)], "equity": (fn.get('equity') or [None]*len(fn['tc']))[fn['native_bands'].index(band)]}
            buckets.append(b); tc_total += hc['mode']*sh*tri_mean(tc); hc_total += hc['mode']*sh
    if problems: print('\n'.join('[!!] '+p for p in problems)); sys.exit(1)
    disclosed = run['facts_count']['headcount']['value']
    model = {"company": run['company'], "reference_date": run['reference_date'], "threshold": {"amount": run['threshold'], "currency": run['currency']},
             "workforce": {"low": round(hc_total*0.98), "mode": round(hc_total), "high": round(hc_total*1.02)}, "buckets": buckets}
    (d/'model.json').write_text(json.dumps(model, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f"model.json written: {len(buckets)} buckets, modelled headcount {hc_total:,.0f}" + (f" vs disclosed {disclosed:,.0f} ({(hc_total-disclosed)/disclosed:+.1%})" if disclosed else ""))
    checks = run.setdefault('checks', {})
    checks['modelled_tc_total_million'] = round(tc_total/1e6, 1)
    E = run['facts']['employee_benefit_expense']['value']; S = run['facts']['sbc_expense']['value'] or 0; r = run['assumptions']['employer_social_rate']
    if E:
        target = ((E - S)/(1+r) + S) * 1e6; dev = (tc_total-target)/target
        print(f"Payroll envelope: modelled TC total {tc_total/1e6:,.0f}M vs target {target/1e6:,.0f}M -> {dev:+.1%} ({'OK' if abs(dev)<=0.10 else 'REVISE levels.json'})")
        checks['payroll_envelope_deviation'] = round(dev, 4)
        checks['envelope_check'] = 'payroll_envelope'
    else:
        # No disclosed benefit expense - normal for unlisted entities. The envelope identity cannot
        # be run, so fall back to affordability ratios. These are plausibility bounds, not accounting
        # identities: they can only catch a model that is impossible, never confirm one that is right.
        checks.pop('payroll_envelope_deviation', None)
        rev = run['facts']['revenue']['value']; gp = run['facts']['gross_profit']['value']
        if rev:
            ratio = tc_total / (rev * 1e6)
            checks['envelope_check'] = 'tc_over_revenue'
            checks['tc_total_over_revenue'] = round(ratio, 4)
            verdict = ('IMPOSSIBLE - payroll exceeds revenue' if ratio > 1.0 else
                       'IMPLAUSIBLE for most sectors - justify it in the notes or revise' if ratio > 0.6 else
                       'within a plausible band')
            print(f"Payroll envelope not checkable (employee_benefit_expense not disclosed).")
            print(f"Substitute check: modelled TC total {tc_total/1e6:,.0f}M / revenue {rev:,.0f}M = {ratio:.1%} -> {verdict}")
            if gp:
                gratio = tc_total / (gp * 1e6)
                checks['tc_total_over_gross_profit'] = round(gratio, 4)
                print(f"                  modelled TC total / gross profit = {gratio:.1%}"
                      + (" -> payroll alone exceeds gross profit; the model implies structural losses"
                         if gratio > 1.0 else ""))
            print("Record this ratio and its justification in analysis_notes.md Chain 9 in place of the envelope identity.")
        else:
            checks['envelope_check'] = 'none'
            print("[!!] Neither employee_benefit_expense nor revenue is available: no affordability check is "
                  "possible. Say so explicitly in the report and keep the run marked provisional.")
    if disclosed and abs(hc_total-disclosed)/disclosed > 0.05: print("[!!] modelled headcount differs from disclosed by >5%: fix levels.json headcounts")
    (d/'run.json').write_text(json.dumps(run, ensure_ascii=False, indent=1), encoding='utf-8')

if __name__ == '__main__': main()
