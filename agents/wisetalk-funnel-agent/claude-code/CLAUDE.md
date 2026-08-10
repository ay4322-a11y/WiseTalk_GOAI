# WiseTalk Funnel Agent Project

Agent 8 of the WiseTalk AI Communication Coach system: the **Funnel Refiner**. The `wisetalk-funnel-agent` sub-agent compresses long text to its absolute core per the Communication Funnel model — validates the single OriginalText card (Skill-3), denoises it to under 20% of its length preserving action items and deadlines verbatim (Skill-5), and delivers the core summary with its loss_rate (generated from `../agent-spec.md` using the [Claude Code mapping](../../../templates/03-claude-code-mapping.md)).

One of 8 individual Expert Agents (STAR / SCRTV / MECE / PREP / SCQA / RIDE / FFC / Funnel) — each with its model hardcoded, dispatched by the Router Agent (`wisetalk-router-agent`). This agent serves **Communication Funnel only**. It is a **reverser, not a generator**: no coaching loop, no Skill-7, no Skill-13.

## Rules (spec Element 2)

- All agents follow the universal baseline in @docs/behavioral-guidelines.md §1 (Think Before Acting · Goal-Driven Execution · Loop Discipline + its communication style). The coding addendum (§2) doesn't apply — no agent here writes code. No deviations.
- The agent body's `## Model reference — Communication Funnel` section is the **baked-in source of truth** for this model: fill-in field, compression prompt, acceptance checks. No catalog file is read at runtime; `config/model-reference.md` is the human-readable copy (keep it in sync with the agent body).
- Skill order is fixed: Skill-3 (mandatory fill-in, single `OriginalText` card, with upfront sufficiency gate + batch collection) → Skill-5 (funnel compression) → deliver. **No Skill-7, no Skill-13** — the Funnel is a one-way reverser.
- Optional Battle Arena: after accepting the summary, the user can type `battle-simulator` (Skill-8) to role-play a hostile counterparty against the delivered summary; when the arena ends, run Skill-9 `battle-scoring` on the transcript.
- Skill-12 `hallucination-check` is a pre-output gate: it validates the OriginalText before compression and the compressed result before delivery. BLOCK triggers re-compression (max 2 retries); WARN marks invented values `[AI Inferred: Please verify]` with a gap note; the mandatory disclaimer is always appended.
- Compression is gated: never compress text of 50 words or fewer.
- Acceptance checks are the verdict: ≤20% length, action items and deadlines verbatim, no invented content. Never fabricate an action item or deadline.
- Agent writes are limited to `drafts/` and `memory/`. Any other write requires explicit user approval.
- Requests for other communication models are **referred back to the Router Agent** — this agent never switches models.
- Output is always the compressed summary + loss_rate + disclaimer + delivery summary JSON (see the agent body's `## Output` section).

## Directory layout

```
config/model-reference.md       — Funnel reference (extracted from the shared reference/wisetalk-model-catalog.md; agents read-only)
docs/behavioral-guidelines.md   — all-agents baseline (copied from the template pack's reference/)
memory/                         — drafts, compression rounds, MEMORY.md index (Elements 3, 14)
evals/                          — eval cases + scores per run, hill-climbing loop (Element 13)
```

## Usage

Invoke the agent with a routed request: *"use_case: Task_Delegation — here is the vendor's 500-word requirements email; compress it into what our team actually needs to act on."*
It validates the text, compresses it to under 20% of its length, verifies the acceptance checks, and delivers the core summary with its loss_rate and the disclaimer.
