# Reasoning chains

Write these out explicitly in `analysis_notes.md` before populating `report.json`. Each chain ends with a number, a range, or a documented "not estimable". Numbers below use Xiaomi FY2025 as a worked example (see `examples/xiaomi/`).

## Chain 1 — Payroll envelope (top-down ceiling)

1. Employee benefit expense `E` (Tier A). Xiaomi: 30.47 bn CNY.
2. Subtract SBC `S` (Tier A) → cash-and-benefits `E_c = E − S`. 30.47 − 5.37 = 25.10 bn.
3. Remove employer social insurance/housing fund. PRC rule of thumb: 15–25% on top of cash pay, capped per city; use 18% for Beijing-heavy HQ unless disclosed. `Cash pay ≈ E_c / 1.18` ≈ 21.3 bn.
4. Per-capita cash pay = cash pay / headcount. 21.3 bn / 56,531 ≈ 376k.
5. Annualised equity per capita ≈ S / headcount as a floor (accounting basis) ≈ 95k; mark-to-market may differ.
6. Result: the modelled bucket TCs, weighted by headcount, must sum to within ±10% of `cash pay + S`. If not, the bucket split or the level-pay table is wrong — revise before proceeding.

## Chain 2 — Workforce decomposition (bottom-up)

1. Start from disclosed function counts (R&D personnel, sales, production) and geography split.
2. Estimate frontline population from physical footprint: stores × staff/store, factories × shifts, call-centre scale. Xiaomi: ~18,000 stores are mostly franchised/partner-run, so only a fraction are employees; the EV plant and delivery centres add thousands.
3. Remaining non-R&D professionals = headcount − R&D − frontline − overseas.
4. Split each function by level using a pyramid prior (entry ≈ 55–60%, mid ≈ 30–35%, senior ≈ 8–10%, director ≈ 2–3%, exec < 0.3%) and adjust with two anchors:
   - **equity-recipient anchor**: number of employees holding share awards ≈ population at and above the first equity-eligible level. Xiaomi: 16,572 holders vs modelled ≥16-level ≈ 16,800.
   - **grant-cadence anchor**: annual grantees (3,877 + 2,496 + 3,334 ≈ 9.7k person-grants in 2025) vs the population you expect to receive a grant each year.
5. Keep bucket headcounts as triangular ranges, never points.

## Chain 3 — Level-to-TC calibration

1. Collect a level-pay table from Tier C/D/E sources. Record its date; it is a snapshot.
2. Age the table: if disclosed benefit expense grew faster than headcount, shift cash bands by roughly (expense growth − headcount growth). Xiaomi 2025: +33% expense vs +≈16% headcount → +5–10% per level.
3. Annualise equity per level: recent grant value per person ÷ vesting years (Xiaomi share awards: 4–10 year vesting; use 4 for annualisation unless the schedule is disclosed), then state the price basis (grant date vs report date).
4. Convert each level to a TC triangle (low/mode/high) or directly to `p_exceed` for the threshold. Use `tc` triangles when the band straddles the threshold; use `p_exceed` when the band is clearly above or below.
5. Sanity: per-capita TC of the modelled pyramid should reproduce Chain 1 within ±10%.

## Chain 4 — Profit pool → role dependency

1. Rank segments by gross profit (not revenue) and by gross-profit growth.
2. For each of the top pools, ask: which process, if it failed for a quarter, would cut this pool by >10%? Name the role that owns that process.
3. Grade dependency: `extreme` (single bottleneck, months to replace, no internal successor), `high`, `medium`, `low`. Cite the evidence (org announcement, patent, product credit, hiring pattern).
4. Flag pools where headcount is small relative to profit (Xiaomi internet services: 28.6 bn CNY gross profit at 76.5% margin from a small workforce) — these are the roles most likely underpaid relative to economic justification.

## Chain 5 — Three-band pricing for a critical role

1. Market replacement band: external offers for equivalent scope at peer companies, adjusted for geography and equity liquidity.
2. Economic justification band: `(profit pool at risk × dependency factor) / expected tenure`, capped by affordability (operating profit, payroll ratio). Dependency factor: extreme 5–10%, high 2–5%, medium 0.5–2%.
3. Internal-equity band: what adjacent native levels and disclosed director pay imply.
4. Intersect with `pay_band_diagnostic.py`; interpret the diagnostic (overlap / market_above_economic / internal_below / internal_above).

## Chain 6 — Career graph

1. Pull transitions from executive bios, appointment announcements, and public profiles.
2. Normalise to the native level ladder; record months in prior state when dated.
3. Report shares only when `n ≥ 10` per origin state; otherwise report paths qualitatively.
4. Identify the first state whose TC mode exceeds the threshold — that is the "threshold-crossing state".

## Chain 7 — Charter and control

1. Identify legal form, issuer domicile, listing venue, share classes.
2. For each governance claim, tag `original` / `official_summary` / `reconstructed`.
3. Connect control to compensation: who approves equity plans, whether founder control changes grant behaviour, whether buybacks offset dilution from awards.

## Chain 8 — Sensitivity

Vary, one at a time: senior-level headcount (±25%), equity price basis (grant vs market), equity coverage at the first eligible level, level-pay table age. Report which one moves the p50 most and what single document would resolve it.

## Chain 9 — Cross-check results

Write the result of every check, including the ones that failed, and what you changed because of them.

1. **Payroll envelope.** Modelled TC total vs `(benefit expense − SBC)/(1 + employer social rate) + SBC`.
   Within ±10% or revise `levels.json`. Use the *disclosed* employer social rate when there is one — the
   registry prior runs from ~1% (Denmark) to ~32% (Spain), and the wrong rate breaks the identity silently.
2. **When the envelope cannot be run** — no disclosed benefit expense, the normal case for unlisted
   entities — record the substitute ratio `build_model.py` prints: modelled TC total ÷ revenue. State why
   that payroll intensity is plausible for this sector. It is a plausibility bound, not an identity: above
   100% of revenue the model is impossible; above roughly 60% it is implausible for most sectors and needs
   an argument. With neither payroll nor revenue, say plainly that no affordability check was possible and
   keep the run provisional.
3. **Equity-recipient anchor.** Modelled headcount at or above the first equity-eligible level vs the
   disclosed number of award holders.
4. **Grant cadence.** Person-grants disclosed in the last 12 months vs the modelled eligible population.
5. **Seniority mix.** Implied mix vs the mix visible in public job postings and profiles.
6. **Ceiling.** Compensation ceiling against gross profit and operating profit.
7. **Revisions.** What you changed after the checks, and what still does not reconcile.

## Failure modes to check before delivery

- Title equated with level without evidence.
- Tier E salary tables presented as observed facts.
- Outsourced/dispatch workers mixed into payroll headcount, or excluded from frontline estimates.
- Parent vs subsidiary headcount or payroll mixed.
- Fiscal year, currency, or pre-/post-tax mismatch between sources.
- Employee benefit expense treated as take-home cash (it includes employer social insurance and SBC).
- Grant-date equity value treated as annual income.
- Search snippets cited instead of the fetched primary document.
- Promotion "probabilities" reported from a handful of public profiles.
- A provisional run (a required figure declared NOT AVAILABLE) presented with the confidence of a measured one.
- The report written in a different language from the one the user asked in.
