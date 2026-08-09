# Model Reference — RIDE (Agent 6: RIDE Negotiator)

> This agent's section of the shared [wisetalk-model-catalog](../../../../reference/wisetalk-model-catalog.md), kept as a human-readable copy. The agent body's `## Model reference — RIDE` section is the baked-in source of truth at runtime — keep the two in sync. Read-only; do not edit at runtime.

## Model: RIDE

**Structure:** R — Risk · I — Interest · D — Difference · E — Effect

| Letter | Component | Meaning |
|--------|-----------|---------|
| R | Risk | What happens if the proposal is *not* adopted |
| I | Interest | The benefit the audience will gain |
| D | Difference | What makes your proposal distinctive vs alternatives |
| E | Effect | The wider impact, including realistic limitations |

**Best context:** stakeholder persuasion, budget requests, vendor negotiations, investment proposals, change adoption, selling an internal project, influencing a resistant decision-maker, salary negotiation, client deals, vendor management, resource allocation.

**Application guideline (how to coach the user):**
1. **Risk:** describe the consequence of maintaining the status quo.
2. **Interest:** connect the proposal to the stakeholder's priorities.
3. **Difference:** explain why this option is better than the alternatives.
4. **Effect:** acknowledge realistic limitations and describe the overall impact.
5. **Close with a decision request:** state exactly what you want approved.

**Worked example (model shape):**
> **Risk:** If we retain the manual process, monthly reporting errors will continue and management decisions may be delayed.
> **Interest:** Automation will save approximately 16 staff-hours per month.
> **Difference:** This solution integrates with our existing accounting system rather than requiring a full replacement.
> **Effect:** The first-month implementation will require staff training, but the long-term process will be faster and more reliable.

**Common mistakes:** exaggerating the risk or hiding material disadvantages — persuasion is only credible when risks and limitations are stated accurately; interest not tied to the stakeholder's actual priorities; missing the closing decision request.

**Best reference:** RIDE is a practical persuasion checklist without one canonical academic source. Support it with stakeholder analysis, cost-benefit analysis, risk assessment, BATNA and negotiation principles, and ethical persuasion practices.

**Fill-in fields (Skill-3 mandatory cards):**
| Field | Guiding question the agent asks |
|-------|--------------------------------|
| `Risk` | What happens if the proposal is not adopted — what's the cost of doing nothing? |
| `Interest` | What specific benefit does the other party gain by accepting? |
| `Difference` | What makes this option better than the alternatives they might choose? |
| `Effect` | What is the wider impact — including the realistic limitations? |

**Generation prompt template (Skill-7):**
> You are a RIDE Negotiation Expert. The user just filled in the data for a `[<use_case>]`. Synthesize these fragments into a fully persuasive, logically sound, professional-grade negotiation speech: the Risk of inaction stated accurately, the Interest tied to the stakeholder's priorities, the Difference vs alternatives, and an honest Effect with limitations — ending with an explicit decision request. If a `[<user_revision_request>]` is present, strictly apply it to the rewrite.

**Critique dimensions (Skill-13):**
1. **Model integrity:** Does it follow R→I→D→E? Is the Risk of inaction stated (not skipped)? Is the Risk honest — not exaggerated?
2. **Tone & audience fit:** Is the tone confident but not aggressive — right for negotiating with a superior or client?
3. **Logic & persuasion gaps:** Is Interest anchored to the other party's priorities? Is the closing decision request explicit?

**Use cases:** `Salary_Negotiation` · `Client_Deal` · `Vendor_Management` · `Resource_Allocation`

---

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-08-09 | RIDE section from the shared catalog (v1.0) |
