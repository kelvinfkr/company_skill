# Evidence scoring

Score each evidence item on source quality, specificity, recency and directness.

## Tiers
- A: regulator/exchange filing, audited financial statement, prospectus, official charter, official equity plan, official job posting.
- B: official company page, government registry/record, court/public record, named executive biography.
- C: reputable compensation dataset, recruiting database, reputable journalism.
- D: public professional profile, conference bio, recruiting/community report.
- E: anonymous/unverified forum post.

## Confidence fields
Record:
- `source_tier` A-E;
- `observed_date` and `published_date`;
- `entity_specificity` company / BU / role / level / geography;
- `claim_type` observed_fact / derived_metric / assumption / inference / reconstruction;
- `confidence` high / medium / low;
- `cross_check_count`.

Never use Tier E as the sole basis for a material estimate. Historical governance reconstructed from later legal opinions should be labeled `reconstruction` even when the legal opinion itself is Tier A.
