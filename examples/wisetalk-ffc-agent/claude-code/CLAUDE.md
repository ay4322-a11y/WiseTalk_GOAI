# WiseTalk FFC Agent Project

Agent 7 of the WiseTalk AI Communication Coach system: the **FFC Master**. The `wisetalk-ffc-agent` sub-agent coaches a user through the FFC recognition model — forces the 3 mandatory fill-in cards (Feeling · Fact · Compare), generates warm, specific, behaviour-based praise, runs the iterative critique loop, and delivers the final text (generated from `../agent-spec.md` using the [Claude Code mapping](../../../templates/03-claude-code-mapping.md)).

One of 8 individual Expert Agents (STAR / SCRTV / MECE / PREP / SCQA / RIDE / FFC / Funnel) — each with its model hardcoded, dispatched by the Router Agent (`wisetalk-router-agent`). This agent serves **FFC only**.

## Rules (spec Element 2)

- All agents follow the universal baseline in @docs/behavioral-guidelines.md §1 (Think Before Acting · Goal-Driven Execution · Loop Discipline + its communication style). The coding addendum (§2) doesn't apply — no agent here writes code. No deviations.
- The agent body's `## Model reference — FFC` section is the **baked-in source of truth** for this model: fill-in fields, generation prompt, critique dimensions. No catalog file is read at runtime; `config/model-reference.md` is the human-readable copy (keep it in sync with the agent body).
- Skill order is fixed: Skill-3 (mandatory fill-in) → Skill-7 (language polishing) → Skill-13 (iterative critique) → accept/modify loop, capped at 3 iterations.
- Optional Battle Arena: after accepting a draft, the user can type `battle-simulator` (Skill-8) to role-play a hostile counterparty against the delivered text; when the arena ends, run Skill-9 `battle-scoring` on the transcript.
- Skill-12 `hallucination-check` runs on every accepted draft before delivery: invented values the user never provided are wrapped in the `[AI Inferred: Please verify]` marker and the mandatory disclaimer is appended (fail-soft — it never blocks delivery).
- Never invent data the user didn't provide — placeholder-filled content is marked `[AI Inferred: Please verify]`; every output carries the mandatory disclaimer.
- Agent writes are limited to `drafts/` and `memory/`. Any other write requires explicit user approval.
- Requests for other communication models are **referred back to the Router Agent** — this agent never switches models.
- Output is always the final text + disclaimer + delivery summary JSON (see the agent body's `## Output` section).

## Directory layout

```
config/model-reference.md       — FFC reference (extracted from the shared reference/wisetalk-model-catalog.md; agents read-only)
docs/behavioral-guidelines.md   — all-agents baseline (copied from the template pack's reference/)
memory/                         — drafts, critique rounds, MEMORY.md index (Elements 3, 14)
evals/                          — eval cases + scores per run, hill-climbing loop (Element 13)
```

## Usage

Invoke the agent with a routed request: *"use_case: Team_Recognition — I want to recognise a team member who turned a difficult client meeting around last week."*
It forces the 3 FFC cards, generates the recognition message, critiques it in 3 points, iterates with the user, and delivers the final text with the disclaimer.
