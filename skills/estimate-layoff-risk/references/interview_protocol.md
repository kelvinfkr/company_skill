# Adaptive interview protocol

Obtain information public sources cannot observe while minimizing unnecessary personal disclosure. Ask in short rounds. Explain that `unknown` and `prefer_not_to_answer` are valid responses.

## Round 1 - Locate the exposure

Ask these six questions first:

1. What outcome should count: statutory layoff, unit closure, role redundancy, performance exit, contract non-renewal, internship ending, forced transfer, or any involuntary exit?
2. What horizons matter: 3, 6, and/or 12 months?
3. What legal entity employs or contracts with you, and what parent/brand do you work under?
4. What country, worksite, BU, product/project/customer, and role family are you attached to?
5. What is the employment type and contract/probation/internship end date?
6. Is the business stable/profitable, growing but loss-making, incubating, integrating, or contracting? Say `unknown` if uncertain.

Stop and resolve entity ambiguity before searching. Do not mix a parent company's economics with a subsidiary's role exposure.

## Round 2 - Objective local signals

7. What changed in team headcount, open requisitions, replacement hiring, contractors, budget, travel, procurement, or overtime during the last 90 days?
8. Is your workload increasing, stable, disappearing, transferred, automated, or duplicated?
9. Did your manager, skip-level leader, reporting line, cost center, worksite, or product ownership change?
10. Do you have funded deliverables with owners and deadlines for the next 8-12 weeks?
11. Has anyone requested headcount justification, workload logs, handover documents, access review, location changes, or role reapplications?
12. If 20% of the team disappeared, which work must remain and who else could perform yours?

## Answer record

```json
{
  "question_id": "core_07",
  "answer": "Two open roles were closed; one departure was not replaced",
  "observed_date": "YYYY-MM-DD",
  "provenance": "direct_observation",
  "candidate_confidence": 0.8,
  "include_in_report": true
}
```

Allowed provenance values: `formal_notice`, `direct_observation`, `manager_statement`, `coworker_report`, `candidate_interpretation`, and `unknown`.

Do not silently upgrade a coworker rumor into an observed fact.

## Adaptive follow-ups

Select branches by employment type, role family, company type, action regime, and unresolved high-sensitivity assumptions. Ask a follow-up only if the answer could materially move the six-month estimate, change the dominant exit mechanism, or narrow the interval.

Strong upward signals include formal consultation or role reapplication, removal of a funded roadmap, work handoff, leadership departure during restructuring, same-role requisition removal, explicit headcount targets, and responsibility/access removal before transition.

Moderate upward signals include sustained workload decline, repeated budget/vendor freezes, M&A duplicate teams, role-justification requests, and cancelled milestones.

Protective signals include customer/regulatory/safety obligations, funded future deliverables, active same-role hiring, scarce system ownership, long recovery time, retention awards, and credible redeployment.

Weak signals include fewer social meetings, a single terse manager message, undated office rumors, or stock-price movement without an operating mechanism.

## Interview tone

Use neutral language. Do not lead the candidate toward a high-risk answer. Summarize answers and let the candidate correct factual misunderstandings before modeling.
