# Research and evidence protocol

## Eight search passes

1. **Entity:** legal employer, parent, subsidiaries, ticker, BU, brand, product, site, jurisdiction.
2. **Solvency:** cash, debt maturity, covenants, refinancing, going concern, working capital, capex, fundraising, credit.
3. **Profit pools:** segment/product/geography/channel revenue, gross/contribution/operating profit, orders, backlog, retention, inventory, returns, customer concentration.
4. **Targets:** restructuring, severance accrual, savings, productivity, margin, synergy, shared services, delayering, footprint optimization.
5. **Lifecycle:** launches, cancellations, end-of-life, sale/spin-off, research-only transfer, wins/losses, departures, investment.
6. **Workforce demand:** careers pages and snapshots, replacement hiring, freezes, closures, outsourcing, automation, location transfer, vendors, headcount.
7. **Governance:** ownership, incentives, letters, earnings calls, prior restructurings, allocation after misses, turnover, redeployment.
8. **Contradictions/base rates:** expansion, new budgets/contracts, protected work, same-role hiring, independent reports, prior events, peers.

## Query templates

```text
"Company" restructuring OR severance OR workforce reduction
"Company" cost savings OR productivity OR margin target
"Company" segment revenue gross profit operating profit
"Product" discontinued OR roadmap OR strategic review
"Company" hiring freeze OR office closure OR outsourcing
"Company" debt maturity OR covenant OR cash flow
"Company" CEO CFO interview headcount allocation
site:official-regulator-domain "Company" layoff-notice-term
```

Combine company, subsidiary, BU, product, site, and local-language terms.

## Evidence ledger

Store one claim per row with claim ID/text/type, level, direction, event/publication dates, source title/URL/type/tier, independence group, confidence, and notes.

Claim types: `observed_fact`, `candidate_report`, `derived_metric`, `model_assumption`, `inference`.

Source tiers:

- A: audited/regulatory filings, statutory notices, court/government records, disclosed binding contracts.
- B: official calls, announcements, job postings, biographies, government datasets.
- C: reputable independent journalism and industry datasets.
- D: public professional profiles, recruiting databases, trade/community reports.
- E: anonymous forums and unverified posts; use only as weak leads.

Ten syndicated articles tracing to one anonymous claim count as one independence group.

## Temporal discipline

Record event and publication dates. For backtesting, use only evidence available before cutoff. A statutory notice may confirm near-term action but be a weak early-warning feature.

## Contradiction protocol

For every material risk-up claim search continuing same-role hiring, funded launches, new contracts, site expansion, protection/retention, and stronger contribution/cash evidence. Explain whether it contradicts the thesis or indicates skill/location substitution.

## Stop condition

Stop when each material conclusion has a primary or credible independent source and cross-check, or further public search is unlikely to reduce uncertainty. List inaccessible or nonexistent evidence that matters.
