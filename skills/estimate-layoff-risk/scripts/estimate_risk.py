#!/usr/bin/env python3
"""Monte Carlo scenario estimator for transparent competing job-loss hazards."""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path


FIELDS = ["company_action", "unit_given_action", "role_given_unit", "person_given_role", "contract_exit", "performance_exit", "redeployment_given_structural"]


def validate_tri(name: str, tri: dict) -> None:
    values = [float(tri[k]) for k in ("low", "mode", "high")]
    if not (0 <= values[0] <= values[1] <= values[2] <= 1):
        raise ValueError(f"{name} must satisfy 0 <= low <= mode <= high <= 1")


def sample_tri(rng: random.Random, tri: dict) -> float:
    return rng.triangular(float(tri["low"]), float(tri["high"]), float(tri["mode"]))


def quantile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    index = (len(ordered) - 1) * probability
    lo = int(index)
    hi = min(lo + 1, len(ordered) - 1)
    weight = index - lo
    return ordered[lo] * (1 - weight) + ordered[hi] * weight


def summarize(values: list[float]) -> dict:
    return {"p05": round(quantile(values, 0.05), 4), "p50": round(quantile(values, 0.50), 4), "p95": round(quantile(values, 0.95), 4)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("model")
    parser.add_argument("-o", "--output")
    parser.add_argument("--samples", type=int, default=50000)
    parser.add_argument("--seed", type=int, default=17)
    args = parser.parse_args()
    if args.samples < 1000:
        raise ValueError("Use at least 1000 samples")
    model = json.loads(Path(args.model).read_text(encoding="utf-8"))
    rng = random.Random(args.seed)
    results = {}
    for horizon, values in model.get("horizons", {}).items():
        for field in FIELDS:
            if field not in values:
                values[field] = {"low": 0, "mode": 0, "high": 0}
            validate_tri(f"{horizon}.{field}", values[field])
        buckets = {"structural_layoff": [], "contract_or_nonrenewal": [], "performance_exit": [], "redeployment": [], "any_involuntary_exit": []}
        for _ in range(args.samples):
            p_action = sample_tri(rng, values["company_action"])
            p_unit = sample_tri(rng, values["unit_given_action"])
            p_role = sample_tri(rng, values["role_given_unit"])
            p_person = sample_tri(rng, values["person_given_role"])
            structural_pre = p_action * p_unit * p_role * p_person
            p_redeploy_cond = sample_tri(rng, values["redeployment_given_structural"])
            redeploy = structural_pre * p_redeploy_cond
            structural_exit = structural_pre * (1 - p_redeploy_cond)
            contract = sample_tri(rng, values["contract_exit"])
            performance = sample_tri(rng, values["performance_exit"])
            any_exit = 1 - (1 - structural_exit) * (1 - contract) * (1 - performance)
            buckets["structural_layoff"].append(structural_exit)
            buckets["contract_or_nonrenewal"].append(contract)
            buckets["performance_exit"].append(performance)
            buckets["redeployment"].append(redeploy)
            buckets["any_involuntary_exit"].append(any_exit)
        results[horizon] = {key: summarize(series) for key, series in buckets.items()}
    payload = {"calibration_status": model.get("calibration_status", "scenario_only"), "confidence": model.get("confidence", "low"), "combination_assumption": "conditional layer product; independent competing-hazard approximation", "samples": args.samples, "results": results}
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
