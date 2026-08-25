---
name: estimate-layoff-risk
description: Estimate an employee, intern, contractor, or role group's 3/6/12-month involuntary job-loss risk from public company evidence and an adaptive candidate interview. Use for questions about layoff probability, role redundancy, business-unit closure, contract non-renewal, performance exits, reorganization exposure, or which jobs are safer during cost cuts. Reconstruct business economics and profit pools first, trace them through critical processes and roles, model leadership's observable allocation regime, and produce an auditable probability range rather than a false-precision verdict.
---

# Estimate Layoff Risk

Treat job-loss risk as a causal resource-allocation problem, not sentiment analysis.

Use this chain:

`business model -> profit pools -> cash/margin pressure -> allocation decision -> business unit -> critical process -> role family -> employment mechanism -> individual exposure`

## Non-negotiable boundaries

1. Define the outcome before estimating it. Separate mass layoff, unit closure, role redundancy, performance termination, site closure, contract non-renewal, internship ending, and redeployment.
2. Use only public, legally accessible external information plus facts the candidate voluntarily provides. Never request confidential documents, credentials, private coworker data, or access-controlled material.
3. Do not ask for or use protected or highly sensitive traits such as race, ethnicity, sex, pregnancy, disability, health, religion, political affiliation, union membership, family status, or age except a legally necessary age-of-majority check. Do not use proxies for them.
4. Do not infer a private person's performance, compensation, health, relationships, or legal status. Treat self-reported performance evidence as optional and uncertain.
5. Distinguish `observed_fact`, `candidate_report`, `derived_metric`, `model_assumption`, and `inference` in the evidence ledger.
6. Give probability intervals and confidence. If calibration evidence is insufficient, report an ordinal risk band with a scenario range, not a pseudo-statistical percentage.
7. Analyze leadership through observable allocation behavior and governance incentives, never personality diagnosis or cultural stereotype.
8. This is decision support, not a guarantee or legal opinion. Search current jurisdiction-specific law when legal consequences matter.

## Default deliverables

Create a case directory containing:

- `case.json` - scope, entity, role, employment type, location, horizons;
- `candidate_answers.json` - voluntary answers with date, provenance, and confidence;
- `public_evidence.jsonl` - claim-level evidence;
- `source_manifest.csv` - every source searched or used;
- `profit_pools.json` - segment/product/channel economics and strategic-option assessment;
- `dependency_graph.json` - profit pool to process to team to role mapping;
- `model.json` - risk-layer assumptions and sensitivity;
- `report.json` - structured report source;
- `report.pdf` - default user-facing report.

Initialize with:

`python scripts/init_case.py --company "Company" --role "Role" --country "Country" --employment-type employee --out runs/company-role-YYYY-MM-DD`

## Workflow

### Phase 0 - Define scope and competing outcomes

Identify the legal employer, parent/subsidiary, business unit, product, geography, worksite, role family, employment type, reference date, and 3/6/12-month horizons.

Treat these as competing risks:

- enterprise-wide workforce action;
- BU/product/site closure or material contraction;
- process redesign, outsourcing, automation, or location transfer;
- role-family reduction;
- person selection within a reduced role family;
- performance process;
- contract, internship, probation, or vendor non-renewal;
- redeployment instead of separation.

Do not equate non-renewal with a statutory layoff. Report them separately and optionally combine them as `any_involuntary_exit`.

### Phase 1 - Run the adaptive interview

Read `references/interview_protocol.md` and `references/role_playbooks.md`.

Ask the 12 core questions in two short rounds, then only the relevant employment-type and role-family branches. Ask 12-25 questions total in normal cases. Ask follow-ups only when they can materially change the risk interval.

Generate a question set when useful:

`python scripts/questionnaire.py case.json -o questionnaire.json`

For every answer record the answer, observation date, provenance, candidate confidence, and whether the candidate consents to include it in the report.

Prefer objective signals over anxiety labels. Ask what changed in budget, roadmap, workload, hiring, reporting lines, customer commitments, and future tasks.

### Phase 2 - Route the company and economic model

Read `references/profit_pool_model.md`.

Classify the company before searching: public/private, startup, founder-controlled, diversified, PE-owned/highly leveraged, manufacturing/hardware, software/platform, project/services, regulated finance/utility, biotech/long-cycle R&D, or public/nonprofit/state-owned.

Select the correct economic denominator. Prefer contribution profit, gross profit, cash generation, backlog, utilization, plant load, funding runway, or regulatory mandate over raw revenue when appropriate.

### Phase 3 - Search in eight evidence passes

Read `references/research_and_evidence.md` and `references/jurisdiction_playbooks.md`.

Generate the initial plan:

`python scripts/search_plan.py case.json -o search_plan.json`

Run distinct passes for:

1. entity, legal employer, parent, subsidiaries, BU, product, and worksite;
2. solvency, cash runway, debt, covenants, financing, and working capital;
3. company/segment revenue, gross profit, contribution, operating profit, and guidance;
4. margin targets, restructuring charges, synergy commitments, and capital allocation;
5. BU/product lifecycle, customers, orders, roadmap, launches, cancellations, and strategic priority;
6. workforce, payroll, job postings, hiring freezes, location moves, outsourcing, and automation;
7. governance and leadership allocation history;
8. contrary evidence and comparable-company base rates.

Prefer primary sources. Deduplicate syndicated stories by underlying claim and origin. Record unavailable but decision-relevant sources.

### Phase 4 - Reconstruct profit pools and cost pressure

Build a profit-pool table by material `product x geography x channel x customer type x lifecycle` combinations.

For each pool estimate ranges for revenue, gross/contribution profit, cash conversion, growth, orders/retention, inventory, customer concentration, incremental investment, avoidable cost, shared-platform dependency, strategic option, regulatory value, and management commitment.

Classify the action regime as `survival`, `margin_reset`, `capital_reallocation`, `integration`, `demand_capacity`, `performance_system`, or `mixed`.

Do not assume a currently loss-making business is disposable. Estimate future contribution, option value, synergy, required follow-on investment, and probability management still funds the next milestone.

### Phase 5 - Build the dependency graph

Map:

`profit pool -> critical process -> product/project/customer/site -> team -> role family -> employment bucket`

For each node assess value at risk, time until damage, redundancy, automation/outsourcing/transfer feasibility, minimum viable staffing, recovery time, knowledge loss, regulatory/safety/security obligations, and whether headcount cost is actually avoidable.

Estimate the role's layoff net benefit conceptually:

`PV(avoidable loaded cost) - PV(lost contribution + execution risk + rehiring + knowledge + option value)`

Use ranges. Never fabricate individual contribution numbers.

### Phase 6 - Model leadership as an allocation regime

Read `references/leadership_regimes.md`.

Infer weights from repeated decisions, governance, compensation metrics, budget allocation, executive turnover, and responses to prior misses. Assess centralization, strategic stability, cash/margin discipline, tolerance for long-cycle options, performance mechanism, redeployment propensity, and communication predictability.

Use leadership only to update how and when cuts propagate. Operational evidence, formal targets, and product decisions dominate leadership-language evidence.

### Phase 7 - Estimate risk and uncertainty

Read `references/modeling_and_calibration.md`.

For each horizon estimate:

`P(company action) x P(unit affected | action) x P(role reduced | unit affected) x P(person selected | role reduced)`

Then combine structural risk with contract/non-renewal and performance-exit hazards without double counting. Run:

`python scripts/estimate_risk.py model.json -o risk_results.json`

Report component probabilities, `any_involuntary_exit`, redeployment likelihood, evidence coverage, confidence, and the variables that drive interval width.

Numeric output requires a defined outcome/horizon, an appropriate economic model, company-pressure evidence, BU/product and role-dependency assessments, enough candidate answers to locate the role, an explicit prior/base rate, and contradictory evidence. Otherwise provide a provisional map and the next evidence needed.

### Phase 8 - Produce and validate the report

Read `references/report_contract.md` and `references/privacy_and_boundaries.md`.

Populate `report.json`, then render:

`python scripts/render_report.py report.json -o report.pdf`

Render the PDF to images and inspect every page for clipping, broken CJK glyphs, poor pagination, and unreadable tables. Validate the complete bundle:

`python scripts/validate_bundle.py runs/case-directory`

## Reporting rules

- Lead with the 3/6/12-month outcome table and one-sentence diagnosis.
- Show public evidence and candidate-reported evidence separately.
- Explain why the company may cut while profitable, or retain a role inside a loss-making business.
- Include favorable, base, and adverse scenarios.
- State what observable developments would move the estimate up or down.
- Include a candidate-controlled redaction note. Do not expose names or unnecessary personal detail in filenames or report metadata.
- Never advise deception, sabotage, data extraction, or concealment from an employer.

## Packaged resources

- `references/interview_protocol.md` - adaptive question sequence and answer provenance.
- `references/role_playbooks.md` - branch questions and economics by role family and employment type.
- `references/profit_pool_model.md` - Profit-to-Headcount model and company-type routing.
- `references/leadership_regimes.md` - observable leadership allocation regimes.
- `references/research_and_evidence.md` - search passes, evidence grading, and contradiction checks.
- `references/jurisdiction_playbooks.md` - local notice sources and search terms.
- `references/modeling_and_calibration.md` - competing-risk estimation and leakage prevention.
- `references/privacy_and_boundaries.md` - sensitive-data and candidate-control rules.
- `references/report_contract.md` - structured report specification.
- `assets/question_bank.json` and `assets/report_spec.json` - reusable templates.
- `schemas/*.schema.json` - case, evidence, model, and report schemas.
- `scripts/*.py` - initialization, routing, planning, estimation, rendering, and validation.
