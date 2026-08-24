#!/usr/bin/env python3
"""End-to-end harness test: drives a full run through all ten gates with synthetic data.

Covers what unit tests cannot: that the gates, the model, the compiler and the renderer still agree
with each other. Three scenarios run:

  listed     a disclosed-everything company in English; every gate 0-10 must pass and a PDF appear
  unlisted   a private company missing gross profit and payroll; the Phase 1 NOT AVAILABLE escape
             must fire, the run must come out provisional, and the affordability check must fall
             back to TC/revenue
  literal    a CHECKLIST whose prose mentions '[ ]' must not read as an unticked box

Then every shipped locale is rendered to DOCX to prove no pack breaks the renderer.

  python scripts/selftest.py            # DOCX only, no LibreOffice needed
  python scripts/selftest.py --pdf      # also convert to PDF (needs LibreOffice)
"""
from __future__ import annotations
import argparse, json, shutil, subprocess, sys, tempfile
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
SCRIPTS = SKILL / "scripts"
PY = sys.executable
sys.path.insert(0, str(SCRIPTS))
import i18n

FAILURES: list[str] = []


def run(*args, expect=0, label=""):
    p = subprocess.run([PY, *[str(x) for x in args]], capture_output=True, text=True)
    if p.returncode != expect:
        FAILURES.append(f"{label or args[0]}: exit {p.returncode}, expected {expect}\n"
                        f"  stdout: {p.stdout.strip()[:900]}\n  stderr: {p.stderr.strip()[:600]}")
    return p


def check(cond, msg):
    if not cond:
        FAILURES.append(msg)


def tri(low, mode, high):
    return {"low": low, "mode": mode, "high": high}


def tri_mean(t):
    return (t["low"] + t["mode"] + t["high"]) / 3


def tick(md: str) -> str:
    return md.replace("- [ ]", "- [x]")


def fill_todos(node):
    """Replace every TODO / empty prose slot so the Phase 8 gate can pass in a test."""
    if isinstance(node, dict):
        return {k: fill_todos(v) for k, v in node.items()}
    if isinstance(node, list):
        return [fill_todos(v) for v in node]
    if isinstance(node, str) and "TODO" in node:
        return "synthetic test value"
    return node


LEVELS_TC = {
    "R&D": [tri(90_000, 110_000, 140_000), tri(130_000, 160_000, 200_000), tri(190_000, 240_000, 320_000),
            tri(300_000, 400_000, 560_000), tri(500_000, 800_000, 1_400_000)],
    "Non-R&D professional": [tri(70_000, 88_000, 112_000), tri(104_000, 128_000, 160_000),
                             tri(152_000, 192_000, 256_000), tri(240_000, 320_000, 448_000),
                             tri(400_000, 640_000, 1_120_000)],
    "Frontline": [tri(45_000, 55_000, 70_000)],
    "Overseas": [tri(60_000, 80_000, 110_000)],
}
HEADCOUNT = {"R&D": 600, "Non-R&D professional": 300, "Frontline": 50, "Overseas": 50}


def write_levels(d: Path) -> float:
    lv = json.loads((d / "levels.json").read_text(encoding="utf-8"))
    total = 0.0
    for fn in lv["functions"]:
        hc = HEADCOUNT[fn["name"]]
        fn["headcount"] = {"low": round(hc * 0.95), "mode": hc, "high": round(hc * 1.05)}
        fn["tc"] = LEVELS_TC[fn["name"]]
        total += sum(hc * s * tri_mean(t) for s, t in zip(fn["shares"], fn["tc"]))
    (d / "levels.json").write_text(json.dumps(lv, ensure_ascii=False, indent=1), encoding="utf-8")
    return total


def write_manifest(d: Path):
    lines = ["pass,source,url,date,source_type,tier,status"]
    for p in ["1_identity_charter", "2_business_economics", "3_workforce_payroll",
              "4_compensation_equity", "5_organization_roles", "6_career_transitions"]:
        lines.append(f"{p},Synthetic filing,https://example.invalid/{p},2026-01-01,filing,A,used")
    (d / "source_manifest.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_evidence(d: Path, tier="A"):
    rows = [{"id": f"E0{i}", "claim": f"synthetic claim {i}", "source": "Synthetic FY2025 annual report",
             "published_date": "2026-01-01", "claim_type": "observed_fact", "source_tier": tier,
             "confidence": "high"} for i in (1, 2, 3)]
    (d / "evidence.jsonl").write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n",
                                      encoding="utf-8")


def write_transitions(d: Path):
    rows = ["from_state,to_state,transition_type,months,evidence_tier,note"]
    for i in range(9):
        rows.append(f"senior,director,internal_promotion,{24 + i},D,synthetic")
    (d / "career_transitions.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")


def write_pay_bands(d: Path):
    roles = [{"role": f"Critical role {i}", "market": [200_000, 320_000],
              "economic": [240_000, 400_000], "internal": [220_000, 300_000]} for i in (1, 2, 3)]
    (d / "pay_bands.json").write_text(json.dumps({"roles": roles}, ensure_ascii=False, indent=1), encoding="utf-8")


# ---------------------------------------------------------------- scenario: listed

def scenario_listed(tmp: Path, make_pdf: bool) -> Path:
    d = tmp / "listed"
    run(SCRIPTS / "init_run.py", "Northwind Robotics Inc.", "--out", d, "--year", "2025",
        "--jurisdiction", "us", "--language", "en", label="init_run(listed)")

    tc_total = write_levels(d)
    run_json = json.loads((d / "run.json").read_text(encoding="utf-8"))
    sbc, rate = 20.0, run_json["assumptions"]["employer_social_rate"]
    benefit = (tc_total / 1e6 - sbc) * (1 + rate) + sbc  # makes the envelope identity balance exactly

    run_json["entity"] = {"legal_name": "Northwind Robotics Inc.", "ticker": "NWR", "domicile": "US",
                          "listing_venue": "NASDAQ", "company_type": "listed_operating_company",
                          "charter_status": "original"}
    facts = {"revenue": 900.0, "gross_profit": 430.0, "operating_profit": 95.0, "net_profit": 70.0,
             "rnd_expense": 150.0, "sales_expense": 110.0, "admin_expense": 60.0,
             "employee_benefit_expense": round(benefit, 1), "sbc_expense": sbc, "cash_paid_to_employees": 95.0}
    for k, v in facts.items():
        run_json["facts"][k] = {"value": v, "unit": "USD_million", "evidence_id": "E01"}
    counts = {"headcount": sum(HEADCOUNT.values()), "domestic_headcount": 950, "overseas_headcount": 50,
              "rnd_headcount": 600, "equity_award_holders": 240, "person_grants_last_12m": 120}
    for k, v in counts.items():
        run_json["facts_count"][k] = {"value": v, "evidence_id": "E02"}
    run_json["segments"] = [
        {"name": "Industrial arms", "revenue": 600.0, "gross_profit": 300.0, "growth_pct": 18.0,
         "evidence_id": "E01", "dependency": "motion-control firmware team"},
        {"name": "Service contracts", "revenue": 300.0, "gross_profit": 130.0, "growth_pct": 6.0,
         "evidence_id": "E01", "dependency": "named field-engineering leads"}]
    (d / "run.json").write_text(json.dumps(run_json, ensure_ascii=False, indent=1), encoding="utf-8")

    write_manifest(d)
    write_evidence(d, "A")
    write_transitions(d)
    write_pay_bands(d)
    notes = tick((d / "analysis_notes.md").read_text(encoding="utf-8"))
    notes += "\n\nNative level ladder: L3-L9 mapped to entry/mid/senior/director/exec.\n"
    (d / "analysis_notes.md").write_text(notes, encoding="utf-8")

    for phase in (0, 1, 2, 3, 4):
        run(SCRIPTS / "check_phase.py", d, "--phase", phase, label=f"listed gate {phase}")

    run(SCRIPTS / "build_model.py", d, label="build_model(listed)")
    checks = json.loads((d / "run.json").read_text(encoding="utf-8")).get("checks", {})
    check(checks.get("envelope_check") == "payroll_envelope",
          f"listed: expected payroll_envelope check, got {checks.get('envelope_check')!r}")
    check(abs(checks.get("payroll_envelope_deviation", 1)) <= 0.10,
          f"listed: envelope deviation {checks.get('payroll_envelope_deviation')} should be within 10%")
    run(SCRIPTS / "estimate_population.py", d / "model.json", "--samples", "20000",
        "--json-out", d / "population.json", label="estimate_population")
    run(SCRIPTS / "check_phase.py", d, "--phase", 5, label="listed gate 5")
    for phase in (6, 7):
        run(SCRIPTS / "check_phase.py", d, "--phase", phase, label=f"listed gate {phase}")

    run(SCRIPTS / "compile_report.py", d, label="compile_report(listed)")
    report = json.loads((d / "report.json").read_text(encoding="utf-8"))
    check(report["meta"].get("language") == "en", "listed: report.json meta.language should be 'en'")
    check(any(m["type"] == "observed_fact" for m in report["business"]["metrics"]),
          "listed: business metrics should carry canonical claim types")
    report = fill_todos(report)
    report["charter"] = {"summary": [{"item": "Share classes", "current": "single class",
                                      "historical": "unchanged", "evidence": "E01"}], "timeline": []}
    report["talent_pnl"] = [{"profit_pool": "Industrial arms", "process": "motion control",
                             "role": "firmware lead", "dependency": "high", "why": "synthetic"}]
    report["organization"] = [{"native": "L7", "track": "IC", "scope": "team", "function": "R&D",
                               "state": "senior", "confidence": "medium"}]
    report["role_pay"] = [{"role": "Firmware lead", "market": "200-320k", "economic": "240-400k",
                           "internal": "220-300k", "defensible": "240-300k", "diagnostic": "overlap"}]
    report["career"] = {"internal_path": ["senior -> director"], "external_path": ["external senior hire"],
                        "first_threshold_state": "senior", "promotion_tenure": "28 months",
                        "senior_hire_mix": "mostly internal"}
    report["governance"] = [{"metric": "Award holders", "value": "240", "evidence": "E02"}]
    report["sensitivity"] = ["Senior-band headcount +/-25% moves p50 by roughly a fifth."]
    report["evidence"] = [{"id": "E01", "source": "Synthetic FY2025 annual report", "date": "2026-01-01",
                           "status": "observed_fact", "supports": "revenue, gross profit"}]
    (d / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")

    run(SCRIPTS / "check_phase.py", d, "--phase", 8, label="listed gate 8")
    run(SCRIPTS / "validate_bundle.py", d, label="validate_bundle(listed)")
    run(SCRIPTS / "check_phase.py", d, "--phase", 9, label="listed gate 9")

    args = [SCRIPTS / "render_report.py", d / "report.json", "-o", d / "report.pdf"]
    if not make_pdf:
        args.append("--docx-only")
    run(*args, label="render_report(listed)")
    if not make_pdf:
        (d / "report.pdf").write_bytes(b"%PDF-1.4 placeholder for --docx-only selftest\n")
    check((d / "report.pdf").exists(), "listed: report.pdf was not produced")

    (d / "CHECKLIST.md").write_text(tick((d / "CHECKLIST.md").read_text(encoding="utf-8")), encoding="utf-8")
    run(SCRIPTS / "check_phase.py", d, "--phase", 10, label="listed gate 10")
    return d


# -------------------------------------------------------------- scenario: unlisted

def scenario_unlisted(tmp: Path) -> Path:
    d = tmp / "unlisted"
    run(SCRIPTS / "init_run.py", "Talleres Delta S.L.", "--out", d, "--year", "2025",
        "--jurisdiction", "private", "--language", "es", "--currency", "EUR",
        "--threshold", "150000", label="init_run(unlisted)")

    write_levels(d)
    run_json = json.loads((d / "run.json").read_text(encoding="utf-8"))
    run_json["entity"] = {"legal_name": "Talleres Delta S.L.", "ticker": "", "domicile": "ES",
                          "listing_venue": "", "company_type": "private_llc", "charter_status": "official_summary"}
    run_json["facts"]["revenue"] = {"value": 320.0, "unit": "EUR_million", "evidence_id": "E01"}
    run_json["facts_count"]["headcount"] = {"value": sum(HEADCOUNT.values()), "evidence_id": "E01"}
    run_json["segments"] = [{"name": "Contract manufacturing", "revenue": 320.0, "gross_profit": None,
                             "growth_pct": None, "evidence_id": "E01", "dependency": "tooling engineers"}]
    (d / "run.json").write_text(json.dumps(run_json, ensure_ascii=False, indent=1), encoding="utf-8")

    write_manifest(d)
    write_evidence(d, "C")  # no Tier A/B source at all: also an escape, also provisional
    notes = tick((d / "analysis_notes.md").read_text(encoding="utf-8"))
    notes += ("\nNOT AVAILABLE: gross_profit - searched the mercantile registry deposit, the CNMV site "
              "and the group's own press releases; unlisted S.L. deposits abbreviated accounts only.\n"
              "NOT AVAILABLE: employee_benefit_expense - searched the same deposited accounts and the "
              "collective agreement filings; no personnel cost line is published.\n")
    (d / "analysis_notes.md").write_text(notes, encoding="utf-8")

    p = run(SCRIPTS / "check_phase.py", d, "--phase", 1, label="unlisted gate 1")
    check("PROVISIONAL" in p.stdout.upper() or "provisional" in p.stdout,
          "unlisted: gate 1 should report the run as provisional")
    after = json.loads((d / "run.json").read_text(encoding="utf-8"))
    check(after.get("provisional") is True, "unlisted: run.provisional should be True after the escape")
    for want in ("gross_profit", "employee_benefit_expense"):
        check(want in after.get("provisional_facts", []),
              f"unlisted: provisional_facts should name {want}, got {after.get('provisional_facts')}")

    run(SCRIPTS / "build_model.py", d, label="build_model(unlisted)")
    checks = json.loads((d / "run.json").read_text(encoding="utf-8")).get("checks", {})
    check(checks.get("envelope_check") == "tc_over_revenue",
          f"unlisted: expected the TC/revenue fallback, got {checks.get('envelope_check')!r}")
    check(checks.get("tc_total_over_revenue") is not None,
          "unlisted: tc_total_over_revenue should be recorded when the envelope is uncheckable")
    check("payroll_envelope_deviation" not in checks,
          "unlisted: a stale envelope deviation must not survive an uncheckable run")

    run(SCRIPTS / "estimate_population.py", d / "model.json", "--samples", "20000",
        "--json-out", d / "population.json", label="estimate_population(unlisted)")
    run(SCRIPTS / "compile_report.py", d, label="compile_report(unlisted)")
    report = json.loads((d / "report.json").read_text(encoding="utf-8"))
    es = i18n.load_locale("es")
    check(report["meta"]["confidence"] == es["labels"]["provisional_confidence"],
          f"unlisted: confidence should be forced to the provisional wording, got {report['meta']['confidence']!r}")
    check("provisional_note" in report["meta"], "unlisted: cover should carry a provisional note")
    check(report["meta"]["language"] == "es", "unlisted: report language should be es")

    p = run(SCRIPTS / "validate_bundle.py", d, label="validate_bundle(unlisted)")
    check("not checkable" in p.stdout or "Substitute check" in p.stdout,
          "unlisted: validate_bundle should report the substitute affordability check")
    return d


# --------------------------------------------------------------- scenario: literal

def scenario_literal_checkbox(listed_dir: Path):
    """A heading that mentions '[ ]' is prose, not an unticked box."""
    sys.path.insert(0, str(SCRIPTS))
    import check_phase
    text = ("# Delivery checklist (replace every `[ ]` before delivery)\n\n"
            "Some runs write `[ ]` in a sentence. That is prose.\n\n"
            "- [x] first item\n- [x] second item\n")
    check(check_phase.unticked(text) == [],
          "literal: '[ ]' inside prose must not count as an unticked box")
    check(len(check_phase.unticked("- [x] done\n- [ ] not done\n* [ ] also not\n")) == 2,
          "literal: real unticked bullets must still be detected")

    cl = listed_dir / "CHECKLIST.md"
    saved = cl.read_text(encoding="utf-8")
    cl.write_text("# Checklist: tick every `[ ]` below\n\n" + saved, encoding="utf-8")
    run(SCRIPTS / "check_phase.py", listed_dir, "--phase", 10, label="literal gate 10")
    cl.write_text(saved, encoding="utf-8")


# ---------------------------------------------------------------- locale renders

def scenario_all_locales(tmp: Path, source_report: Path):
    data = json.loads(source_report.read_text(encoding="utf-8"))
    out = tmp / "locales"
    out.mkdir(exist_ok=True)
    sys.path.insert(0, str(SCRIPTS))
    import render_report
    for tag in i18n.available_locales():
        data["meta"]["language"] = tag
        target = out / f"report_{tag}.docx"
        try:
            render_report.build_docx(data, target)
        except Exception as exc:  # noqa: BLE001 - a broken pack must name itself
            FAILURES.append(f"render {tag}: {type(exc).__name__}: {exc}")
            continue
        check(target.exists() and target.stat().st_size > 20_000, f"render {tag}: suspiciously small DOCX")
    # An unshipped language must still render, falling back to English chrome.
    data["meta"]["language"] = "vi"
    try:
        render_report.build_docx(data, out / "report_vi.docx")
    except Exception as exc:  # noqa: BLE001
        FAILURES.append(f"render fallback vi: {type(exc).__name__}: {exc}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pdf", action="store_true", help="also convert to PDF (needs LibreOffice)")
    ap.add_argument("--keep", action="store_true", help="keep the temp run directories")
    a = ap.parse_args()

    run(SCRIPTS / "check_locales.py", label="check_locales")
    tmp = Path(tempfile.mkdtemp(prefix="cte_selftest_"))
    try:
        listed = scenario_listed(tmp, a.pdf)
        scenario_unlisted(tmp)
        scenario_literal_checkbox(listed)
        scenario_all_locales(tmp, listed / "report.json")
    finally:
        if a.keep:
            print(f"run directories kept in {tmp}")
        else:
            shutil.rmtree(tmp, ignore_errors=True)

    if FAILURES:
        print(f"\nSELFTEST FAILED ({len(FAILURES)} problems):")
        for f in FAILURES:
            print("  [!!] " + f)
        sys.exit(1)
    print(f"\nSELFTEST PASSED: gates 0-10, the unlisted provisional path, the literal-checkbox fix, "
          f"and {len(i18n.available_locales())} locale renders (+1 fallback).")


if __name__ == "__main__":
    main()
