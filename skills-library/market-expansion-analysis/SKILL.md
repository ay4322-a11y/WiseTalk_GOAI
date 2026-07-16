---
name: market-expansion-analysis
description: Assess a target market for expansion — market sizing, competitor landscape, entry barriers, and a go/no-go recommendation. Use when the task asks whether/how to enter a new market, region, or segment. Do NOT use for a general strategic position assessment of an existing business (use swot-analysis) or for post-entry performance review.
tags: analysis, market, strategy
---

# Market Expansion Analysis

Input: the expanding business (what it sells, current markets) and the target market (region / segment / vertical); optionally constraints (budget, timeline, risk appetite).
Output: a structured expansion assessment — market size, competitor map, entry barriers, risks — closing with a go / no-go / go-with-conditions recommendation, every figure sourced.

## Procedure

1. **Define** — state the target market precisely (geography × segment × offering) and the decision the analysis must support.
2. **Size** — estimate TAM/SAM/SOM from {{data sources — e.g. WebSearch, industry reports, internal sales data}}; record the method (top-down vs. bottom-up) and source for each figure. Flag estimates older than {{max data age, e.g. 2 years}}.
3. **Map competitors** — identify the top {{N, e.g. 5}} incumbents: offering, share (if known), pricing, positioning gap the entrant could occupy.
4. **Assess entry barriers** — regulation/licensing, distribution access, capital requirements, switching costs, localization needs. Rate each low/medium/high with the evidence behind the rating.
5. **Recommend** — weigh sized opportunity against barriers and constraints; deliver go / no-go / go-with-conditions with the 2–3 decisive factors, plus what evidence would change the call. Output to {{output destination — e.g. report section, standalone file}}.

## Failure handling

If market-size data for the exact target is unavailable, size the nearest proxy market and state the extrapolation assumption explicitly — never present a proxy figure as the target's. If the recommendation hinges on a fact that could not be verified, downgrade to "go-with-conditions" and name the fact as the condition.

## Customization points

- `description` trigger — rewrite for the owning agent's routing ("Use when…; do NOT use for…").
- Step 2 `{{data sources}}` and `{{max data age}}` — match the agent's Element 11 tools and freshness bar.
- Step 3 competitor count `{{N}}` — match the depth the agent's reports need.
- Step 5 `{{output destination}}` — match the agent's Element 15 output format.
- If the agent serves one industry, pin the barrier categories in step 4 to that industry's real ones.
