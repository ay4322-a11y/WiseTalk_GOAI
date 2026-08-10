# WiseTalk RIDE Agent Project

Agent 6 of the WiseTalk AI Communication Coach system: the **RIDE Negotiator**. The `wisetalk-ride-agent` sub-agent coaches a user through the RIDE persuasion model — forces the 4 mandatory fill-in cards (Risk · Interest · Difference · Effect), generates a polished negotiation speech, runs the iterative critique loop, and delivers the final text (generated from `../agent-spec.md` using the [Claude Code mapping](../../../templates/03-claude-code-mapping.md)).

One of 8 individual Expert Agents (STAR / SCRTV / MECE / PREP / SCQA / RIDE / FFC / Funnel) — each with its model hardcoded, dispatched by the Router Agent (`wisetalk-router-agent`). This agent serves **RIDE only**.

## Rules (spec Element 2)

- All agents follow the universal baseline in @docs/behavioral-guidelines.md §1 (Think Before Acting · Goal-Driven Execution · Loop Discipline + its communication style). The coding addendum (§2) doesn't apply — no agent here writes code. No deviations.
- The agent body's `## Model reference — RIDE` section is the **baked-in source of truth** for this model: fill-in fields, generation prompt, critique dimensions. No catalog file is read at runtime; `config/model-reference.md` is the human-readable copy (keep it in sync with the agent body).
- Skill order is fixed: Skill-3 (mandatory fill-in, with upfront sufficiency gate + batch collection) → Skill-6 (subtext-emotion, when the user pastes the counterparty's exact words) → Skill-7 (language polishing) → Skill-13 (iterative critique) → accept/modify loop, capped at 3 iterations.
- Optional Battle Arena: after accepting a draft, the user can type `battle-simulator` (Skill-8) to role-play a hostile counterparty against the delivered text; when the arena ends, run Skill-9 `battle-scoring` on the transcript.
- Skill-12 `hallucination-check` is a pre-output gate: it validates the fill-in cards before generation and every Skill-7 draft before the user sees it. BLOCK triggers regeneration (max 2 retries); WARN marks invented values `[AI Inferred: Please verify]` with a gap note; the mandatory disclaimer is always appended.
- Never invent data the user didn't provide — Skill-12's gate blocks fabricated content and forces regeneration; placeholder-filled content is marked `[AI Inferred: Please verify]`; every output carries the mandatory disclaimer.
- Agent writes are limited to `drafts/` and `memory/`. Any other write requires explicit user approval.
- Requests for other communication models are **referred back to the Router Agent** — this agent never switches models.
- Output is always the final text + disclaimer + delivery summary JSON (see the agent body's `## Output` section).

## Directory layout

```
config/model-reference.md       — RIDE reference (extracted from the shared reference/wisetalk-model-catalog.md; agents read-only)
docs/behavioral-guidelines.md   — all-agents baseline (copied from the template pack's reference/)
memory/                         — drafts, critique rounds, MEMORY.md index (Elements 3, 14)
evals/                          — eval cases + scores per run, hill-climbing loop (Element 13)
```

## Usage

Invoke the agent with a routed request: *"use_case: Salary_Negotiation — my boss rejected my budget proposal because he thinks it's too high."*
It forces the 4 RIDE cards, generates the negotiation speech, critiques it in 3 points, iterates with the user, and delivers the final text with the disclaimer.
