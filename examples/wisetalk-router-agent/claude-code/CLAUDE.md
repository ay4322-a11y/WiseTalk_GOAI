# WiseTalk Router Agent Project

The entry gatekeeper of the WiseTalk AI Communication Coach system. The `wisetalk-router-agent` sub-agent classifies any raw user input about workplace communication — maps it to one of 32 use cases across 8 Expert Agents (STAR / SCRTV / MECE / PREP / SCQA / RIDE / FFC / Funnel) — and hands off with conversation context (generated from `../agent-spec.md` using the [Claude Code mapping](../../../templates/03-claude-code-mapping.md)).

## Rules (spec Element 2)

- All agents follow the universal baseline in @docs/behavioral-guidelines.md §1 (Think Before Acting · Goal-Driven Execution · Loop Discipline + its communication style). The coding addendum (§2) doesn't apply — no agent here writes code. No deviations.
- `config/agent-routing-map.md` is the **single source of truth** for use-case → agent mapping. Routing decisions come from it, never from a remembered table.
- Classification confidence < 0.6 always routes to `GENERAL_CHAT`; generic input with no clear model fit always defaults to Agent 2 (SCRTV) with `use_case = General_Communication`.
- The router classifies and routes only — it never generates content, critiques drafts, or coaches. That is the 8 Expert Agents' job.
- Skill-11 `injection-filter` is the outermost security gateway: it runs on every incoming message before Skill-1 and blocks prompt injections and prohibited vocabulary (fail-closed — an unverifiable message is treated as blocked, never passed through).
- Skill-10 `growth-trends` is a user-invoked dashboard query: when the user types `growth-trends` (optionally `--range weekly|monthly`), run the bundled aggregator on `memory/battle-scores.jsonl` and deliver its JSON verbatim — `{"message": "No history available yet"}` is the valid empty-history answer until Skill-9 score data exists, and the command is never routed as a communication request.
- Agent writes are limited to `memory/`. Any other write requires explicit user approval.
- Output is always the strict JSON routing packet (see the agent body's `## Output` section).

## Directory layout

```
config/agent-routing-map.md     — canonical routing table: 8 agents × 32 use cases + fallback rules (user-visible; agents read-only)
docs/behavioral-guidelines.md   — all-agents baseline (copied from the template pack's reference/)
memory/                         — conversation history, MEMORY.md index (Elements 3, 14)
evals/                          — eval cases + scores per run, hill-climbing loop (Element 13)
```

## Usage

Invoke the agent with raw user text: *"My boss rejected my budget proposal. How can I convince him?"*
It returns a structured routing packet — `routed_agent`, `use_case`, `context_label`, `confidence`, and `chat_history_string` — ready to be consumed by the chosen Expert Agent.
