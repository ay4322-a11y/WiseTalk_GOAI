---
name: swot-analysis
description: Produce an evidence-grounded SWOT analysis of a company, product, or initiative. Use when the task asks for strengths/weaknesses/opportunities/threats, a strategic position assessment, or a SWOT section inside a larger report. Do NOT use for market sizing or expansion decisions (use market-expansion-analysis) or for financial valuation.
tags: analysis, strategy, business
---

# SWOT Analysis

Input: the subject (company / product / initiative) and scope (market, region, time horizon), plus any evidence already gathered by the caller.
Output: a 4-quadrant SWOT with every entry traceable to cited evidence, ending with 2–3 cross-quadrant strategic implications.

## Procedure

1. **Frame** — restate the subject and scope in one line; list the 3–5 evaluation dimensions that matter for this subject (e.g. product, distribution, cost position, brand, regulation).
2. **Gather** — collect evidence per dimension from {{data sources — e.g. WebSearch, internal docs, provided files}}. Keep the source (URL / file / doc section) attached to every fact. Minimum {{N, e.g. 3}} independent sources for external claims.
3. **Classify** — sort each evidenced fact into the quadrant it supports: internal-favorable → Strength, internal-unfavorable → Weakness, external-favorable → Opportunity, external-unfavorable → Threat. Discard facts with no evidence; never fill a quadrant with plausible-sounding filler.
4. **Cross-analyze** — derive 2–3 strategic implications by pairing quadrants (S×O: leverage plays; W×T: exposures to mitigate; S×T: defenses; W×O: gaps to close).
5. **Deliver** — output the 4-quadrant table (each entry: one-line claim + source), then the implications, to {{output destination — e.g. report section, standalone file}}.

## Failure handling

If a quadrant has fewer than 2 evidenced entries after step 3, deliver the SWOT anyway with that quadrant explicitly marked "insufficient evidence — needs {{what's missing}}" rather than padding it. If the subject or scope is ambiguous, ask one consolidated clarifying question before step 2.

## Customization points

- `description` trigger — rewrite for the owning agent's routing ("Use when…; do NOT use for…").
- Step 2 `{{data sources}}` and evidence threshold `{{N}}` — match the agent's Element 11 tools and quality bar.
- Step 5 `{{output destination}}` — match the agent's Element 15 output format.
- Evaluation dimensions in step 1 — pin them if the agent always analyzes the same kind of subject.
