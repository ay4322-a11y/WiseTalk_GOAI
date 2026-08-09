# Model Reference — Communication Funnel (Agent 8: Funnel Refiner)

> This agent's section of the shared [wisetalk-model-catalog](../../../../reference/wisetalk-model-catalog.md), kept as a human-readable copy. The agent body's `## Model reference — Communication Funnel` section is the baked-in source of truth at runtime — keep the two in sync. Read-only; do not edit at runtime.

## Model: Communication Funnel

**Structure:** What I intend to say → What I actually say → What the listener hears → What the listener understands → What the listener remembers → What the listener acts upon

The funnel is a **diagnostic + compression model**: information is progressively lost/distorted through each stage. The agent's job is to reverse the loss — extract the absolute core (action items, data, conclusions) from a long text and compress it, so what the listener retains matches what the speaker intended.

**Best context:** task delegation, complex instructions, information compression, executive summaries, giving instructions to employees/teams, communicating requirements to vendors/developers, explaining complex issues to senior management, handovers between departments, safety/compliance/operational procedures.

**Application guideline (how to coach the user):**
1. Define the intended outcome — what should the listener know, decide, or do?
2. Reduce the message — remove unnecessary history, jargon, and unrelated details.
3. State the core message first (e.g. "The project will be delayed by two weeks because UAT is not complete.").
4. Use a structured format: context, issue, implication, required action, deadline.
5. Ask for confirmation: "Can you summarise the action you will take?"
6. Document the agreement — meeting summary with owners and due dates.
7. Follow up — check whether the intended action occurred.

**Worked example (model shape):**
> "The system launch will move from 1 September to 15 September because the payment gateway test is incomplete. The technology team must complete testing by 5 September. Please confirm by 3 p.m. today whether this date is achievable."

**Common mistakes:** compressing into a summary that keeps background but drops the action item and deadline; extracting opinions instead of facts; keeping jargon the listener won't understand.

**Best reference:** no single canonical textbook — treat the funnel as a diagnostic model for where communication becomes distorted. Combine with active listening, closed-loop communication, and meeting-minute practices.

**Skill assignment difference — CRITICAL:**
- This agent does **NOT** run the coaching loop. No Skill-7 (`language-polishing`), no Skill-13 (`iterative-critique`).
- It uses **Skill-3** (`mandatory-fill-in`, single text box) + **Skill-5** (`funnel-compression`).
- The pipeline is: user pastes long text → validate it exists → compress to <20% of original length → deliver the core summary. One-way compression, no generation, no critique.

**Fill-in field (Skill-3 mandatory card — single field):**
| Field | Guiding question the agent asks |
|-------|--------------------------------|
| `OriginalText` | Paste the long text you need compressed (more than 50 words). |

**Compression prompt template (Skill-5):**
> You are a denoising expert. The user sent a long text. According to the Communication Funnel, 80% of information is lost in transmission. Extract the absolute core 20% — Action items, Data, and Conclusions. Compress it to less than 20% of the original length, preserving the action items and deadlines verbatim.

**Critique dimensions:** none — no critique loop. The compression output is self-evidently correct when it passes Skill-5's acceptance checks (≤ 20% length, action items preserved, no invented content).

**Use cases:** `Task_Delegation` · `Complex_Instruction` · `Information_Compression` · `Executive_Summary`

---

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-08-09 | Funnel section from the shared catalog (v1.0) |
