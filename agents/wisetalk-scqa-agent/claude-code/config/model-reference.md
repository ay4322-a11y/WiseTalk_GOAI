# Model Reference — SCQA (Agent 5: SCQA Analyst)

> This agent's section of the shared [wisetalk-model-catalog](../../../../reference/wisetalk-model-catalog.md), kept as a human-readable copy. The agent body's `## Model reference — SCQA` section is the baked-in source of truth at runtime — keep the two in sync. Read-only; do not edit at runtime.

## Model: SCQA

**Structure:** S — Situation · C — Complication · Q — Question · A — Answer

| Letter | Component | Meaning |
|--------|-----------|---------|
| S | Situation | The familiar background the audience already recognises |
| C | Complication | The problem, change, or conflict that disrupts the situation |
| Q | Question | The decision question that naturally follows |
| A | Answer | The recommendation or solution |

**Best context:** business proposals, problem-solving presentations, change-management communication, project escalation, strategy recommendations, consulting-style reports, explaining why an action is necessary, crisis management, conflict resolution, urgent incidents.

**Application guideline (how to coach the user):**
1. Begin with facts the audience already recognises.
2. Explain what has changed or gone wrong.
3. Convert the issue into a clear decision question.
4. Answer the question with a recommendation.
5. Add supporting evidence, risks, costs, and next steps.

**Worked example (model shape):**
> **Situation:** Our company currently processes customer complaints through email.
> **Complication:** Complaint volume has increased by 40%, causing response delays and inconsistent tracking.
> **Question:** How can we improve response speed and visibility?
> **Answer:** We should implement a centralised customer-service ticketing system.

**Common mistakes:** starting with the answer (that's PREP); a Complication the audience doesn't perceive as a problem; a vague Question that isn't a decision; answer without risks or next steps.

**Best reference:** SCQA is associated with structured business communication and consulting-style storytelling (Minto-school problem framing). Most useful when the audience needs to understand *why* a recommendation is necessary. Difference from PREP: PREP starts with the conclusion for short answers; SCQA builds a problem narrative first.

**Fill-in fields (Skill-3 mandatory cards):**
| Field | Guiding question the agent asks |
|-------|--------------------------------|
| `Situation` | What is the stable, familiar background your audience already agrees on? |
| `Complication` | What changed or went wrong that makes the situation untenable? |
| `Question` | What is the decision question that this complication raises? |
| `Answer` | What is your recommendation, with evidence, risks, and next steps? |

**Generation prompt template (Skill-7):**
> You are a SCQA Problem-Solving Expert. The user just filled in the data for a `[<use_case>]`. Synthesize these fragments into a problem-framed narrative: Situation facts first, the Complication that breaks it, the sharp decision Question, then your Answer with supporting evidence, risks, costs, and next steps. If a `[<user_revision_request>]` is present, strictly apply it to the rewrite.

**Critique dimensions (Skill-13):**
1. **Model integrity:** Does it follow S→C→Q→A in order? Does the Complication genuinely undermine the Situation (not a non-event)?
2. **Tone & audience fit:** Is the framing calm and factual — suited to crisis or escalation contexts?
3. **Logic & persuasion gaps:** Is the Question a real decision? Does the Answer address the Question directly, with risks and next steps?

**Use cases:** `Crisis_Management` · `Problem_Solving` · `Conflict_Resolution` · `Urgent_Incident`

---

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-08-09 | SCQA section from the shared catalog (v1.0) |
