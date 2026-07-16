---
name: agent-builder
description: Builds a complete AI agent from three inputs — responsibilities, objective, and architecture design structure — by walking the 15-element template pack in this project. Use when the user says "build an agent for…", "create a new agent", "establish an AI agent", or provides an agent's responsibilities/objective/architecture. Do NOT use for editing the templates themselves or for general questions about the 15 elements (read reference/15-elements-reference.md directly for that).
---

# Agent Builder

Generate a complete, validated agent package from the user's three inputs, following this project's template pack.

## Inputs to collect

From the user's request, extract:
1. **Objective** — the single outcome the agent must achieve (+ success criteria if given)
2. **Responsibilities** — the duties the agent owns
3. **Architecture design structure** — topology (single agent / agent+skills / orchestrator+sub-agents) and target runtime

If any of the three is missing or too vague to derive a spec from, ask ONE consolidated round of clarifying questions (use AskUserQuestion when available). Infer the **complexity tier** (Lite / Standard / Full) from the architecture answer using the applicability matrix in `templates/02-development-guideline.md` — confirm it with the user only if genuinely ambiguous.

## Procedure

Work inside an output folder named `agents/<agent-name>/` (create it; kebab-case name derived from the objective unless the user names it).

1. **Intake** — copy the structure of `templates/00-intake-form.md` and fill every section (A–G) from the user's inputs. Infer each responsibility's trigger type (`on-demand` / `scheduled(cron)` / `event(source)`) from how the user describes it; a scheduled/event trigger, the acceptance signal (B), escalation path (F), and eval cadence (G) are always marked *(inferred — confirm)* when not stated explicitly. Mark all other inferred answers with *(inferred — confirm)* too. Save as `agents/<agent-name>/intake-form.md`.
2. **Specify** — fill `templates/01-agent-spec-template.md` element by element **in the dependency order from the guideline** (1&15 → 5&13 → 11,9,10 → 2,7,12 → 4,6,8 → 3,14). Respect the tier: out-of-tier elements get "N/A because…". Success criteria **and the acceptance signal** from intake section B must appear **verbatim** in Element 13. Stop conditions (Element 7 step budget/no-progress, Element 13 cycle cap, Element 11 caps) must be **concrete numbers**, never "reasonable" or "a few". Save as `agents/<agent-name>/agent-spec.md`.
3. **Build (Claude Code target)** — follow `templates/03-claude-code-mapping.md`:
   - Generate `.claude/agents/<agent-name>.md` from the skeleton (frontmatter: name, routing-rule description, exact tool allow-list, model) — including its `## Stop conditions` block with the concrete numbers from the spec.
   - Generate/extend `CLAUDE.md` with the project rules (Element 2) and directory layout.
   - Loop scaffolding, as activated by the intake (per the mapping's loop construct map): a scheduled/event trigger → `docs/trigger-setup.md` with the exact `/schedule` / `/loop` / hook configuration (**instructions only — never arm a trigger yourself**) plus `memory/state.md` from the resumable-state skeleton; eval cadence ≠ never → `evals/eval-cases.md` seeded from the success criteria + the 3 validation scenarios plus a copy of the library's `run-evals` skill (customized like any library skill); Element 8 maker/checker separation → the checker agent from the checker skeleton.
   - One skill file per Element 9 skill — **library first**: match each skill against the index table in `skills-library/README.md` (name/description/tags vs. the skill's purpose). On a match, copy the library skill into `.claude/skills/<name>/` and customize its `## Customization points` to this agent's spec (rewrite the description trigger, replace every `{{…}}`); after customizing, verify no `{{…}}` placeholders remain. No match → generate from the mapping's skill skeleton as usual.
   - `.mcp.json` + settings permissions only if Element 10 lists servers.
   - For a non-Claude-Code runtime, instead emit the framework-mapping notes from the guideline's Phase 3.
4. **Validate** — copy `templates/04-validation-checklist.md` as `agents/<agent-name>/validation-checklist.md`, pre-fill the tier and pass criteria, seed the eval-set table (cases filled from the success criteria + 3 scenarios; score columns blank until the first real run), then run the `/validate-agent` skill's static checks (placeholder scan, criteria verbatim, tool allow-list match, concrete stop conditions, responsibility coverage) and pre-fill what they prove — a static pass supports at most a 1. Leave runtime checks blank with a note to score after the first real run.
5. **Report** — end with: the file list produced, marking each skill `(from library: <name>)` or `(new)`; the tier and any inferred decisions needing confirmation; **which of the four loop layers are active** (agent / verification / event-driven / hill-climbing) and what remains manual (e.g. "run the `/schedule` command in `docs/trigger-setup.md` to arm the weekly trigger"); for each new skill that another agent could plausibly reuse, offer to save it to `skills-library/` via `/save-skill` (ask — never save silently); and the next step (run the typical input example end-to-end, then finish scoring the checklist and record the eval baseline).

## Rules

- Every generated agent inherits the **universal baseline** (§1) of `reference/behavioral-guidelines.md`; agents that write/edit code also inherit the **coding addendum** (§2). Copy the file to the target project as `docs/behavioral-guidelines.md`, reference the applicable parts from the generated `CLAUDE.md` and the agent body's Rules section (per the mapping's skeleton), and record which parts apply — plus any deviations — in spec Element 2.
- Ground every generated section in the user's three inputs — no invented responsibilities, tools, or success criteria. Anything assumed is labeled *(inferred — confirm)*.
- Never grant a generated agent tools beyond what its Element 11 table lists.
- Every generated agent has at least one **verifiable stop condition per active loop layer** (a concrete number the agent can check itself); never arm a scheduled/event trigger — generate the setup instructions and let the user run them.
- Consult `examples/research-report-agent/` (Standard tier) and `examples/competitor-intel-agent/` (Full tier: orchestrator + workers + checker + resumable state) as the canonical style references for depth and tone of a completed package.
- Do not modify files under `templates/` or `reference/` — they are the pack, not the output. `skills-library/` is different: it is user content you may read from freely and, with the user's confirmation, save skills back into.
