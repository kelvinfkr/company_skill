---
name: company-talent-economics
description: Reconstruct a company's compensation distribution, high-compensation population, promotion/hiring paths, and role-specific pay bands from public filings and other public data, and deliver a typeset PDF report. Works for companies in any country and writes the report in the language of the company name the user typed (Chinese, Japanese, Korean, German, Spanish, Arabic and more). Use when asked how much people at a company earn, how many employees exceed a total-compensation threshold, which roles are economically critical, how promotion works, or what a role at a given level should be paid. Starts from segment profit pools and the payroll envelope, then rebuilds the level pyramid, equity awards, and career graph. Public data only; never infers a private individual's pay.
---
# Company Talent Economics

## Operating procedure (follow this literally)

Every run is a directory with a fixed set of files and ten numbered phase gates. Do not skip gates, do not write `report.json` by hand before Phase 8, and do not present anything before Phase 10 passes. `$SKILL` below means the folder containing this file.

```bash
python $SKILL/scripts/init_run.py "<company>" --out ./talent-economics/<slug> --year <FY> \
       [--jurisdiction <code>] [--language <tag>] [--threshold N --currency ISO]
python $SKILL/scripts/check_phase.py ./talent-economics/<slug> --next     # prints the exact steps for the next phase
# ... do the steps ...
python $SKILL/scripts/check_phase.py ./talent-economics/<slug>            # verifies the gate; on pass prints the next phase
```

Repeat `check_phase.py` until `PHASE 10 GATE PASSED`. If a gate fails, fix only what it lists, then rerun. The gate output is the authoritative to-do list; the rest of this file explains *why*.

`--jurisdiction` and `--language` are inferred from the company name when omitted, and both are recorded in `run.json`. Confirm them at Phase 0 — changing either later means recompiling and re-rendering.

Files the harness creates and what you must do with each:

| File | Created by | Your job |
|---|---|---|
| `run.json` | init_run | check `language` / `jurisdiction` / `currency` / `threshold`; fill `entity`, `facts` (millions), `facts_count`, `segments`, each with an `evidence_id` |
| `analysis_notes.md` | init_run | replace every checkbox line with numbers + evidence ids (Chains 1-9) |
| `source_manifest.csv` | init_run | one row per document per pass; status `used` / `calibration only` / `searched, not found` |
| `evidence.jsonl` | init_run (empty) | one JSON line per number used; `claim_type` + `source_tier` mandatory |
| `levels.json` | init_run | headcount triangle per function, band shares, TC triangle per band |
| `model.json`, `population.json` | build_model, estimate_population | never edit by hand |
| `pay_bands.json`, `career_transitions.csv` | init_run | fill in Phases 6-7 |
| `report.json` | compile_report | fill only the `TODO` prose fields after Phase 8 |
| `report.pdf` | render_report | inspect visually, then deliver |

Rules that the scripts cannot check for you:

1. A search snippet is never a source. Fetch the filing, read the section, then write the number.
2. Anything from a forum or salary-crowdsourcing site is Tier E and can only appear as `calibration only`.
3. Never invent a number to satisfy a gate. Leave it `null` and write `NOT AVAILABLE: <fact_key> - <what you searched>` in the notes. For an unlisted entity that passes the Phase 1 gate and marks the whole run **provisional**; the report then says so on its cover and no figure in it may be presented as measured.
4. When unsure which default to use, take it from `assets/defaults.json` or `assets/jurisdictions.json` and say so in the notes.
5. Use the words in `references/glossary.md`, in the language you are writing in. A company has articles/charter, never a "constitution". TC is pre-tax and includes annualised vested equity.

## Language: follow the company name

**Write the report in the language of the company name the user typed.** `ソニーグループ` gets a Japanese report; `Siemens AG` gets a German one; `小米集团` gets a Chinese one. If the user wrote their request in a different language from the company name, **the user's language wins** — they are the reader. Speak to the user in that language too, not only in the PDF.

`init_run.py` resolves this and records it in `run.json -> language`; every later script reads it from there. Explicit `--language` beats `$CTE_LANG`, which beats detection from the name.

Read `references/localization.md` before Phase 0. The two things it settles:

- **Detection confidence.** `python $SKILL/scripts/i18n.py detect "<name>"` reports `high` / `medium` / `low` / `ambiguous`. On `low` or `ambiguous` — plain Latin names, or a legal form like `S.A.` that four languages share — do not silently default to English. Use the language the user wrote in; if that is also unclear, ask once, in one line.
- **Any language works.** Twelve languages have a locale pack for the report's structural labels (`en zh-CN zh-TW ja ko es fr de pt it ru ar`). Any other language still gets a full report in that language, with the structural labels falling back to English and a note printed. Adding a pack is one JSON file: `python $SKILL/scripts/check_locales.py --new <tag>`.

Search in two languages, always: filings are indexed under their local names, cross-border coverage under English ones. `search_plan.py` does this automatically.

Do not translate the company's own words. Native titles, level names, segment names and charter terms stay in the original language with a translation in parentheses on first use.

## Country: route by jurisdiction, not by assumption

`assets/jurisdictions.json` holds 49 jurisdictions with filing venues, local document names, registries, currency, a default high-pay threshold and an employer social-contribution rate.

```bash
python $SKILL/scripts/i18n.py jurisdictions          # list every code
python $SKILL/scripts/i18n.py jurisdictions japan    # one entry in full; aliases resolve
```

Two of those fields are **priors, not facts**, and every override belongs in `analysis_notes.md`:

- `threshold_default` is the round local number that reads as "high earner" in that market (CNY 1,000,000, JPY 20,000,000, USD 250,000, INR 10,000,000). It is not a statistical cut-off and is not comparable across countries at market FX. A user-supplied threshold always wins.
- `employer_social_rate` ranges from roughly 1% (Denmark, funded through income tax) to roughly 32% (Spain). Applying the wrong one silently breaks the payroll envelope. Use the disclosed number whenever the filing gives one.

An unmapped country routes to `other`: find the national registry and securities regulator first, then run the generic six-pass plan. Read `references/jurisdiction_playbooks.md` for what each regime is unusually good at and where it misleads.


Analyze talent as part of the company's economic system, not as a generic salary benchmark.

The central causal chain is:

`business model -> profit pools -> critical processes -> critical roles -> org/level structure -> market replacement cost -> compensation distribution -> promotion/hiring paths`

A title is not a salary. Two people at the same nominal level may rationally receive very different compensation if they control different profit pools, customer relationships, technical bottlenecks, or scarce capabilities.

## Default scope

If the user gives only a company name:

- analyze the most recent public information available;
- use the company's main operating geography, but segment materially different geographies;
- define total compensation (TC) as base salary + expected cash bonus/commission + annualised vested equity value, pre-tax, in the reporting currency; state the equity price basis (grant-date or report-date);
- separately show cash TC and equity-inclusive TC when equity is material;
- take the high-compensation threshold from `assets/jurisdictions.json` for that jurisdiction (a round local-currency number that reads as "high earner" there), state it explicitly on the cover, and let any user-supplied threshold override it; in a high-inflation economy state the FX date or quote in USD;
- include employees and executives, exclude founders from employee-distribution statistics unless the user asks otherwise.

## Non-negotiable rules

1. Use only public, legally accessible sources. Never bypass login walls, CAPTCHAs, robots restrictions, or access controls.
2. Prefer official filings, prospectuses, annual reports, exchange filings, company job postings, and formal compensation/equity disclosures.
3. Public professional profiles may be used to infer aggregate role taxonomy and career transitions, never a private person's exact pay.
4. Tag every claim in the evidence ledger with a canonical key: `observed_fact`, `derived_metric`, `assumption`, `inference` or `reconstruction`. Write those same English keys into `report.json`; `render_report.py` prints the label for the report's language (披露 / Disclosed / Offengelegt / 開示 ...). `validate_bundle.py` accepts either form in `report.json` and only the canonical key in `evidence.jsonl`.
5. Never present inferred company-wide counts or promotion probabilities as exact. Give ranges and confidence.
6. Do not equate title with level without evidence. Maintain company-native titles and a separate normalized latent-role representation.
7. Do not infer compensation solely from market salary sites. Company economics and internal pay capacity are separate constraints.
8. If evidence is weak, widen intervals and report the missing evidence that would most reduce uncertainty.
9. Use the terminology in `references/glossary.md`, in the language you are writing in: use that language's accounting and corporate-law term, never its colloquial one. A company has articles/charter (章程 / Satzung / statuts / 定款 / 정관 / устав), never a "constitution"; employee benefit expense is not take-home pay; a grant is not a vest; observed transition shares are not promotion probabilities.
10. Cite fetched primary documents, not search snippets. A snippet is a pointer to a document that must then be read.

## Final deliverable contract

The default user-facing artifact is **`report.pdf`**, not raw Markdown.

Always build the analysis in an auditable structured form, then typeset it:

- `analysis_notes.md` - the written-out reasoning chains (see `references/reasoning_chains.md`) with intermediate numbers; produced before `report.json`;
- `report.json` - structured report model used by the renderer;
- `evidence.jsonl` - claim-level evidence ledger;
- `source_manifest.csv` - every source searched/used, with date and source type;
- `model.json` - headcount/TC assumptions used by estimators;
- `career_transitions.csv` - observed public-profile transitions when used;
- `report.pdf` - final polished deliverable.

The final PDF must **not** be generated by directly converting Markdown. Populate `report.json` using `assets/report_spec.json` (including `meta.language`), run `scripts/validate_bundle.py <dir>`, then run `scripts/render_report.py report.json -o report.pdf`. The renderer builds a typeset DOCX internally and converts that document to PDF, choosing section titles, table headers, number formatting, fonts and text direction from `meta.language`. Keep the DOCX only when explicitly requested with `--keep-docx`.

Before delivery, visually inspect the rendered PDF: clipped tables, tofu boxes where the script's font is missing, orphaned headings, pagination. For Arabic and Hebrew, confirm the mirrored layout actually rendered. `render_report.py` warns on stderr when no installed font covers the report's script — install the font rather than shipping boxes.

## Company-type routing is mandatory

Before searching compensation data, read `references/company_type_router.md` and classify the entity. The source plan must change by company type. Charter and control-structure sources are a separate workstream (Pass 1), not an optional appendix.

For historical charters, use one of three statuses:

- `original` - actual charter/articles/amendment obtained;
- `official_summary` - official filing describes the terms but original document is not attached;
- `reconstructed` - terms inferred from later prospectus/legal opinion/registry history.

Never present reconstructed wording as original charter text.

## Required output

Produce these sections unless the user requests a narrower analysis:

1. **Executive estimate** — workforce, median/upper-tail TC, employees above threshold, confidence.
2. **Charter and control structure** — legal form, share classes, founder economic ownership vs voting power, board control, charter document status.
3. **Business economics** — revenue, gross profit, operating profit, major segments/profit pools, customer concentration, payroll/R&D/sales intensity.
4. **Profit-pool → role dependency map** — which processes and roles appear to create, defend, or unlock each profit pool.
5. **Organization map** — functions, business units, management layers, IC/manager tracks, native levels where observable.
6. **Compensation distribution** — cash and equity-inclusive TC by function x level x geography, with p25/p50/p75/p90 or defensible ranges.
7. **High-compensation population** — estimated count and share above threshold, decomposed by bucket.
8. **Role pay bands** — for economically important roles, show market replacement band, economic-justification band, and recommended/defensible overlap.
9. **Career graph** — observed internal promotions, external-entry routes, typical tenure between states, and the first states that usually cross the target TC.
10. **Equity incentives & talent capital allocation** — equity incentives, dilution, share-based compensation, executive pay, and who receives ownership.
11. **Evidence & uncertainty** — source ledger, confidence, sampling biases, and sensitivity.

## Workflow

### Phase 0 — Resolve the entity, language and jurisdiction

First confirm the three fields `init_run.py` inferred, because everything downstream depends on them:

- `run.json -> language` — the language you will write in. Inferred from the company name; if the user wrote to you in another language, theirs wins. Fix it now, not at Phase 10.
- `run.json -> jurisdiction` — decides which filing venues Phase 1 searches. `python $SKILL/scripts/i18n.py jurisdictions <code>` shows what that maps to.
- `run.json -> currency` and `threshold` — priors from the registry. State the threshold on the cover; a user-supplied one always wins.

Then identify:

- legal entity and major subsidiaries;
- listed ticker/exchange if applicable;
- private/public status;
- jurisdiction;
- reference date;
- relevant business units and geographies.

Do not mix parent-company and subsidiary headcounts or compensation without labeling them.

Classify the company using `references/company_type_router.md` before launching the search plan. Record the legal form, listing venue, issuer domicile, operating entity, share classes, and whether historical charter documents are expected to be publicly available.

### Phase 1 — Six-pass public-source search

Read `references/source_playbook.md`, `references/jurisdiction_playbooks.md`, and `references/company_type_router.md`.

Use whatever web tools the host agent exposes (Claude Code: `WebSearch` / `WebFetch`; Codex: built-in web search) to run a structured search, not a single query. Fetch primary filings in full rather than relying on search snippets. Run **six separate search passes** with the stop rules in `references/source_playbook.md`: (1) identity & charter, (2) business economics, (3) workforce & payroll, (4) compensation & equity awards, (5) organisation & critical roles, (6) career transitions. `scripts/search_plan.py <company> --jurisdiction <code> --year <FY>` prints the query ladder: venue-scoped `site:` queries built from that jurisdiction's filing venues and local document names, plus six passes of queries in the run's language **and** in English. Search both sides — filings are indexed under their local names, cross-border analyst coverage under English ones. For each pass, search → identify the primary document → fetch it in full → extract numbers with unit, period and page. Search across:

- official filings / annual reports / prospectus / ESG reports;
- investor relations and exchange disclosures;
- company careers pages and current job postings;
- executive biographies and organization announcements;
- equity-incentive and share-based-compensation documents;
- reputable compensation databases and public recruiting ranges;
- public professional histories for aggregate transitions;
- reputable media only for facts not available in primary sources.

Create `evidence.jsonl` matching `schemas/evidence.schema.json` and a `source_manifest.csv`. The manifest must record sources that were searched but unavailable when that absence matters (for example, an early private-company charter).

**When a required figure genuinely is not public** — normal for unlisted entities, where gross profit and the payroll line are often never filed — leave it `null` and write in `analysis_notes.md`:

```
NOT AVAILABLE: <fact_key> - <the venues and queries you actually searched>
```

Use the `run.json` key as `<fact_key>` (`revenue`, `gross_profit`, `employee_benefit_expense`, `headcount`). For an unlisted entity the Phase 1 gate then passes and marks the run **provisional**: `compile_report.py` forces the report's confidence to the locale's provisional wording and prints a cover note naming what was missing. You still need `revenue` or `headcount` — without either there is no scale anchor, and no company-wide distribution may be produced at all. This is a label for honest uncertainty, never a licence to invent the missing number.

Continue searching until each critical output has at least one strong source and major estimates have a cross-check, or until no additional public source is likely to materially reduce uncertainty.

### Phase 2 — Reconstruct company economics and the payroll envelope before salaries

Read `references/company_economics.md` and write Chains 1 and 4 of `references/reasoning_chains.md` into `analysis_notes.md`. The payroll envelope (employee benefit expense − SBC − employer social contributions) is a hard ceiling every later bucket model must respect.

Collect and derive:

- revenue, gross profit, operating profit, net income;
- segment revenue and, when available, segment gross profit / operating profit;
- customer concentration and major-channel dependence;
- employee count, R&D headcount, sales headcount if disclosed;
- employee cash payments / employee benefit expense / share-based compensation;
- R&D, sales, G&A expense;
- revenue, gross profit, and payroll per employee;
- equity incentive grants and dilution.

Build a `profit_pool` table. Do not assume revenue equals value creation; use gross profit / contribution / operating profit when available.

### Phase 3 — Reconstruct organization and critical roles

Read `references/org_dependency_model.md`.

Build role states using two layers:

**Company-native layer**
- native title / level / BU / location / manager-or-IC.

**Latent comparable layer**
- scope: task / project / team / multi-team / function / company;
- decision authority;
- technical depth;
- people responsibility;
- revenue/profit responsibility;
- customer concentration exposure;
- talent scarcity / replacement difficulty;
- equity intensity.

For each major profit pool, trace:

`profit pool -> critical process -> critical role -> likely org node`

Score role dependency qualitatively (`low`, `medium`, `high`, `extreme`) with evidence. Never turn weak evidence into a fake precise score.

### Phase 4 — Build compensation evidence

Read `references/compensation_model.md`.

For each `function x native level x geography` bucket, collect:

- public recruiting salary range;
- executive compensation disclosures;
- employee equity grants / option or restricted-share plans;
- salary database samples;
- commission/bonus structure when relevant;
- external comparable-company observations;
- market supply/scarcity evidence.

Normalize to annual pre-tax TC. Keep components separate:

`cash_base`, `cash_bonus`, `commission`, `equity_annualized`, `other`.

Prefer a distribution or range over a single average. When enough evidence exists, report p25/p50/p75/p90; otherwise report a low/central/high band.

### Phase 5 — Estimate the company-wide compensation distribution

Write Chains 2 and 3 (workforce decomposition, level-to-TC calibration) in `analysis_notes.md` first. Create buckets that jointly cover the workforce. At minimum segment by function and native level band; add geography or business unit when material. Anchor the pyramid with the equity-recipient count and grant cadence when disclosed.

Populate a JSON input using `schemas/company_model.schema.json` and run:

`python scripts/estimate_population.py company_model.json --samples 50000`

The estimator accepts either a direct `p_exceed` interval or a triangular `tc` distribution per bucket.

Report:

- p05/p50/p95 estimated employees above threshold;
- share of workforce above threshold;
- contribution by function/level/geo;
- which buckets dominate uncertainty.

### Phase 6 — Determine what a role should be paid

Read `references/role_pay_bands.md`.

For each critical role, construct three distinct bands:

1. **Market replacement band** — what it costs to hire/retain a credible replacement externally.
2. **Economic justification band** — what the company can rationally pay given profit pool, value-at-risk, dependency, and affordability.
3. **Internal-equity band** — what adjacent roles / current executives / incentive plans imply internally.

Do not mechanically average them.

- If the bands overlap, the overlap is the defensible pay zone.
- If market cost is above economic justification, flag a structural talent-economics problem: the company may not be able to afford the talent it needs.
- If internal pay is materially below the market/economic overlap, flag retention risk.
- If internal pay is materially above both, flag potential overpayment/governance risk.

Use `scripts/pay_band_diagnostic.py` for a transparent intersection/gap calculation when useful.

### Phase 7 — Build promotion and hiring paths

Read `references/career_graph.md`.

From public professional histories, official promotion announcements, executive biographies, job postings, and recruiting materials, create transitions between normalized role states.

Classify each transition:

- `internal_promotion`;
- `internal_lateral`;
- `external_entry`;
- `manager_switch`;
- `exit`.

Record months in prior state when observable and evidence quality. Aggregate with:

`python scripts/career_graph.py transitions.csv`

Report observed path shares and median tenure only when sample size is adequate. Unless the true denominator is known, call them **observed public-profile transition shares**, not company-wide promotion probabilities.

### Phase 8 — Analyze equity and governance as compensation

Read `references/governance_equity.md`.

For public companies and late-stage private companies, collect:

- stock/option/restricted-share pool size;
- new-issue vs treasury-share source;
- vesting/attribution schedule;
- grant price vs market price;
- share-based compensation expense;
- executive/director grants;
- number and type of employee recipients;
- dilution and voting-right consequences when relevant.

Use equity grants as a strong signal of whom the company itself regards as strategically important, but distinguish accounting expense, grant-date fair value, and realized/mark-to-market employee value.

### Phase 9 — Cross-check and sensitivity

Run at least these identities and record each result in `analysis_notes.md`:

- **payroll envelope**: headcount-weighted modelled TC ≈ (benefit expense − SBC)/(1 + employer social rate) + SBC, within ±10% (`validate_bundle.py` checks this). Use the *disclosed* employer social rate when the filing gives one — the registry prior ranges from ~1% (Denmark) to ~32% (Spain), and the wrong one silently breaks this identity;
- **when the envelope is not checkable** (no disclosed benefit expense — normal for unlisted entities): `build_model.py` falls back to modelled TC total ÷ revenue and records it in `run.json -> checks`. That ratio is a plausibility bound, not an identity: above revenue it is impossible, above ~60% it is implausible for most sectors and needs a written justification in Chain 9. If neither payroll nor revenue exists, say plainly in the report that no affordability check was possible;
- **equity-recipient anchor**: modelled population at/above the first equity-eligible level ≈ disclosed number of award holders;
- **grant cadence**: annual person-grants disclosed vs modelled eligible population;

- implied payroll from modeled compensation vs disclosed employee cash/benefit expense;
- modeled high-earner count vs executive/equity-incentive recipient counts;
- implied seniority mix vs public job/profile mix;
- compensation ceiling vs gross profit and operating-profit economics;
- promotion graph vs current hiring strategy (internal build vs external buy).

If the model implies an impossible payroll or seniority structure, revise the assumptions.

### Phase 10 — Compile the PDF report

Populate `report.json` using `assets/report_spec.json` and `schemas/report.schema.json` (top-level key `charter`, not `constitution`; `meta.language` set), run `python scripts/validate_bundle.py <dir>`, then run:

`python scripts/render_report.py report.json -o report.pdf`

The renderer uses a structured JSON -> DOCX -> PDF pipeline and takes every structural label, number format, font and text direction from `meta.language`. Markdown must not be used as the final layout source. The PDF is the default artifact delivered to the user; `report.json` and the evidence bundle are retained for auditability.

Every key number must be tagged as observed, derived, or inferred. Always include a short “what would change this estimate most?” section. Present the report to the user in the run's language — the PDF being localized is not enough if you then summarise it in English.

## Source confidence

Read `references/evidence_scoring.md`.

Default hierarchy:

- **Tier A**: audited filings, prospectus, exchange/regulator filings, official equity plans, official job postings.
- **Tier B**: official company pages, executive biographies, government datasets, court/public records.
- **Tier C**: reputable compensation datasets, credible recruiting databases, reputable journalism.
- **Tier D**: public professional profiles, conference bios, recruiting/community reports.
- **Tier E**: anonymous forums / unverified posts. Use only as weak calibration, never as the sole basis for a material estimate.

## Stop conditions

A numeric company-wide distribution is allowed only when the analysis has:

- a credible workforce denominator;
- a business-economics model;
- a function/seniority decomposition covering most employees;
- compensation evidence for the high-pay buckets;
- at least one payroll or affordability sanity check;
- explicit uncertainty.

Otherwise output a provisional map and a targeted list of missing evidence.

## Running on Claude Code and Codex

This skill is host-agnostic. The same folder works in both:

| | Claude Code | Codex |
|---|---|---|
| Install path | `~/.claude/skills/company-talent-economics/` (global) or `.claude/skills/` (project) | `~/.codex/skills/company-talent-economics/` |
| Invocation | auto-triggered from the `description`, or `/company-talent-economics <company>` | `$company-talent-economics <company>` or auto |
| Web access | `WebSearch`, `WebFetch` tools | built-in web search (enable in config) |
| Shell | `Bash` tool | sandboxed shell; request network/file-write approval when prompted |

Installation is covered in the repository `README.md` (English) and `README.zh-CN.md` (中文): a Claude Code
plugin marketplace entry, `install.sh` for symlink/copy installs into both hosts, and a zip bundle for the
claude.ai Skills uploader. `bash install.sh --check` verifies Python deps, LibreOffice and the fonts for the
scripts you actually need.

Script paths in this file are relative to the skill root; resolve them with the directory that contains
`SKILL.md` (e.g. `$SKILL_DIR/scripts/render_report.py`), never with the current working directory.

Write all working files (`report.json`, `evidence.jsonl`, `report.pdf`, ...) into a per-run output directory
in the user's workspace (e.g. `./talent-economics/<company>/`), not into the skill folder.

If LibreOffice is unavailable, run `render_report.py --docx-only` and tell the user the DOCX needs external
PDF conversion; do not fall back to Markdown-to-PDF.

`python $SKILL/scripts/selftest.py` drives a synthetic run through all ten gates, exercises the unlisted
provisional path, and renders every locale. Run it after changing any script.

## Packaged resources

### Harness
- `scripts/init_run.py` — create a run directory with all templates; resolves language, jurisdiction, currency and threshold.
- `scripts/check_phase.py` — phase gates 0–10 with imperative next-step instructions; the harness spine.
- `scripts/search_plan.py` — six-pass query ladder, venue-scoped and bilingual, driven by the jurisdiction registry.
- `scripts/build_model.py` — `levels.json` → `model.json`, headcount and payroll-envelope checks with a TC/revenue fallback, epistemic `p_exceed`.
- `scripts/estimate_population.py` — Monte Carlo high-compensation population estimator.
- `scripts/pay_band_diagnostic.py` — market/economic/internal band overlap diagnostic.
- `scripts/career_graph.py` — aggregate observed career transitions.
- `scripts/compile_report.py` — fills all numeric sections of `report.json` in the run's language; leaves `TODO` for prose; enforces the provisional label.
- `scripts/validate_bundle.py` — bundle completeness, claim-type vocabulary, terminology and the affordability check, all locale-aware.
- `scripts/render_report.py` — structured JSON → DOCX → PDF renderer; localized chrome, per-script fonts, RTL.
- `scripts/selftest.py` — end-to-end test of all ten gates, the provisional path and every locale.

### Localization
- `scripts/i18n.py` — language detection, locale packs, jurisdiction registry, locale-aware formatting. CLI: `detect`, `locales`, `jurisdictions`.
- `scripts/check_locales.py` — validate locale packs and the jurisdiction registry; `--new <tag>` scaffolds a pack.
- `locales/*.json` — 12 chrome locale packs (`en zh-CN zh-TW ja ko es fr de pt it ru ar`).
- `assets/jurisdictions.json` — 49 jurisdictions: filing venues, local document names, registries, currency, threshold prior, employer social rate, and what each regime gets right or wrong.
- `assets/search_terms.json` — search vocabulary per language for `search_plan.py`.
- `references/localization.md` — how language and country resolution works, and how to add either.

### Method references
- `references/glossary.md` — exact terminology and definitions; mandatory.
- `references/reasoning_chains.md` — the nine written-out reasoning chains with a worked example; mandatory before `report.json`.
- `references/company_type_router.md` — route research by legal/listing type.
- `references/source_playbook.md` — structured search sequence and query recipes.
- `references/jurisdiction_playbooks.md` — what each disclosure regime is unusually good at, and where it misleads.
- `references/company_economics.md` — profit-pool and affordability reconstruction.
- `references/org_dependency_model.md` — organization and role-dependency model.
- `references/compensation_model.md` — TC normalization and distribution estimation.
- `references/role_pay_bands.md` — market/economic/internal pay-band logic.
- `references/career_graph.md` — promotion and hiring transition methodology.
- `references/governance_equity.md` — equity incentives, dilution, and talent ownership.
- `references/evidence_scoring.md` — source/evidence confidence rules.

### Templates and schemas
- `assets/defaults.json` — priors (pyramid shares, vesting years, dependency factors, tolerances).
- `assets/report_spec.json` — structured report model template.
- `assets/report_layout.md` — PDF layout requirements for the renderer.
- `assets/analysis_notes_template.md`, `assets/CHECKLIST.md` — fill-in reasoning template and delivery checklist.
- `schemas/report.schema.json` — report JSON validation schema.
- `schemas/company_model.schema.json` — population-estimator input schema.
- `schemas/evidence.schema.json` — evidence-ledger schema.
- `agents/openai.yaml` — Codex UI metadata for the skill list and invocation chip.
- `requirements.txt` — Python dependency (`python-docx`); every other script is standard library only.

### Examples
- `examples/demo_report.json` and `examples/demo_report.pdf` — fictional renderer smoke-test fixtures.
- `examples/xiaomi/` — complete real-company worked example (Xiaomi FY2025): `model.json`, `report.json`, evidence ledger, manifest, transitions, rendered PDF. Use it as the reference for expected depth and file layout.
- `examples/fictional_robotics_company.json`, `examples/fictional_pay_bands.json`, `examples/fictional_transitions.csv` — runnable estimator examples.
