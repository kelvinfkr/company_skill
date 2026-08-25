# Modeling and calibration

## Competing risks

Estimate structural redundancy, BU/product/site closure, contract/internship/probation/vendor non-renewal, performance-system exit, and redeployment separately.

For structural risk use:

`P(action) x P(unit affected | action) x P(role reduced | unit) x P(person selected | role)`

Each probability needs an evidence explanation and prior. Do not multiply arbitrary scores.

Combine nonexclusive exit hazards with an explicit dependence assumption. The packaged estimator uses an independence approximation for scenario analysis:

`1 - product(1 - component hazard)`

Flag overlap and widen intervals. Do not present the combination as a statutory-layoff probability.

## Priors

Choose priors by country/employment mechanism, industry/cycle, company stage/leverage/ownership, role family, horizon, and whether restructuring is already active.

Without a validated prior, call the number a scenario prior and report an ordinal band.

## Evidence and confidence

Formal action, funded/cancelled roadmaps, statutory notices, covenant pressure, and explicit cost targets outweigh sentiment, stock price, and anonymous commentary.

Assess confidence separately from risk using economic coverage, BU identification, role dependency, local-signal quality, source independence, prior calibration, contradiction resolution, and horizon stability.

## Calibration dataset

Build event panels with cutoffs before announcements and include non-events. Segment by jurisdiction, company type, role family, and active-restructuring state.

Evaluate Brier score, log loss, calibration curves, precision-recall, lead time, BU/role ranking, and performance versus sector/company-history baselines.

Use time-based and company-grouped validation. Prevent leakage from later articles, updated headcount, post-cutoff notices, or known affected departments.

## Scenario output

Report low/base/high or p05/p50/p95 for 3/6/12 months. Show assumptions that move the estimate most, such as non-labor savings, continued product funding, location substitution, contract expiry, or redeployment.

Use labels only as communication aids: low, low-moderate, moderate, moderate-high, high, or very high/active process. Do not hard-code universal cutoffs without population-specific calibration.
