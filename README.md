# AI Agent Development Template Pack

A reusable template system for establishing AI agents, built on the **15-element agent pipeline** from *AI Agent Development Templates.pdf* (Agent 全流程时序图解).

**Input:** an agent's **responsibilities** (职责) · **objective** (目标) · **architecture design structure** (架构设计)
**Output:** a fully specified, built, and validated AI agent.

## Quick start

**One command (Claude Code):** run `/agent-builder` and provide the three inputs — it generates the completed intake form, the 15-element spec, the Claude Code agent files, and a pre-filled validation checklist.

**Manual (any framework):**
1. Fill in [templates/00-intake-form.md](templates/00-intake-form.md) — capture objective, responsibilities, architecture, and pick a complexity tier.
2. Complete [templates/01-agent-spec-template.md](templates/01-agent-spec-template.md) — specify the 15 elements, following the phase order in [templates/02-development-guideline.md](templates/02-development-guideline.md).
3. Build ([templates/03-claude-code-mapping.md](templates/03-claude-code-mapping.md) for Claude Code) and score against [templates/04-validation-checklist.md](templates/04-validation-checklist.md) — the agent is established when it passes.

## File map

| File | Role |
|------|------|
| [reference/15-elements-reference.md](reference/15-elements-reference.md) | Source of truth: the 15 elements distilled from the PDF, with original Chinese terms |
| [reference/loop-engineering-reference.md](reference/loop-engineering-reference.md) | **The loop overlay** — Loop Engineering (trigger → execute → verify → remember → retry/escalate/stop): 4 loop layers, 6 engineering components, and guardrails, mapped onto the 15 elements |
| [reference/behavioral-guidelines.md](reference/behavioral-guidelines.md) | **All-agents baseline** — universal guidelines (Think Before Acting · Goal-Driven Execution · Loop Discipline + communication style) inherited by every agent via Element 2, plus a coding addendum (Simplicity First · Surgical Changes · code output style) for agents that write code |
| [templates/00-intake-form.md](templates/00-intake-form.md) | **The input** — responsibilities, objective, architecture (+ derivation map to all 15 elements) |
| [templates/01-agent-spec-template.md](templates/01-agent-spec-template.md) | **The core** — 15-element specification template with tier tags, options & trade-offs |
| [templates/02-development-guideline.md](templates/02-development-guideline.md) | **The process** — 5 phases (intake → specify → build → validate → iterate) + element applicability matrix |
| [templates/03-claude-code-mapping.md](templates/03-claude-code-mapping.md) | **The generator** — maps each element to Claude Code files, with copy-paste skeletons |
| [templates/04-validation-checklist.md](templates/04-validation-checklist.md) | **The gate** — per-element Definition-of-Done rubric with pass thresholds |
| [skills-library/](skills-library/README.md) | **The reuse layer** — user-owned catalog of pre-built skills; copy & customize into new agents, save new ones back with `/save-skill` |
| [.claude/skills/agent-builder/SKILL.md](.claude/skills/agent-builder/SKILL.md) | **The automation** — `/agent-builder` runs the whole flow from the three inputs |
| [.claude/skills/save-skill/SKILL.md](.claude/skills/save-skill/SKILL.md) | **The library writer** — `/save-skill` generalizes a built skill and saves it into `skills-library/` |
| [.claude/skills/validate-agent/SKILL.md](.claude/skills/validate-agent/SKILL.md) | **The static gate** — `/validate-agent` pre-scores the checklist's statically checkable rows (leftover placeholders, criteria verbatim, tool allow-list, concrete stop conditions) |
| [examples/research-report-agent/](examples/research-report-agent/) | **Worked example** — a Standard-tier market research agent, from intake to generated Claude Code files |

## The 15 elements at a glance

| Intake | Understanding | Dispatch & planning | Execution loop | Capability stack | Quality & learning | Delivery |
|--------|---------------|---------------------|----------------|------------------|--------------------|----------|
| 1 Task Input | 2 Context Builder · 3 Memory Retrieval | 4 Router · 5 Planner · 6 Workflow (DAG) | 7 Reasoning · 8 Brain Hub · 12 Observation | 9 Skills · 10 MCP · 11 Tools | 13 Reflection · 14 Memory Update | 15 Output Generation |

Not every agent needs all 15 at full depth — the [applicability matrix](templates/02-development-guideline.md#element-applicability-matrix) defines three tiers: **Lite** (~7 required), **Standard** (~13), **Full** (all 15).

## The core loop every agent should exhibit

User input → understand & recall memory → decompose & plan → autonomously schedule tools & execute → self-check & correct → persist experience → deliver standardized result.

That is the **inner** loop. [Loop Engineering](reference/loop-engineering-reference.md) adds the outer rings: what starts a run (on-demand / scheduled / event triggers), what proves it done (a verifiable acceptance signal), what stops it (self-checkable stop conditions), and what improves the next one (an eval set scored across runs).

*(LLM 负责思考，Agent 负责把事情做完 — the LLM does the thinking; the agent gets things done.)*
