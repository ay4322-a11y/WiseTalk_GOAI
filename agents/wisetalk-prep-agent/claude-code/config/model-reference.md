# Model Reference — PREP (Agent 4: PREP Speaker)

> This agent's section of the shared [wisetalk-model-catalog](../../../../reference/wisetalk-model-catalog.md), kept as a human-readable copy. The agent body's `## Model reference — PREP` section is the baked-in source of truth at runtime — keep the two in sync. Read-only; do not edit at runtime.

## Model: PREP

**Structure:** P — Point · R — Reason · E — Example · P — Point

| Letter | Component | Meaning |
|--------|-----------|---------|
| P | Point | Your main view, stated once, clearly |
| R | Reason | Why — one to three reasons |
| E | Example | Evidence, data, or an illustration supporting the reason |
| P | Point | Restate the conclusion / required action |

**Best context:** meetings, short presentations, impromptu questions, stakeholder discussions, team recommendations, interview answers requiring a direct opinion, professional disagreements, elevator pitches, quick meeting speeches, daily standups, public comments.

**Application guideline (how to coach the user):**
1. State one clear point.
2. Give one to three reasons.
3. Support the reasons with data, examples, or experience.
4. End by repeating the point and, where appropriate, specifying the action.

**Worked example (model shape):**
> **Point:** We should automate the monthly sales report.
> **Reason:** The current process takes two working days and creates avoidable manual errors.
> **Example:** Last month, three regional figures were reported incorrectly because of spreadsheet-copying mistakes.
> **Point:** Therefore, automating the report should reduce preparation time and improve accuracy.

**Common mistakes:** several unrelated points in one PREP response (use one PREP per conclusion, or switch to the Pyramid Principle); reasons without evidence; missing the final restated point.

**Best reference:** PREP is a practical speaking framework rather than a formal academic theory. Use as a concise presentation technique combined with evidence-based reasoning and audience analysis.

**Fill-in fields (Skill-3 mandatory cards):**
| Field | Guiding question the agent asks |
|-------|--------------------------------|
| `Point` | What is your main view or recommendation, in one sentence? |
| `Reason` | Why should the audience believe it — what's the rationale? |
| `Example` | What evidence, data, or illustration backs the reason? |
| `Action` | What do you want to happen next (restated point + required action)? |

**Generation prompt template (Skill-7):**
> You are a PREP Speaking Expert. The user just filled in the data for a `[<use_case>]`. Synthesize these fragments into a tight, spoken-ready answer: Point first, one to three Reasons, an Example grounding each reason, then the Point restated with a clear action. Keep it short enough to speak aloud. If a `[<user_revision_request>]` is present, strictly apply it to the rewrite.

**Critique dimensions (Skill-13):**
1. **Model integrity:** Does it follow P→R→E→P? Is there exactly one central point — not several unrelated conclusions?
2. **Tone & audience fit:** Is the answer concise and confident enough for spoken delivery?
3. **Logic & persuasion gaps:** Does every reason carry a concrete example? Is the closing action explicit?

**Use cases:** `Elevator_Pitch` · `Quick_Meeting_Speech` · `Daily_Standup` · `Public_Comment`

---

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-08-09 | PREP section from the shared catalog (v1.0) |
