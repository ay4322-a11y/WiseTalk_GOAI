# Model Reference — MECE / Pyramid Principle (Agent 3: MECE Architect)

> This agent's section of the shared [wisetalk-model-catalog](../../../../reference/wisetalk-model-catalog.md), kept as a human-readable copy. The agent body's `## Model reference — MECE` section is the baked-in source of truth at runtime — keep the two in sync. Read-only; do not edit at runtime.

## Model: MECE / Pyramid Principle

**Structure:** Main conclusion → 3–4 key supporting arguments → evidence under each

| Layer | Meaning |
|-------|---------|
| Conclusion first | The recommendation stated in one sentence at the top |
| Key arguments | 3–4 points that support the conclusion |
| Evidence | Data, examples, and analysis under each argument |

Core rules: **conclusion first**; **above supports below** (each lower point supports the point above); **MECE** — points at the same level are Mutually Exclusive (no overlap) and Collectively Exhaustive (no gaps).

**Best context:** logical analysis, report outlining, meeting minutes, brainstorming structure, board papers, management reports, consulting presentations, investment recommendations, business cases, feasibility studies, strategy papers, executive emails.

**Application guideline (how to coach the user):**
1. Write the answer first — the recommendation in one sentence.
2. Identify three to four supporting arguments.
3. Group similar points together.
4. Arrange points logically (e.g. financial, operational, strategic).
5. Add evidence under each point.
6. Check for overlap and gaps (MECE check via Skill-4 where available).
7. Put detailed analysis in an appendix if the audience is senior.

**Worked example (model shape):**
> **Recommendation: Approve the CRM implementation in Q4.**
> - It is financially viable, with an expected payback period of 18 months.
> - It addresses the current sales-data problem.
> - It can be implemented without disrupting the existing billing system.
> Supporting evidence: cost-benefit analysis, user pain points, implementation plan, risk assessment.

**Common mistakes:** burying the conclusion; overlapping arguments (e.g. "reduce labor cost" and "cut overtime pay" — one contains the other); incomplete coverage (missing a dimension like supply chain); unsupported claims without evidence.

**Best reference:** Barbara Minto, *The Pyramid Principle: Logic in Writing and Thinking*. Combine with MECE structuring, issue trees, and executive-summary writing.

**Fill-in fields (Skill-3 mandatory cards):**
| Field | Guiding question the agent asks |
|-------|--------------------------------|
| `Conclusion` | What is your main recommendation or answer — in one sentence? |
| `Arguments` | What are the 3–4 key points that support it? (List each separately.) |
| `Evidence` | What data, examples, or analysis backs each argument? |

**Generation prompt template (Skill-7):**
> You are a MECE / Pyramid Principle Expert. The user just filled in the data for a `[<use_case>]`. Synthesize these fragments into a pyramid-structured document: the conclusion stated first, then its supporting arguments grouped logically (MECE — no overlap, no gaps), each with its evidence beneath. If a `[<user_revision_request>]` is present, strictly apply it to the rewrite.

**Critique dimensions (Skill-13):**
1. **Model integrity:** Is the conclusion stated first in one sentence? Are arguments MECE — no overlap, no missing dimensions (check against a fixed domain library: Human, Machine, Material, Method, Environment)?
2. **Tone & audience fit:** Is the register appropriate for a report/briefing audience?
3. **Logic & persuasion gaps:** Does every argument carry evidence? Does any claim at the same level belong under another (overlap)?

**Use cases:** `Logical_Analysis` · `Report_Outlining` · `Meeting_Minutes` · `Brainstorming_Structure`

---

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-08-09 | MECE section from the shared catalog (v1.0) |
