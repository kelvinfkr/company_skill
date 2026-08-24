#!/usr/bin/env python3
"""Monte Carlo estimator for employees above a TC threshold.

Each bucket has triangular headcount uncertainty plus either:
- p_exceed = triangular epistemic probability interval; or
- tc = triangular within-bucket TC distribution.

Standard library only.
"""
from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from statistics import mean


def quantile(values, p):
    xs = sorted(values)
    if not xs:
        return float('nan')
    pos = (len(xs) - 1) * p
    lo, hi = math.floor(pos), math.ceil(pos)
    if lo == hi:
        return xs[lo]
    w = pos - lo
    return xs[lo] * (1 - w) + xs[hi] * w


def validate_tri(x, label, max_value=None):
    lo, mode, hi = x['low'], x['mode'], x['high']
    if not (0 <= lo <= mode <= hi):
        raise ValueError(f'{label}: require 0 <= low <= mode <= high')
    if max_value is not None and hi > max_value:
        raise ValueError(f'{label}: high must be <= {max_value}')


def tri_cdf(x, a, c, b):
    if x <= a: return 0.0
    if x >= b: return 1.0
    if a == b: return 1.0 if x >= a else 0.0
    if x <= c:
        denom = (b-a)*(c-a)
        return 0.0 if denom == 0 else ((x-a)**2)/denom
    denom = (b-a)*(b-c)
    return 1.0 if denom == 0 else 1 - ((b-x)**2)/denom


def p_exceed_from_tc(tc, threshold):
    return 1.0 - tri_cdf(threshold, tc['low'], tc['mode'], tc['high'])


def fmt(x):
    return f'{x:,.0f}' if abs(x) >= 100 else f'{x:.1f}'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('input', type=Path)
    ap.add_argument('--samples', type=int, default=50000)
    ap.add_argument('--seed', type=int, default=20260824)
    ap.add_argument('--json-out', type=Path)
    args = ap.parse_args()
    if args.samples < 1000:
        raise ValueError('Use at least 1000 samples')
    data = json.loads(args.input.read_text())
    threshold = float(data['threshold']['amount'])
    buckets = data['buckets']
    for b in buckets:
        validate_tri(b['headcount'], b['name']+'.headcount')
        if 'p_exceed' in b:
            validate_tri(b['p_exceed'], b['name']+'.p_exceed', 1)
        elif 'tc' in b:
            validate_tri(b['tc'], b['name']+'.tc')
        else:
            raise ValueError(f"{b['name']}: need p_exceed or tc")

    random.seed(args.seed)
    total_hc, total_high = [], []
    bucket_vals = {b['name']: [] for b in buckets}
    for _ in range(args.samples):
        hc_sum = high_sum = 0.0
        for b in buckets:
            h = b['headcount']
            hc = random.triangular(h['low'], h['high'], h['mode'])
            if 'p_exceed' in b:
                p = b['p_exceed']
                pe = random.triangular(p['low'], p['high'], p['mode'])
            else:
                pe = p_exceed_from_tc(b['tc'], threshold)
            nh = hc * pe
            hc_sum += hc; high_sum += nh
            bucket_vals[b['name']].append(nh)
        total_hc.append(hc_sum); total_high.append(high_sum)

    shares = [h/n if n else 0 for h,n in zip(total_high,total_hc)]
    result = {
        'company': data['company'],
        'reference_date': data.get('reference_date'),
        'threshold': data['threshold'],
        'samples': args.samples,
        'estimated_headcount': {k: v for k,v in [('p05',quantile(total_hc,.05)),('p50',quantile(total_hc,.5)),('p95',quantile(total_hc,.95)),('mean',mean(total_hc))]},
        'estimated_above_threshold': {k: v for k,v in [('p05',quantile(total_high,.05)),('p50',quantile(total_high,.5)),('p95',quantile(total_high,.95)),('mean',mean(total_high))]},
        'share_above_threshold': {'p05':quantile(shares,.05),'p50':quantile(shares,.5),'p95':quantile(shares,.95)},
        'buckets': []
    }
    for b in buckets:
        vals = bucket_vals[b['name']]
        result['buckets'].append({
            'name': b['name'], 'function': b.get('function'), 'level': b.get('level'),
            'geography': b.get('geography'), 'business_unit': b.get('business_unit'),
            'above_threshold_p05': quantile(vals,.05), 'above_threshold_p50': quantile(vals,.5), 'above_threshold_p95': quantile(vals,.95)
        })

    t=result['estimated_above_threshold']; s=result['share_above_threshold']
    print(f"Company: {result['company']}")
    print(f"Threshold: {data['threshold']['currency']} {threshold:,.0f}")
    print(f"Above threshold p05/p50/p95: {fmt(t['p05'])} / {fmt(t['p50'])} / {fmt(t['p95'])}")
    print(f"Share p05/p50/p95: {s['p05']*100:.1f}% / {s['p50']*100:.1f}% / {s['p95']*100:.1f}%")
    print('\nBucket contribution (p50):')
    for r in sorted(result['buckets'], key=lambda x:x['above_threshold_p50'], reverse=True):
        print(f"  {r['name']}: {fmt(r['above_threshold_p50'])}")
    if args.json_out:
        args.json_out.write_text(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
