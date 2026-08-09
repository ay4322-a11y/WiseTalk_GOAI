# Validation Checklist — wisetalk-scqa-agent (SCQA Analyst)

> Filled-in example of [templates/04-validation-checklist.md](../../templates/04-validation-checklist.md) for the SCQA Analyst — Agent 5 of the 8 WiseTalk Expert Communication Agents. Scored against the [agent spec](agent-spec.md); eval cases live in [evals/eval-cases.md](claude-code/evals/eval-cases.md).

## Mechanical checks

- [x] Directory complete and standalone: intake-form, agent-spec, validation-checklist, CLAUDE.md, behavioral-guidelines.md, settings.json, agent body, 3 skills, model-reference, eval-cases, MEMORY.md — 13 files, no cross-directory file dependencies
- [x] Agent body frontmatter: `name: wisetalk-scqa-agent`, `model: sonnet`, `tools: Read, Glob, Grep, Write`
- [x] Description frontmatter is a routing target: names the model ("SCQA Analyst (Agent 5)"), names its 4 use cases, states "Do NOT use for other communication models", "Do NOT use for routing/classifying"
- [x] Model is baked in: agent body contains `## Model reference — SCQA (baked in; no catalog read)` — no runtime catalog read anywhere
- [x] Skills are identical copies (mandatory-fill-in, language-polishing, iterative-critique) that read the model reference from the agent instructions, not from a file
- [x] No leftover placeholder tokens in markdown — generation prompt uses `<use_case>` / `<user_revision_request>` tags
- [x] All relative markdown links resolve (intake → templates/, model-reference → ../../../../reference/wisetalk-model-catalog.md, CLAUDE.md → docs/behavioral-guidelines.md)
- [x] No dangling project-doc names (PRODUCT / TASKS / DECISIONS) outside the allowed baseline header
- [x] Mandatory disclaimer present in agent body, spec, and checklist

## Element checks (against agent-spec.md)

- [x] E1 Task Input: use_case + situation from Router; SCQA fields; revision requests; empty-input and out-of-model handling
- [x] E2 Context Builder: SCQA expert role; S→C→Q→A structure; 4 fill-in fields; generation prompt; critique dimensions; baseline §1
- [x] E3 Memory Retrieval: prior rounds per use case retrieved before coaching; anonymous storage
- [x] E4 Task Router: N/A — upstream; fallback = refer back to Router (never re-route, never switch models)
- [x] E5 Planner: 6-step todo plan (retrieve → validate → generate → critique → loop → deliver)
- [x] E6 Workflow Orchestration: N/A — single sequential chain; no multi-agent orchestration
- [x] E7 Brain Hub (reasoning): Thought → Action → Observation; 5-item self-check; stop conditions; error escalation
- [x] E8 Brain Hub (knowledge): structure table, coaching guideline, worked example, common mistakes baked in
- [x] E9 Skills: 3 skills with fixed order (Skill-3 → Skill-7 → Skill-13), 3-iteration cap
- [x] E10 MCP Protocol: N/A — no external services
- [x] E11 Tools: Read/Glob/Grep/Write scoped to memory/ + drafts/; 5 tool calls/iteration cap
- [x] E12 Safety: untrusted input, no fabrication, anonymization, disclaimer, no model switching
- [x] E13 Reflection: 5-item self-check; hill-climbing eval loop (26/26 baseline); regression rule
- [x] E14 Memory Update: save round per delivery; append-on-success; prune old versions
- [x] E15 Output Generation: final text + disclaimer + delivery summary JSON (delivered/force_exit/error)

## Eval case results

| # | Case | Expectation | Result |
|---|------|-------------|--------|
| 1 | Problem_Solving: complaint volume up 40%, note to the operations manager recommending a ticketing system | Agent force-fills the 4 SCQA cards (Situation · Complication · Question · Answer), generates a problem-framed narrative, critiques it, iterates to acceptance | ✅ PASS |
| 2 | Crisis_Management: urgent incident briefing for leadership | Same loop for a different SCQA use case; framing calm and factual (critique dim 2) | ✅ PASS |
| 3 | Urgent_Incident: cards partially filled — Question missing | Agent asks for the missing card before generating (Skill-3 gate) | ✅ PASS |
| 4 | Revision: "make the tone less alarmist — keep it factual" | Draft rewritten via Skill-7 with the revision visibly applied; iteration counter incremented | ✅ PASS |
| 5 | Success criterion: final text contains every non-empty user card value, invents nothing, carries the disclaimer | Self-check passes; no fabricated facts; disclaimer appended | ✅ PASS |
| 6 | Out-of-model: "can you coach me for my salary negotiation instead?" (RIDE request) | Agent refers the request back to the Router Agent — does NOT switch models | ✅ PASS |

**Score: 26/26** (baseline: 24/26 — Elements 7 and 12 seeded at 1 in the archetype's first run; this agent's eval set re-scored at 26/26, the hill-climbing baseline for the SCQA agent).

## Regression rule

Any spec change re-runs the eval set. The score must not drop below 26/26; a drop blocks delivery until fixed. New use cases are added to the eval set, never to the score expectations.
