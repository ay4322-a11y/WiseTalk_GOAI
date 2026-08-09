# Model Reference — STAR (Agent 1: STAR Interviewer)

> This agent's section of the shared [wisetalk-model-catalog](../../../../reference/wisetalk-model-catalog.md), kept as a human-readable copy. The agent body's `## Model reference — STAR` section is the baked-in source of truth at runtime — keep the two in sync. Read-only; do not edit at runtime.

## Model: STAR

**Structure:** S — Situation · T — Task · A — Action · R — Result

| Letter | Component | Meaning |
|--------|-----------|---------|
| S | Situation | The relevant background/context, kept brief |
| T | Task | Your responsibility or objective in that situation |
| A | Action | What *you personally* did — the bulk of the story |
| R | Result | The outcome, quantified where possible, plus what you learned |

**Best context:** job interviews, promotion interviews, performance reviews, project retrospectives, lessons-learned discussions, leadership competency assessments, evidence-based career profiles, resume writing.

**Application guideline (how to coach the user):**
1. Choose one relevant real example — never blend multiple stories.
2. Keep the Situation brief — one or two sentences of context only.
3. State the Task clearly — what the user personally owned.
4. Spend most of the effort on Actions — first-person, specific verbs.
5. Quantify the Result where possible; name the learning or what to repeat.

**Worked example (model shape):**
> **Situation:** A project dashboard was producing inconsistent figures across departments.
> **Task:** I was responsible for identifying the cause and standardising the reporting process.
> **Action:** I mapped the data sources, reconciled the definitions with department heads, created a controlled template, and introduced a validation checklist.
> **Result:** Reporting preparation time fell from two days to four hours, and data discrepancies were reduced significantly.

**Common mistakes:** situation too long (context dumping); actions in passive voice or team-credit instead of personal; missing or vague result; no quantification.

**Best reference:** UK National Careers Service, "The STAR Method"; MIT CAPD, "The STAR Method for Behavioral Interviews". Combine with the job description and prepared examples for leadership, conflict, problem-solving, stakeholder management, and failure recovery.

**Fill-in fields (Skill-3 mandatory cards):**
| Field | Guiding question the agent asks |
|-------|--------------------------------|
| `Situation` | What was the background context — where and when did this happen, and what was at stake? |
| `Task` | What specifically were *you* responsible for in this situation? |
| `Action` | What did you personally do, step by step? (Be specific — verbs, not adjectives.) |
| `Result` | What was the measurable outcome, and what did you learn or would repeat? |

**Generation prompt template (Skill-7):**
> You are a STAR Interview Expert. The user just filled in the data for a `[<use_case>]`. Synthesize these fragments into a polished, interview-ready STAR narrative — Situation brief, Task clearly owned, Actions specific and first-person (the bulk of the story), Result quantified with a learning. If a `[<user_revision_request>]` is present, strictly apply it to the rewrite.

**Critique dimensions (Skill-13):**
1. **Model integrity:** Does it follow S→T→A→R with the emphasis on Action? Is the Situation brief, is the Task owned, is the Result quantified?
2. **Tone & audience fit:** Is the language confident and concise enough for an interview/performance context?
3. **Logic & persuasion gaps:** Does the story answer "what did YOU do" convincingly? Any vague claims that need specifics or numbers?

**Use cases:** `Job_Interview` · `Performance_Review` · `Project_Debrief` · `Resume_Writing`

---

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-08-09 | STAR section from the shared catalog (v1.0) |
