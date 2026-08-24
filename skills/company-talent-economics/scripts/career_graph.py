#!/usr/bin/env python3
"""Aggregate observed public career transitions from CSV.
Required columns: from_state,to_state,transition_type. Optional: months,evidence_weight.
"""
import argparse, csv
from collections import defaultdict
from statistics import median


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('csv_path'); args=ap.parse_args()
    edges=defaultdict(lambda:{'count':0,'weight':0.0,'months':[]})
    source_weight=defaultdict(float)
    with open(args.csv_path, newline='', encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            key=(r['from_state'],r['to_state'],r['transition_type'])
            w=float(r.get('evidence_weight') or 1.0)
            edges[key]['count']+=1; edges[key]['weight']+=w; source_weight[r['from_state']]+=w
            if r.get('months'):
                try: edges[key]['months'].append(float(r['months']))
                except ValueError: pass
    for key,v in sorted(edges.items(), key=lambda kv:kv[1]['weight'], reverse=True):
        fs,ts,tt=key; share=v['weight']/source_weight[fs] if source_weight[fs] else 0
        med=median(v['months']) if v['months'] else None
        medtxt=f'{med:.0f} mo' if med is not None else 'n/a'
        print(f'{fs} -> {ts} [{tt}] n={v["count"]}, weighted_share={share:.1%}, median_tenure={medtxt}')

if __name__=='__main__': main()
