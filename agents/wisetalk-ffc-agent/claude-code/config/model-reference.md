# Model Reference — FFC (Agent 7: FFC Master)

> This agent's section of the shared [wisetalk-model-catalog](../../../../reference/wisetalk-model-catalog.md), kept as a human-readable copy. The agent body's `## Model reference — FFC` section is the baked-in source of truth at runtime — keep the two in sync. Read-only; do not edit at runtime.

## Model: FFC

**Structure:** F — Feeling · F — Fact · C — Compare

| Letter | Component | Meaning |
|--------|-----------|---------|
| F | Feeling | Your personal reaction — what it felt like to observe |
| F | Fact | The specific behaviour or result, described concretely |
| C | Compare | How it stands out vs a normal/previous standard |

Main principle: praise a **concrete behaviour**, never a vague compliment.

**Best context:** employee feedback, coaching, recognition messages, team leadership, peer appreciation, performance reviews, client or vendor appreciation, relationship building, team recognition, ice-breaking.

**Application guideline (how to coach the user):**
1. State the positive feeling or reaction.
2. Identify the specific fact that caused it — the observed behaviour.
3. Explain the improvement, difference, or positive standard.
4. If appropriate, connect it to business impact.
5. Avoid exaggerated or personality-based statements.

**Worked example (model shape):**
> "I was impressed by how confidently you handled the client meeting. You summarised each issue, confirmed the client's priorities, and ended with clear next steps. Compared with our previous meetings, the discussion was more focused and resulted in faster agreement."

**Common mistakes:** praise such as "You are brilliant" with no evidence — specific praise is more credible, memorable, and reinforces repeatable behaviour; personality-based rather than behaviour-based statements.

**Best reference:** FFC is a practical feedback mnemonic. Combine with SBI (Situation, Behaviour, Impact), feedforward coaching, behaviourally specific performance feedback, and the "continue, start, stop" method.

**Fill-in fields (Skill-3 mandatory cards):**
| Field | Guiding question the agent asks |
|-------|--------------------------------|
| `Feeling` | What was your honest reaction when you observed this? |
| `Fact` | What specific behaviour or result caused it? (Observable, concrete.) |
| `Compare` | How does this stand out vs a normal or previous standard? |

**Generation prompt template (Skill-7):**
> You are a FFC Feedback Expert. The user just filled in the data for a `[<use_case>]`. Synthesize these fragments into warm, specific, behaviour-based recognition: your Feeling, the concrete Fact that caused it, and the Compare showing how it stands out — with business impact where appropriate. Never praise personality, only observable behaviour. If a `[<user_revision_request>]` is present, strictly apply it to the rewrite.

**Critique dimensions (Skill-13):**
1. **Model integrity:** Does it follow F→F→C? Is the Fact specific and observable (not a personality compliment)?
2. **Tone & audience fit:** Is the warmth genuine without exaggeration — right for the relationship?
3. **Logic & persuasion gaps:** Does the Compare anchor against a real prior standard? Is the behaviour one worth repeating?

**Use cases:** `Team_Recognition` · `Relationship_Building` · `Peer_Feedback` · `Ice_Breaking`

---

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-08-09 | FFC section from the shared catalog (v1.0) |
