# Role-holder cases and CV comparison

Use this module when the user wants to see who holds a target R&D role, how those
people entered it, and how their own experience compares. Start with a company,
role family, geography and reference date. A candidate CV is optional.

## Research

Run `scripts/role_profiles.py init` to create `profiles.json` and `search_plan.json`
in the user's workspace. Search company team pages and appointment announcements
for names. Follow personal homepages and public CVs for education and employment;
use conference biographies, technical blogs, papers and open-source records to
fill gaps. Search role aliases in the local language and English. Check recent
appointments, moves and departures before treating anyone as a current case.

Read primary pages. Each populated role claim and experience needs direct source
IDs. Record the queries actually run in `searches`, including useful searches that
found no evidence. Follow links to earlier employers and institutional profiles
when they clarify entry history. Stop when additional queries repeat known cases
or cannot fill decision-relevant gaps; report the collected cases even if the
sample is empty.

Confirm identity before combining records. Keep ambiguous names, former employees
and mismatched roles in the separate case list. Explain role equivalence through
responsibilities in `match_reason`; retain the person's native title. Use the
same employer and geography as the target for included cases. A broad research
title alone does not establish a match to a specific engineering job.

Use public pages that the host can read without bypassing access controls. BOSS
sources are excluded. A publicly readable professional profile may supplement
first-party pages. Log access failures and keep the fields they would support
unknown. Publication affiliations are discovery evidence; confirm current
employment through a personal or company statement.

The identity and field-source workflow draws on
[find-researcher-cv](https://github.com/WuLin0919/find-researcher-cv). This module
adds role discovery, dated entry histories and CV comparisons. It runs with the
same host web tools and Python dependencies as company-talent-economics.

## Evidence contract

Use `schemas/role_profiles.schema.json`; the fictional records in
`examples/role_profiles/` show the complete input. `role_profiles.py check` also
checks references, dates, source types and target scope.

- `meta`: company, target role, geography, report language and reference date.
- `sources`: ID, title, direct URL, source type, content dates and access date.
  Include the original statement and set `origin_id` to its source ID for every
  mirror or repost. An original source uses its own ID.
- `capabilities`: stable IDs and labels for the comparison dimensions. Preserve
  the source's wording in experience summaries.
- `requirements`: advertised required/preferred capabilities with job-posting
  evidence. Case characteristics remain distinct from advertised requirements.
- `profiles`: resolved identity, native role, match explanation, joining date and
  sourced experience records. A `person_key` identifies one resolved person
  across multiple source records; merge duplicates before building.
- `searches`: query, search date, outcome (`found`, `not_found`, `excluded`) and note.

Source types are `company_page`, `appointment`, `personal_homepage`, `public_cv`,
`orcid`, `publication`, `conference_bio`, `technical_blog`, `open_source`,
`public_professional_profile` and `job_posting`.

Keep year/month date precision. The compiler labels an experience `pre_entry`
only when its latest possible end precedes the earliest possible joining date.
It labels `post_entry` when its earliest start is on or after the latest possible
joining date. Overlaps and missing dates stay `unknown`. Entry comparisons use
the dated pre-entry records; the case pages retain all experiences.

## Source freshness

Current-case ordering combines source quality, role relevance and content age:

`ordering_weight = source_weight × role_match_weight × 2^(-age_days / half_life_days)`

Role sources receive weights of 1.0 for company pages and appointments; 0.9 for
personal homepages and public CVs; 0.7 for conference biographies and technical
blogs; and 0.6 for public professional profiles. ORCID, papers, open-source
records and job postings supplement the evidence; they do not rank a person's
current role. Exact role matches receive 1.0; related roles 0.75.
The default half-life is 730 days. Undated evidence receives a freshness weight
of 0.5. Override these ordering assumptions in `policy` when the research scope
calls for a different time scale. Scores express ordering, not probabilities.

Use `role.as_of` for an explicitly dated role statement, otherwise the source's
verified `updated_date` or `published_date`. Record an update only when it applies
to the supporting content. HTTP timestamps, copyright years and access dates
do not date a role claim. Rank mirrors using the original statement's source type
and date. Multiple original sources contribute the strongest weight. Historical
education and completed experiences keep their evidence regardless of age.

## Candidate comparison

Read the user-supplied CV and map its stated experiences to the capability IDs.
Save a separate candidate file:

```json
{
  "experiences": [{
    "summary": "Built a distributed training prototype",
    "capability_ids": ["systems"],
    "resume_reference": "CV, Projects, item 1"
  }],
  "next_steps": [{
    "capability_id": "systems",
    "action": "Add the training scale, your contribution and evaluation results.",
    "evidence_ids": ["J1"]
  }]
}
```

Candidate experience is self-reported. Every match cites a CV location. Missing
CV evidence is `not_documented`; ask for an example before calling it an ability
gap. Write concrete next steps from the advertised requirements and dated cases,
with source IDs. Distinguish adding an existing experience to the CV from
developing a new skill. Keep candidate files and generated reports in the user's
workspace; commit the fictional fixtures, not personal data.

Keep public salary ranges in the company report's existing pay sections. Case
profiles do not receive inferred individual salaries. Report sample counts and
different entry paths; the public cases do not establish workforce frequencies,
salary premiums or hiring probabilities.

## Build and render

Paths below are relative to the skill directory; `$S` is its absolute path.

```bash
python "$S/scripts/role_profiles.py" init --company "Company" \
  --role "Research Scientist" --geography "US" --language en \
  --date 2026-10-12 --out ./role-research
# Research and fill ./role-research/profiles.json.
python "$S/scripts/role_profiles.py" check ./role-research/profiles.json
python "$S/scripts/role_profiles.py" build ./role-research/profiles.json \
  --candidate ./candidate.json --out ./role-research/result
python "$S/scripts/render_report.py" ./role-research/result/report.json \
  --profiles-only -o ./role-research/result/report.pdf
```

Omit `--candidate` for cases without a personal comparison. The build writes
`report.json`, `evidence.jsonl` and `source_manifest.csv`. Add
`--report ./talent-economics/company/report.json` to attach the section to an
existing report with the same company, language and reference date. Compile the
company report first, attach the cases, then validate and render as usual. The
ten phase gates stay unchanged. Inspect the PDF before delivery; use the existing
`--docx-only` option when LibreOffice is unavailable.

Run the fictional example by replacing the input paths with
`$S/examples/role_profiles/profiles.json` and
`$S/examples/role_profiles/candidate.json`. Verify changes with:

```bash
python -m unittest discover -s "$S/tests" -v
python "$S/scripts/check_locales.py"
python "$S/scripts/selftest.py"
```
