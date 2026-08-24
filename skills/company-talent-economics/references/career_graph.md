# Career graph

Build a graph from public histories and official organization changes.

## Node
`company_native_role + normalized_state + function + BU + geography`

## Edge types
- internal_promotion
- internal_lateral
- manager_switch
- external_entry
- exit

Record dates/months when visible, previous company, and evidence tier. Aggregate only after deduplication.

## Reporting discipline
Public profiles are a selected sample. Unless a company-wide denominator is known, report `observed public-profile transition share`, not true promotion probability.

Useful outputs:
- most common internal path into high-TC states;
- most common external-entry path;
- observed median months between states;
- first state where crossing the target TC becomes common;
- build-vs-buy pattern for senior talent.
