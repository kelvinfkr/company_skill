#!/usr/bin/env python3
import json, sys

def band(x):
    return float(x[0]), float(x[1])

def diagnose(market, economic, internal):
    m0,m1=band(market); e0,e1=band(economic); i0,i1=band(internal)
    lo=max(m0,e0,i0); hi=min(m1,e1,i1)
    if lo <= hi:
        return {"diagnostic":"overlap", "defensible_zone":[lo,hi]}
    me_lo=max(m0,e0); me_hi=min(m1,e1)
    if me_lo <= me_hi and i1 < me_lo:
        return {"diagnostic":"retention_risk", "market_economic_overlap":[me_lo,me_hi]}
    if m0 > e1:
        return {"diagnostic":"structural_talent_gap", "gap":[e1,m0]}
    if i0 > max(m1,e1):
        return {"diagnostic":"overpayment_or_governance_risk"}
    return {"diagnostic":"no_clean_overlap"}

def main():
    data=json.load(open(sys.argv[1],encoding='utf-8'))
    out=[]
    for r in data.get('roles',[]):
        out.append({"role":r['role'], **diagnose(r['market'],r['economic'],r['internal'])})
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
