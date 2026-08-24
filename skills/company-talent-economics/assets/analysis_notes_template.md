# analysis_notes.md - {company} FY{year}

- Report language: **{language}**  -  write these notes and the report in it.
- Jurisdiction: **{jurisdiction}**  -  see references/jurisdiction_playbooks.md and assets/jurisdictions.json.

Fill every checkbox line below. Write the number, its unit, and the evidence id (E01...) from evidence.jsonl.

When a figure genuinely is not public, write a line in this exact form instead:

    NOT AVAILABLE: <fact_key> - <the venues and queries you actually searched>

Use the run.json key as `<fact_key>` (`revenue`, `gross_profit`, `employee_benefit_expense`, `headcount`).
For an unlisted entity that satisfies the Phase 1 gate and marks the whole run provisional; the report
is then labelled a provisional estimate and no figure in it may be presented as measured. It is never a
licence to invent a number.

## Phase 0 — Entity
- [ ] Legal entity / ticker / domicile / listing venue:
- [ ] Company type (from company_type_router.md):
- [ ] Fiscal year end and reference date:
- [ ] Reporting currency; conversion rate if any:

## Chain 1 — Payroll envelope
- [ ] Employee benefit expense E (Tier A):
- [ ] SBC S (Tier A):
- [ ] Employer social rate used (defaults.json or disclosed):
- [ ] Cash pay = (E − S)/(1+rate) =
- [ ] Per-capita cash = cash pay / headcount =
- [ ] Target modelled TC total = cash pay + S =

## Chain 2 — Workforce decomposition
- [ ] Total headcount / domestic / overseas:
- [ ] R&D headcount:
- [ ] Frontline estimate (stores × staff, plants × shifts, service centres) and basis:
- [ ] Non-R&D professional = total − R&D − frontline − overseas =
- [ ] Equity-recipient anchor: disclosed award holders vs modelled ≥ first-eligible level:
- [ ] Grant-cadence anchor: person-grants in last 12 months:

## Chain 3 — Level → TC calibration
- [ ] Level-pay table source, date, tier:
- [ ] Ageing adjustment (benefit-expense growth − headcount growth):
- [ ] Equity annualisation: value per grantee / vesting years; price basis:
- [ ] First level whose TC mode exceeds threshold:

## Chain 4 — Profit pool → role
- [ ] Segments ranked by gross profit:
- [ ] For each top-3 pool: process that would cut it >10% if it failed → owning role → dependency grade → evidence:

## Chain 5 — Three-band pricing (per critical role, see pay_bands.json)
- [ ] Market band source:
- [ ] Economic band = pool at risk × dependency factor / tenure, capped by affordability:
- [ ] Internal band source:

## Chain 6 — Career graph
- [ ] Transitions collected (n) and whether n ≥ 10 per origin state:
- [ ] Threshold-crossing state:

## Chain 7 — Charter and control
- [ ] Share classes / WVR / founder voting vs economic:
- [ ] Charter document status (original / official_summary / reconstructed):
- [ ] Who approves equity plans; buyback vs award dilution:

## Chain 8 — Sensitivity
- [ ] Senior-band headcount ±25% → Δp50:
- [ ] Equity price basis grant vs market → Δ senior TC:
- [ ] Single document that would most narrow the range:

## Chain 9 - Cross-check results
- [ ] Payroll envelope deviation (validate_bundle.py):
- [ ] If the envelope was not checkable: modelled TC total / revenue = ____ , and why that payroll intensity is plausible for this sector:
- [ ] Equity-recipient anchor deviation:
- [ ] Any revision made after the checks:
