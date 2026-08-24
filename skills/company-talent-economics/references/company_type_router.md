# Company-type source router

Classify the legal/listing structure before research. The classification controls which governance and compensation sources to search first.

## Router

| Type | Typical identity | Charter/governance sources | Economics/compensation sources | Special cautions |
|---|---|---|---|---|
| `cn_a_share` | PRC listed on SSE/SZSE/BSE | current articles, historical articles/amendments when disclosed, IPO prospectus, inquiry replies, shareholder-meeting notices/results, board rules, equity-incentive plans | annual/semiannual reports, employee tables, cash paid to employees, R&D, executive pay, SBC/equity incentive, job postings | one-share-one-vote is common, but STAR/ChiNext may have special voting-right structures established pre-listing |
| `cn_pre_ipo_joint_stock` | PRC 股份有限公司 preparing to list | current articles, IPO-draft articles, sponsor/legal opinions, audit notes, historical equity changes, shareholder agreements/special-right cleanup | prospectus, audit reports, equity plan, recruitment, employee count | distinguish articles from shareholder agreements; mark historical charters unavailable if not public |
| `cn_private_llc` | PRC 有限责任公司 | business-registration changes, publicly available articles/amendments, financing agreements when disclosed, court/government records, later IPO/legal-opinion reconstruction | financing announcements, recruiting, salary ranges, official team statements, public profiles | historical articles are often not public; reconstruct governance rather than invent text |
| `hk_listed` | HKEX listed, possibly Cayman/BVI issuer | articles of association, prospectus, annual report, WVR disclosures, substantial shareholder filings, circulars | remuneration reports, share award/option/RSU schemes, annual/interim reports, job postings | economic ownership and voting power may differ materially |
| `us_listed` | SEC registrant, often Delaware/Cayman | certificate/articles, bylaws/M&A exhibits, S-1/F-1, 10-K/20-F, DEF 14A, 8-K/6-K, voting agreements | executive comp, SBC, headcount, segment data, equity plans, salary-range job postings | map ADS to underlying shares; inspect dual-class, conversion and sunset clauses |
| `foreign_private` | non-listed foreign company | local registry/company house, shareholder agreements if public, financing documents | official recruiting, compensation databases, financing data | widen uncertainty; law/source availability differs by country |
| `state_owned` | central/local SOE or controlled listed company | articles, SASAC/government ownership documents, exchange filings, board/party-governance disclosures | annual reports, salary-control disclosures, executive-remuneration rules, recruiting | administrative pay constraints and appointment mechanisms may dominate market pricing |

## Mandatory charter pass

For every company, search for the following in this order and record the result even if nothing is found:

1. current articles/charter/bylaws;
2. historical amended-and-restated versions or amendment notices;
3. IPO/pre-IPO articles or listing-effective articles;
4. shareholder agreements / investor-rights agreements / voting agreements;
5. WVR/dual-class/special-voting-right terms;
6. board appointment, committee, veto and reserved-matters rules;
7. equity-incentive pool and dilution terms;
8. evidence of special-right termination before IPO.

If an old charter is unavailable, set `charter_status = reconstructed` and state the exact documents used to reconstruct it. Never quote reconstructed language as charter text.

## Search-depth rule

Do not stop after finding the latest annual report. A company-type-specific analysis is complete only when the search has separately covered:

- charter/governance;
- economics/profit pools;
- workforce/payroll;
- compensation/equity;
- organization/critical roles;
- career transitions.
