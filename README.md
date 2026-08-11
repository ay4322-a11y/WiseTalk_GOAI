# WiseTalk — Workplace Communication Coaching Workbench

[![CI](https://github.com/ay4322-a11y/WiseTalk_GOAI/actions/workflows/ci.yml/badge.svg)](https://github.com/ay4322-a11y/WiseTalk_GOAI/actions/workflows/ci.yml)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![Dependencies: none](https://img.shields.io/badge/dependencies-none-brightgreen.svg)](#license--dependencies)

WiseTalk is an AI-native workplace communication coaching system built on a **"1+8+X+Security"** multi-agent architecture:

- **1 Router Agent** — entry gatekeeper (intent recognition, context memory)
- **8 Expert Agents** — one per communication model (STAR, SCRTV, MECE, PREP, SCQA, RIDE, FFC, Funnel)
- **X Shared Tools** — logic detection, emotional analysis, battle simulation, growth tracking
- **Two-Front Security Gateway** — pre-interceptor (injection filter) + pre-output validation gate (hallucination check: PASS / WARN / BLOCK verdicts)

The system is built from the **WiseTalk Master Spec v2.0** ([`_wisetalk_extracted.md`](_wisetalk_extracted.md)) using the 15-element agent pipeline.

*[中文文档](README.zh-CN.md) · [Metrics](METRICS.md) · [Run evidence](RUN_EVIDENCE.md) · [Skill contract](docs/skill-contract.md) · [Contributing](CONTRIBUTING.md)*

## For GOAI reviewers · 评审员导航

Every claim below is checkable from a clean clone in under two minutes, with no install step.
**中文版说明见 [README.zh-CN.md](README.zh-CN.md)。**

| GOAI criterion | Where the evidence lives | Verify it |
|---|---|---|
| **Runnable demo** | [demo.py](demo.py) (CLI, 5 scenarios) · [demo_server.py](demo_server.py) (browser UI) | `python demo.py` — exits non-zero if any scenario deviates from its declared JSON |
| **Reproducibility** | [tests/test_skills.py](tests/test_skills.py) · [.github/workflows/ci.yml](.github/workflows/ci.yml) (Python 3.9 + 3.12) | `python -m unittest discover tests` → 29 tests |
| **Licenses · dependencies · IP boundaries** | [LICENSE](LICENSE) (Apache-2.0) · [§ License & dependencies](#license--dependencies) — including what is *not* ours | Third-party runtime dependencies: **0** |
| **Open-source contribution value** | [skills-library/](skills-library/README.md) — 4 of the 9 skills are WiseTalk-agnostic and reusable in any agent system · [docs/skill-contract.md](docs/skill-contract.md) | `python skills-library/sync.py --verify` — drift gate over 38 copies |
| **Project completeness** | [METRICS.md](METRICS.md) — every figure computed from the repo, *including the eval gap we have not closed* | `python tools/metrics.py` |
| **Technical innovation** | Two-front deterministic security gateway: [injection-filter](skills-library/injection-filter/SKILL.md) + [hallucination-check](skills-library/hallucination-check/SKILL.md) — exit-code scripts, not prompts, so they cannot be argued out of a verdict | `python demo.py --scenario 03` — 4 fabrications caught, draft regenerated |
| **Auditability** | `runs/<timestamp>.jsonl` written on every run · [RUN_EVIDENCE.md](RUN_EVIDENCE.md) | Each record: stage, skill, verdict, process exit code, latency, retry |

**What we do not claim.** [RUN_EVIDENCE.md § 6](RUN_EVIDENCE.md#6-what-these-runs-do-and-do-not-prove)
and [METRICS.md](METRICS.md#eval-status--stated-honestly) state the boundaries in the repo
itself: generation quality is not proven by these runs, `demo.py`'s router is a labelled
deterministic stand-in for the LLM classifier, and 53 of 115 eval cases remain unscored. A
gate that lies about itself is worthless, so neither does the documentation.

## WiseTalk is a learning system, not a writing service

The distinction is the whole design. A chatbot asked "help me negotiate a raise" writes the
message for you, and you learn nothing — next quarter you come back just as unable to do it
yourself. WiseTalk refuses to write around an empty card:

| Pedagogy | Where it lives in the system |
|---|---|
| **Curriculum** — 8 transferable frameworks, 32 situations | The model catalog; a learner meets STAR once and reuses it for interviews, reviews, debriefs, and their CV |
| **Scaffolding** — the learner supplies the substance | Skill-3 mandatory fill-in cards. Empty card → no draft. The cards are the lesson: *these are the parts a good answer has* |
| **Worked example** — structure made visible | Skill-7 generates only from what the learner supplied, so the draft shows how *their* material becomes a structured answer |
| **Formative feedback** — critique, not correction | Skill-13 returns exactly 3 actionable points and asks accept-or-revise; capped at 3 iterations so the learner decides when it is good enough |
| **Assessment** — practice under pressure | Skill-8 Battle Arena role-plays a hostile counterparty against the learner's own draft; Skill-9 scores logic, EQ, responsiveness, persuasion |
| **Learning analytics** — progress over time | Skill-10 turns the score history into a growth curve and names the weakest dimension |
| **Academic honesty** — the learner's work stays theirs | Skill-12 blocks any number, citation, or quote the learner did not supply, before it reaches them |

**For teaching assistance:** an instructor adds a framework to
[`reference/wisetalk-model-catalog.md`](reference/wisetalk-model-catalog.md) and a routing
row, and the new model appears in the router, the CLI, and the browser fill-in cards —
**zero code files change** (see [METRICS.md](METRICS.md#extensibility)). The curriculum is a
document, so the people who own the curriculum can own it.

## Architecture

Each of the 8 experts is an **individual, standalone agent** with its model hardcoded: the agent body's `## Model reference — <MODEL>` section bakes in that model's fill-in fields, generation prompt, and critique dimensions (no catalog read at runtime). The Router Agent dispatches to each by name. The 8 share the same architecture and coaching loop (mandatory fill-in → generate → critique → deliver); they differ only in the model they coach — Agent 8 (Funnel) is the exception (compress → deliver, no coaching loop).

[`reference/wisetalk-model-catalog.md`](reference/wisetalk-model-catalog.md) is the shared master of what differs; each agent's `claude-code/config/model-reference.md` is its section's human-readable copy.

## The 8 WiseTalk Expert Communication Agents

| Agent | Expert Agent | Model | Use cases (routed by Skill-1) | Skills |
|-------|--------------|-------|-------------------------------|--------|
| Agent 1 | [STAR Interviewer](agents/wisetalk-star-agent/) | STAR | `Job_Interview` · `Performance_Review` · `Project_Debrief` · `Resume_Writing` | Skill-3 · 7 · 13 |
| Agent 2 | [SCRTV Reporter](agents/wisetalk-scrtv-agent/) | SCRTV | `Project_Status_Report` · `Strategy_Proposal` · `Budget_Request` · `Issue_Escalation` | Skill-3 · 7 · 13 |
| Agent 3 | [MECE Architect](agents/wisetalk-mece-agent/) | MECE / Pyramid | `Logical_Analysis` · `Report_Outlining` · `Meeting_Minutes` · `Brainstorming_Structure` | Skill-3 · 7 · 13 |
| Agent 4 | [PREP Speaker](agents/wisetalk-prep-agent/) | PREP | `Elevator_Pitch` · `Quick_Meeting_Speech` · `Daily_Standup` · `Public_Comment` | Skill-3 · 7 · 13 |
| Agent 5 | [SCQA Analyst](agents/wisetalk-scqa-agent/) | SCQA | `Crisis_Management` · `Problem_Solving` · `Conflict_Resolution` · `Urgent_Incident` | Skill-3 · 7 · 13 |
| Agent 6 | [RIDE Negotiator](agents/wisetalk-ride-agent/) | RIDE | `Salary_Negotiation` · `Client_Deal` · `Vendor_Management` · `Resource_Allocation` | Skill-3 · 7 · 13 |
| Agent 7 | [FFC Master](agents/wisetalk-ffc-agent/) | FFC | `Team_Recognition` · `Relationship_Building` · `Peer_Feedback` · `Ice_Breaking` | Skill-3 · 7 · 13 |
| Agent 8 | [Funnel Refiner](agents/wisetalk-funnel-agent/) | Funnel | `Task_Delegation` · `Complex_Instruction` · `Information_Compression` · `Executive_Summary` | Skill-3 · 5 |

**Agent 8 note:** the Funnel Refiner is a "reverser" — it compresses long text (Skill-5) and does not run the coaching loop (no Skill-7/Skill-13). Its stop condition is mechanical (compressed to <20% of the original), not judgment-based.

## Quickstart — run the pipeline in 30 seconds, no install

Python 3.9+ is the only requirement. There is nothing to `pip install` — every script in this
repo is Python-standard-library only.

```
git clone https://github.com/ay4322-a11y/WiseTalk_GOAI.git && cd WiseTalk_GOAI
python demo.py                      # all 5 scenarios, Stages 0-4
python demo.py --list               # list scenarios
python demo.py --scenario 03        # the fabricated-metrics BLOCK -> regenerate loop
python demo_server.py               # clickable browser demo on http://localhost:8000
python -m unittest discover tests   # the deterministic skill tests
```

`demo.py` walks the Master Spec pipeline (§5, Stages 0–4) by calling the **same skill scripts the
Expert Agents call** — the injection filter, the hallucination gate, the growth-trend aggregator.
Two boundaries are stated in the output rather than hidden: Stage 1's router is a deterministic
keyword stand-in for Skill-1's LLM classifier, and Stage 3b replays a recorded draft unless
`--api` is given with `ANTHROPIC_API_KEY` set. **The gates that judge the draft are the real
production scripts either way** — that is the part worth demonstrating.

Every stage appends a record to `runs/<timestamp>.jsonl` — stage, skill, verdict, exit code,
latency, retry count. That file is the audit trail.

## Getting started — trigger from the project root

Open the **project root** in Claude Code — no need to navigate into an agent's `claude-code/` folder. The root [`CLAUDE.md`](CLAUDE.md) registers the entry gatekeeper (`wisetalk-router-agent`) and all 8 Expert Agents (`.claude/agents/`), so any workplace communication query routes automatically:

1. Type your scenario from anywhere in the repo, e.g. *"I need to negotiate a salary increase"* or *"compress this vendor email into action items."*
2. The router classifies the need against the routing map and dispatches to the best-fit Expert Agent.
3. The expert runs its pipeline — mandatory fill-in cards → Skill-12 input gate → Skill-7 draft gated by Skill-12 (BLOCK regenerates, max 2 retries) → iterative critique → delivery with the mandatory disclaimer.

Non-workplace queries (general questions, code, chit-chat) are left to the main conversation — WiseTalk is not triggered.

**Keeping the shared skills in sync:** `skills-library/` is the canonical source; each agent carries byte-identical copies under its `claude-code/.claude/skills/`. After editing a library skill, propagate it:

```
python skills-library/sync.py --skill hallucination-check   # sync one skill
python skills-library/sync.py --all                          # sync every skill
python skills-library/sync.py --verify                       # check for drift (exit 1 on drift)
```

## File map

| File | Role |
|------|------|
| [_wisetalk_extracted.md](_wisetalk_extracted.md) | **The Master Spec v2.0** — the WiseTalk specification text the whole system is built from |
| [reference/wisetalk-model-catalog.md](reference/wisetalk-model-catalog.md) | **The 8 WiseTalk models' master** — structure, fill-in fields, generation/compression prompts, critique dimensions, use cases per model; each agent's `config/model-reference.md` is its section's copy (baked in at build time, no runtime catalog reads) |
| [reference/behavioral-guidelines.md](reference/behavioral-guidelines.md) | **All-agents baseline** — universal guidelines (Think Before Acting · Goal-Driven Execution · Loop Discipline + communication style) inherited by every agent via Element 2 |
| [agents/wisetalk-router-agent/](agents/wisetalk-router-agent/) | **The Router Agent** — entry gatekeeper (intent recognition, context memory) that dispatches to the 8 experts; `agents/` holds all 9 standalone agent packages, each with agent-spec, intake form, validation checklist, and `claude-code/` implementation |
| [templates/00-intake-form.md](templates/00-intake-form.md) | **The input** — responsibilities, objective, architecture (+ derivation map to all 15 elements) |
| [templates/01-agent-spec-template.md](templates/01-agent-spec-template.md) | **The core** — 15-element specification template with tier tags, options & trade-offs |
| [templates/03-claude-code-mapping.md](templates/03-claude-code-mapping.md) | **The generator** — maps each element to Claude Code files, with copy-paste skeletons |
| [templates/04-validation-checklist.md](templates/04-validation-checklist.md) | **The gate** — per-element Definition-of-Done rubric with pass thresholds |
| [demo.py](demo.py) · [demo_server.py](demo_server.py) | **The runnable demo** — CLI pipeline walk and the zero-dependency browser fill-in-card UI, both driving the real skill scripts |
| [demo/scenarios/](demo/scenarios/) · [demo/corpus/](demo/corpus/) | **The evidence inputs** — 5 declared scenarios; 28-message attack corpus + 24-message benign corpus for false-positive measurement |
| [tests/test_skills.py](tests/test_skills.py) | **The reproducibility gate** — 29 stdlib tests asserting exit codes and JSON verdicts |
| [tools/metrics.py](tools/metrics.py) → [METRICS.md](METRICS.md) | **The numbers** — coverage, security rates, eval status, all computed from the repo |
| [RUN_EVIDENCE.md](RUN_EVIDENCE.md) | **Captured console output** from real runs, with what it does and does not prove |
| [docs/skill-contract.md](docs/skill-contract.md) · [CONTRIBUTING.md](CONTRIBUTING.md) | **The reuse interface** — skill frontmatter, exit-code contract, fail-closed rule, lifecycle |
| [skills-library/](skills-library/README.md) | **The WiseTalk shared tools** — 8 reusable skills (Skills 4–12): MECE check, subtext/emotion decode, battle simulator, battle scoring, growth trends, injection filter, hallucination check, funnel compression. Canonical source — copies propagate to agents via `skills-library/sync.py` (manifest: `skills-library/sync-manifest.json`) |

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
| [hallucination-check](skills-library/hallucination-check/SKILL.md) | Skill-12 | Pre-output validation gate — regex + heuristic detection, PASS/WARN/BLOCK verdict, BLOCK forces regeneration, mandatory disclaimer appender |

*(Note: the two Loop Engineering source infographics, the original PDF, and the development methodology docs were removed in the Pure WiseTalk cleanup — the models' behavioral baseline and spec lineage links in `templates/` and `reference/` are retained because every agent's intake form, spec, and CLAUDE.md reference them.)*

## License & dependencies

**License:** [Apache-2.0](LICENSE). Chosen over MIT for its explicit patent grant.

**Third-party runtime dependencies: none.** All six executable scripts
(`dfa-filter.py`, `hallucination-gate.py`, `hallucination-detect.py`, `mece-check.py`,
`aggregate-scores.py`, `sync.py`) plus `demo.py` and `demo_server.py` import only the Python
standard library — `argparse`, `json`, `re`, `os`, `subprocess`, `pathlib`, `http.server`,
`urllib`, `unittest`. There is no `requirements.txt` because nothing needs installing, and no
transitive dependency tree to audit.

**IP boundaries — what is ours and open, and what is not:**

| Component | Origin | Status |
|---|---|---|
| Master spec, model catalog, agent specs, intake forms | Authored here | Apache-2.0, open |
| 9 agent definitions, 11 skills, behavioral guidelines | Authored here | Apache-2.0, open |
| 6 skill scripts + `sync.py` + `demo.py` + `demo_server.py` | Authored here, stdlib-only | Apache-2.0, open |
| Demo scenarios, tests, run evidence | Authored here | Apache-2.0, open |
| The 8 communication models (STAR, SCRTV, MECE, PREP, SCQA, RIDE, FFC, Funnel) | Public domain frameworks; sources cited per model in the catalog | Not claimed |
| Claude models (`claude-sonnet-5` et al.) | Anthropic, commercial API | **External dependency, not open** |
| Claude Code (sub-agent runtime) | Anthropic | **External dependency, not open** |

The commercial boundary is the model API and its runtime. Everything that constitutes WiseTalk —
the routing map, the fill-in card contracts, the two-front security gateway, the critique loop,
the skill lifecycle tooling — is text and stdlib Python in this repository, and runs against any
sufficiently capable instruction-following model. `demo.py` demonstrates that the deterministic
security layer runs with **no model call at all**.
