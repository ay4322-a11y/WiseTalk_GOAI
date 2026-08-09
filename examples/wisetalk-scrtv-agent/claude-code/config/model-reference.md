# Model Reference — SCRTV (Agent 2: SCRTV Reporter)

> This agent's section of the shared [wisetalk-model-catalog](../../../../reference/wisetalk-model-catalog.md), kept as a human-readable copy. The agent body's `## Model reference — SCRTV` section is the baked-in source of truth at runtime — keep the two in sync. Read-only; do not edit at runtime.

## Model: SCRTV

**Structure:** S — Scene · C — Conflict · R — Reason · T — Tactics · V — Value

| Letter | Component | Meaning |
|--------|-----------|---------|
| S | Scene | The current context/operating environment |
| C | Conflict | The problem, tension, or performance gap |
| R | Reason | The underlying cause(s) of the conflict |
| T | Tactics | The proposed actions — owners, timing, resources |
| V | Value | The expected benefits, quantified with KPIs or financials |

**Best context:** project proposals, transformation programmes, marketing campaigns, operational improvement plans, technology implementation, internal business presentations, strategy proposals, budget requests, project status reports, issue escalation, explaining the logic behind a strategy.

**Application guideline (how to coach the user):**
1. Describe the current operating environment factually.
2. Identify the performance gap or business problem precisely.
3. Analyse the underlying causes — don't jump to solutions.
4. Present specific tactics with owners, timing, and resources.
5. Quantify the expected value using KPIs, financial benefits, or risk reduction.

**Worked example (model shape):**
> **Scene:** The company has expanded into three new Malaysian states.
> **Conflict:** Regional teams are using different sales processes, making performance comparisons difficult.
> **Reason:** There is no common CRM workflow or reporting definition.
> **Tactics:** Introduce a standard CRM process, train sales managers, and create a weekly dashboard.
> **Value:** Management will obtain consistent pipeline visibility and reduce reporting preparation time.

**Common mistakes:** skipping the Scene (audience lacks shared context); blaming without Reason analysis; tactics without owners or deadlines; value stated as adjectives ("better", "improved") instead of numbers.

**Best reference:** SCRTV is a practical mnemonic without one canonical academic source. Combine with SCQA for problem framing, the Pyramid Principle for logical organisation, a cost-benefit analysis for value quantification, and a RACI matrix for accountability.

**Fill-in fields (Skill-3 mandatory cards — 5 cards):**
| Field | Guiding question the agent asks |
|-------|--------------------------------|
| `Scene` | What is the current situation the audience already knows — or needs to know? |
| `Conflict` | What problem, tension, or gap exists right now? |
| `Reason` | What is the underlying cause of that problem? |
| `Tactics` | What specific actions will you take — with owners, timing, and resources? |
| `Value` | What is the expected benefit, quantified with KPIs or financial figures? |

**Generation prompt template (Skill-7):**
> You are a SCRTV Reporting Expert. The user just filled in the data for a `[<use_case>]`. Synthesize these fragments into a professional, logically-sequenced report or proposal following Scene → Conflict → Reason → Tactics → Value, with each tactic carrying an owner and each value claim carrying a number. If a `[<user_revision_request>]` is present, strictly apply it to the rewrite.

**Critique dimensions (Skill-13):**
1. **Model integrity:** Does it follow S→C→R→T→V in order? Is there a genuine causal link from Reason to Tactics?
2. **Tone & audience fit:** Is the register right for a board/management report — objective, no hedging, no emotional language?
3. **Logic & persuasion gaps:** Are tactics specific (owners/timing)? Is Value quantified? Any unsupported claims needing evidence?

**Use cases:** `Project_Status_Report` · `Strategy_Proposal` · `Budget_Request` · `Issue_Escalation`

---

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-08-09 | SCRTV section from the shared catalog (v1.0) |
