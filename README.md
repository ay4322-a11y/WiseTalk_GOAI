# WiseTalk — Workplace Communication Coaching Workbench

WiseTalk is an AI-native workplace communication coaching system built on a **"1+8+X+Security"** multi-agent architecture:

- **1 Router Agent** — entry gatekeeper (intent recognition, context memory)
- **8 Expert Agents** — one per communication model (STAR, SCRTV, MECE, PREP, SCQA, RIDE, FFC, Funnel)
- **X Shared Tools** — logic detection, emotional analysis, battle simulation, growth tracking
- **Two-Front Security Gateway** — pre-interceptor (injection filter) + post-validator (hallucination check)

The system is built from the **WiseTalk Master Spec v2.0** ([`_wisetalk_extracted.md`](_wisetalk_extracted.md)) using the 15-element agent pipeline.

## Architecture

Each of the 8 experts is an **individual, standalone agent** with its model hardcoded: the agent body's `## Model reference — <MODEL>` section bakes in that model's fill-in fields, generation prompt, and critique dimensions (no catalog read at runtime). The Router Agent dispatches to each by name. The 8 share the same architecture and coaching loop (mandatory fill-in → generate → critique → deliver); they differ only in the model they coach — Agent 8 (Funnel) is the exception (compress → deliver, no coaching loop).

[`reference/wisetalk-model-catalog.md`](reference/wisetalk-model-catalog.md) is the shared master of what differs; each agent's `claude-code/config/model-reference.md` is its section's human-readable copy.

## The 8 WiseTalk Expert Communication Agents

| Agent | Expert Agent | Model | Use cases (routed by Skill-1) | Skills |
|-------|--------------|-------|-------------------------------|--------|
| Agent 1 | [STAR Interviewer](examples/wisetalk-star-agent/) | STAR | `Job_Interview` · `Performance_Review` · `Project_Debrief` · `Resume_Writing` | Skill-3 · 7 · 13 |
| Agent 2 | [SCRTV Reporter](examples/wisetalk-scrtv-agent/) | SCRTV | `Project_Status_Report` · `Strategy_Proposal` · `Budget_Request` · `Issue_Escalation` | Skill-3 · 7 · 13 |
| Agent 3 | [MECE Architect](examples/wisetalk-mece-agent/) | MECE / Pyramid | `Logical_Analysis` · `Report_Outlining` · `Meeting_Minutes` · `Brainstorming_Structure` | Skill-3 · 7 · 13 |
| Agent 4 | [PREP Speaker](examples/wisetalk-prep-agent/) | PREP | `Elevator_Pitch` · `Quick_Meeting_Speech` · `Daily_Standup` · `Public_Comment` | Skill-3 · 7 · 13 |
| Agent 5 | [SCQA Analyst](examples/wisetalk-scqa-agent/) | SCQA | `Crisis_Management` · `Problem_Solving` · `Conflict_Resolution` · `Urgent_Incident` | Skill-3 · 7 · 13 |
| Agent 6 | [RIDE Negotiator](examples/wisetalk-ride-agent/) | RIDE | `Salary_Negotiation` · `Client_Deal` · `Vendor_Management` · `Resource_Allocation` | Skill-3 · 7 · 13 |
| Agent 7 | [FFC Master](examples/wisetalk-ffc-agent/) | FFC | `Team_Recognition` · `Relationship_Building` · `Peer_Feedback` · `Ice_Breaking` | Skill-3 · 7 · 13 |
| Agent 8 | [Funnel Refiner](examples/wisetalk-funnel-agent/) | Funnel | `Task_Delegation` · `Complex_Instruction` · `Information_Compression` · `Executive_Summary` | Skill-3 · 5 |

**Agent 8 note:** the Funnel Refiner is a "reverser" — it compresses long text (Skill-5) and does not run the coaching loop (no Skill-7/Skill-13). Its stop condition is mechanical (compressed to <20% of the original), not judgment-based.

## File map

| File | Role |
|------|------|
| [_wisetalk_extracted.md](_wisetalk_extracted.md) | **The Master Spec v2.0** — the WiseTalk specification text the whole system is built from |
| [reference/wisetalk-model-catalog.md](reference/wisetalk-model-catalog.md) | **The 8 WiseTalk models' master** — structure, fill-in fields, generation/compression prompts, critique dimensions, use cases per model; each agent's `config/model-reference.md` is its section's copy (baked in at build time, no runtime catalog reads) |
| [reference/behavioral-guidelines.md](reference/behavioral-guidelines.md) | **All-agents baseline** — universal guidelines (Think Before Acting · Goal-Driven Execution · Loop Discipline + communication style) inherited by every agent via Element 2 |
| [templates/00-intake-form.md](templates/00-intake-form.md) | **The input** — responsibilities, objective, architecture (+ derivation map to all 15 elements) |
| [templates/01-agent-spec-template.md](templates/01-agent-spec-template.md) | **The core** — 15-element specification template with tier tags, options & trade-offs |
| [templates/03-claude-code-mapping.md](templates/03-claude-code-mapping.md) | **The generator** — maps each element to Claude Code files, with copy-paste skeletons |
| [templates/04-validation-checklist.md](templates/04-validation-checklist.md) | **The gate** — per-element Definition-of-Done rubric with pass thresholds |
| [skills-library/](skills-library/README.md) | **The WiseTalk shared tools** — 8 reusable skills (Skills 4–12): MECE check, subtext/emotion decode, battle simulator, battle scoring, growth trends, injection filter, hallucination check, funnel compression |

## The shared tools (Skills 4–12)

The 8 skills in the library are the system's shared capability layer. Each is a complete, deterministic, tested skill:

| Skill | WiseTalk # | Role |
|-------|-----------|------|
| [mece-logic-checker](skills-library/mece-logic-checker/SKILL.md) | Skill-4 | Deterministic MECE check on argument points |
| [funnel-compression](skills-library/funnel-compression/SKILL.md) | Skill-5 | Compress text to <20% of original length |
| [subtext-emotion](skills-library/subtext-emotion/SKILL.md) | Skill-6 | Decode hidden intentions from exact words |
| [battle-simulator](skills-library/battle-simulator/SKILL.md) | Skill-8 | Role-play interrogation of a draft |
| [battle-scoring](skills-library/battle-scoring/SKILL.md) | Skill-9 | Score completed battle transcripts |
| [growth-trends](skills-library/growth-trends/SKILL.md) | Skill-10 | Aggregate battle-score history into trends |
| [injection-filter](skills-library/injection-filter/SKILL.md) | Skill-11 | Prompt-injection & sensitive-keyword pre-interceptor |
| [hallucination-check](skills-library/hallucination-check/SKILL.md) | Skill-12 | Post-validator for invented numeric claims + disclaimer |

*(Note: the two Loop Engineering source infographics, the original PDF, and the development methodology docs were removed in the Pure WiseTalk cleanup — the models' behavioral baseline and spec lineage links in `templates/` and `reference/` are retained because every agent's intake form, spec, and CLAUDE.md reference them.)*
