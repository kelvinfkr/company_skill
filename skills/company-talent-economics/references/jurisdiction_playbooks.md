# Jurisdiction playbooks

The machine-readable half of this lives in `assets/jurisdictions.json`: 49 jurisdictions with filing
venues, local document names, registries, currency, threshold prior and employer social rate.
`search_plan.py` reads it directly. This file explains how to *work* each family — what the disclosure
regime actually gives you, and where it misleads.

```bash
python scripts/i18n.py jurisdictions          # every code
python scripts/i18n.py jurisdictions de       # one entry in full
```

If a country is not in the registry, run it as `other`: find the national company registry and the
securities regulator first, then follow the generic six-pass plan. Add the entry once you have located
the venues — it is a data change, not a code change.

## The generic method, in priority order

1. **Statutory accounts** — the payroll envelope line (staff costs / personnel expense / employee benefit expense) and headcount. In much of Europe these exist for private companies too.
2. **The remuneration filing** — nearly every regime has one, and it is the densest pay document in the file: DEF 14A, Vergütungsbericht, IARC, Formulário de Referência item 13, Remuneration Report, 임원 보수 지급, 役員報酬.
3. **The equity plan** — recipient counts and grant sizes tell you who the company itself treats as critical.
4. **Statutory pay-transparency artefacts** — gender pay-gap reports, pay registers, salary ranges in job postings. These are the only lawful window onto non-executive pay in many countries.
5. **The registry extract** — legal form, share classes, ownership history.

## What each regime is unusually good at

**Disclosure that names individuals below board level**
- **India** — Companies Rules 5(2): the ten highest-paid employees, by name and pay. The single best top-tail anchor anywhere.
- **Israel** — the five highest-paid officers, individually.
- **Brazil** — Formulário de Referência gives highest, lowest and average pay for the board and executive bodies.
- **Norway, Sweden, Finland** — public tax or income data. Usable as aggregate calibration; never publish an individual's pay from it.

**Disclosure that anchors the whole distribution**
- **United States** — the CEO pay-ratio names the *median employee's* total compensation. That is a direct read on the middle of the distribution, not an inference. State-level transparency laws (CA, CO, NY, WA, IL) put real ranges in job postings.
- **Japan** — 有価証券報告書 discloses average annual pay (平均年間給与) and headcount, often by segment.
- **Korea** — 사업보고서 discloses average pay by gender and every individual above KRW 500m.
- **Taiwan** — listed issuers publish non-managerial employee headcount plus average *and median* pay.

**Private-company accounts that are actually public**
- **United Kingdom** — Companies House publishes statutory accounts for private companies; average staff cost and headcount sit in the notes.
- **Belgium** — the NBB Balanscentrale files staff cost and FTE for essentially every company.
- **Sweden, Denmark, Norway, Finland** — Årsredovisning / Årsrapport carry personnel costs and average FTE.
- **France** — the bilan social and the index d'égalité professionnelle give headcount and pay structure.

**Where the charter and control structure is the workstream**
- **Hong Kong** — WVR/dual-class structures change what an equity grant is worth in control terms.
- **Mainland China** — CNINFO prospectuses and inquiry responses reconstruct early charter history that is otherwise unavailable.
- **Germany, Switzerland** — say-on-pay makes the remuneration report detailed and contested, therefore reliable.

## Where each regime misleads

- **Denmark** — employer social cost is near zero because it is funded through income tax. Applying a continental rate of 20-30% inflates the envelope by a fifth.
- **UAE, Saudi Arabia and the Gulf** — statutory pension applies to GCC nationals only. Expatriate staff carry end-of-service gratuity instead. Model the two populations separately or the payroll envelope is wrong for most of the workforce.
- **Mainland China** — 支付给职工的现金 (cash-flow statement) excludes share-based compensation; 职工薪酬 (income statement note) includes it. They are not interchangeable, and mixing them silently double-counts or drops equity.
- **Argentina, Türkiye, Egypt, Nigeria** — a local-currency threshold without an FX date is meaningless within a quarter. State the date or quote in USD.
- **Russia** — disclosure has thinned since 2022 and issuers may hold publication exemptions. Absence of a filing is not evidence of absence of the fact.
- **Everywhere** — registered capital is not valuation and not payroll capacity. Headcount "including outsourced and dispatch workers" is not payroll headcount.

## Private companies, any country

Public evidence is thinner and the intervals must widen. Prioritise:

- deposited statutory accounts, wherever the country publishes them (see above — this is the biggest single differentiator between jurisdictions);
- financing announcements with post-money valuation when disclosed;
- pre-IPO filings if any exist;
- official headcount statements from the company itself;
- public job openings with pay ranges;
- reputable recruiting reports;
- public professional profiles, for aggregate career graphing only.

Do not convert illiquid private equity into cash-like TC without explicitly modelling liquidity and
valuation risk. When gross profit or the payroll line genuinely is not public, use the Phase 1
`NOT AVAILABLE:` declaration: the run continues, marked provisional, on the substitute TC/revenue
affordability check. That is an honest label, never a licence to invent the missing number.
