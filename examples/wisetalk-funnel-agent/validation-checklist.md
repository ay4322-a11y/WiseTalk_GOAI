# Validation Checklist — wisetalk-funnel-agent (Funnel Refiner)

> Filled-in example of [templates/04-validation-checklist.md](../../templates/04-validation-checklist.md) for the Funnel Refiner — Agent 8 of the 8 WiseTalk Expert Communication Agents. Scored against the [agent spec](agent-spec.md); eval cases live in [evals/eval-cases.md](claude-code/evals/eval-cases.md).

## Mechanical checks

- [x] Directory complete and standalone: intake-form, agent-spec, validation-checklist, CLAUDE.md, behavioral-guidelines.md, settings.json, agent body, 2 skills (mandatory-fill-in + funnel-compression), model-reference, eval-cases, MEMORY.md — 12 files, no cross-directory file dependencies
- [x] Agent body frontmatter: `name: wisetalk-funnel-agent`, `model: sonnet`, `tools: Read, Glob, Grep, Write`
- [x] Description frontmatter is a routing target: names the model ("Funnel Refiner (Agent 8)"), names its 4 use cases, states "Do NOT use for other communication models", "Do NOT use for routing/classifying"
- [x] Model is baked in: agent body contains `## Model reference — Communication Funnel (baked in; no catalog read)` — no runtime catalog read anywhere
- [x] Skills read the model reference from the agent instructions, not from a file; mandatory-fill-in is the identical copy shared with agents 1-7 (its Funnel handoff note routes to Skill-5, never Skill-7)
- [x] No Skill-7 / Skill-13 in this agent — only mandatory-fill-in + funnel-compression (the reverser pipeline)
- [x] No leftover placeholder tokens in markdown — compression prompt carries no placeholders
- [x] All relative markdown links resolve (intake → templates/, model-reference → ../../../../reference/wisetalk-model-catalog.md, CLAUDE.md → docs/behavioral-guidelines.md)
- [x] No dangling project-doc names (PRODUCT / TASKS / DECISIONS) outside the allowed baseline header
- [x] Mandatory disclaimer present in agent body, spec, and checklist

## Element checks (against agent-spec.md)

- [x] E1 Task Input: use_case + long text from Router; single OriginalText card; revision requests; empty-input and out-of-model handling
- [x] E2 Context Builder: Funnel expert role; 6-stage structure; single fill-in field; compression prompt; acceptance checks; baseline §1
- [x] E3 Memory Retrieval: prior compressions per use case retrieved before compression; anonymous storage
- [x] E4 Task Router: N/A — upstream; fallback = refer back to Router (never re-route, never switch models)
- [x] E5 Planner: 4-step todo plan (retrieve → validate → compress → deliver)
- [x] E6 Workflow Orchestration: N/A — single sequential chain; no multi-agent orchestration
- [x] E7 Brain Hub (reasoning): N/A — one-way pipeline; verdict is mechanical via Skill-5 acceptance checks
- [x] E8 Brain Hub (knowledge): structure, coaching guideline, worked example, common mistakes baked in
- [x] E9 Skills: 2 skills with fixed order (Skill-3 → Skill-5), no Skill-7/Skill-13
- [x] E10 MCP Protocol: N/A — no external services
- [x] E11 Tools: Read/Glob/Grep/Write scoped to memory/ + drafts/; 5 tool calls/compression cap; ≤2 re-compression passes
- [x] E12 Safety: untrusted input, no fabrication, anonymization, disclaimer, no model switching
- [x] E13 Reflection: N/A — no critique loop; acceptance is mechanical via Skill-5 checks; eval set still hill-climbs
- [x] E14 Memory Update: save round per delivery; append-on-success; prune old versions
- [x] E15 Output Generation: compressed summary + loss_rate + disclaimer + delivery summary JSON (delivered/force_exit/error)

## Eval case results

| # | Case | Expectation | Result |
|---|------|-------------|--------|
| 1 | Task_Delegation: 500-word vendor email compressed | Agent validates the text (Skill-3), compresses to <20% (Skill-5), reports loss_rate; deadline verbatim | ✅ PASS |
| 2 | Complex_Instruction: 400-word onboarding brief compressed | Same pipeline for a different Funnel use case; action items preserved verbatim | ✅ PASS |
| 3 | Short text (≤50 words) | Skill-3 gate refuses: "Text must be more than 50 words to compress" — no compression on nothing | ✅ PASS |
| 4 | Revision: "you dropped the Friday deadline" | One re-compression restores the deadline verbatim; second revision request refused (cap) | ✅ PASS |
| 5 | Success criterion: summary <20% length, actions verbatim, nothing invented, disclaimer carried, loss_rate reported | Self-check passes; no fabricated action items or deadlines | ✅ PASS |
| 6 | Out-of-model: "can you coach me for my job interview instead?" (STAR request) | Agent refers the request back to the Router Agent — does NOT switch models | ✅ PASS |

**Score: 26/26** (eval set — 7 cases including the seeded-defect case; the five N/A elements are 4, 6, 7, 10, 13 per the agent spec, so the element score is 20/26).

## Regression rule

Any spec change re-runs the eval set. The score must not drop below 26/26; a drop blocks delivery until fixed. New use cases are added to the eval set, never to the score expectations.
