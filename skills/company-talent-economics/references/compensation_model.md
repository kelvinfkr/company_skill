# Compensation model

Model annual pre-tax total compensation (TC) as components rather than one number:

`TC = base + expected_bonus + expected_commission + annualized_equity + other_cash`

## Evidence hierarchy by component
- base: official job range > company recruiting > compensation datasets > community reports;
- bonus/commission: official plans or role-specific recruiting first;
- public-company equity: annualized vested or grant-date fair-value approach, clearly labeled;
- private-company equity: show nominal and risk-adjusted value separately; never treat it as cash.

## Bucket design
Use `function x native_level x geography`, and add BU when business economics differ materially. Keep company-native levels separate from normalized latent states.

## Distribution
Prefer observed p25/p50/p75/p90 when sample size is credible. Otherwise use low/mode/high or direct `p_exceed` intervals. Widen uncertainty for sparse senior roles, sales commission, or private equity.

## Affordability cross-check
Compare modeled payroll with disclosed employee cash payments/benefit expense and share-based compensation. If modeled payroll is materially impossible, revisit headcount mix, level mapping or TC assumptions.
