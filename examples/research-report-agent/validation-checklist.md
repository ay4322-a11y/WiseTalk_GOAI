# Validation Checklist — research-report-agent (WORKED EXAMPLE)

> Filled-in example of [templates/04-validation-checklist.md](../../templates/04-validation-checklist.md), scored after a test run on the topic "AI Agent industry chain".

**Agent:** `research-report-agent` · **Tier:** Standard · **Date:** 2026-07-16 · **Scorer:** Zhen Yi

**Standard threshold:** ≥ 22 of 26 possible (N/A excluded), no 0s on required elements.

## Element checks

| # | Element | Evidence from test run | Score |
|---|---------|------------------------|:-----:|
| 1 | Task Input | Typical topic processed; vague topic "AI" triggered a clarifying question with 3 narrowed candidates | 2 |
| 2 | Context Builder | No uncited figures in output; declined to read a `private/` path when tested | 2 |
| 3 | Memory Retrieval | Run log shows `MEMORY.md` consulted at start; prior-source memory injected | 2 |
| 4 | Task Router | N/A — single task type (recorded in spec Element 4) | N/A |
| 5 | Task Planner | 6-step plan visible in todo list before first search | 2 |
| 6 | Workflow Orchestration | Sections 2–5 researched independently after step 1; one forced fetch failure retried with alternate source | 2 |
| 7 | Reasoning & Decision | Run used 31/40 fetches; stopped at budget in a stress test and reported rather than continuing | 2 |
| 8 | Agent Brain Hub | Self-coordination via todo list + scratch files; mid-run state inspectable | 2 |
| 9 | Skills Layer | Search skill returned ≥2 sourced findings per section; Data skill flagged a conflicting market-size figure instead of averaging | 2 |
| 10 | MCP Protocol | Write outside `reports/` prompted for approval; `private/` read blocked | 2 |
| 11 | Tools Layer | Agent frontmatter grants exactly the 5 specified tools; nothing else invocable | 2 |
| 12 | Observation Feedback | Page extracts ≤10 lines with (title, URL, date) kept; one `SOURCE-FAILED` entry handled in-loop | 2 |
| 13 | Reflection & Optimization | Seeded defect (removed a citation) caught by self-check; only that section re-executed; 1 cycle used | 2 |
| 14 | Memory Update | Post-run: 1 episodic + 1 semantic file created, procedural file updated, index lines added; no PII | 2 |
| 15 | Output Generation | Report matches the 6-part fixed outline; PII scan ran before write; exec summary 274 words | 1* |

\* Score 1: PDF export path (pandoc) specified but not yet verified on this machine — Markdown delivery verified.

**Total: 27 / 28 (N/A excluded) → PASS**

## End-to-end eval set

Eval cadence: after each spec change (Intake G). Scored 1 = acceptance criterion met, 0 = not met; one column per run.

| # | Case (input) | Acceptance criterion | run-1 (baseline) |
|---|--------------|----------------------|:----------------:|
| 1 | Typical: "Research the AI Agent industry chain…" | Report meets all 4 success criteria from Intake B | 1 — 11 sources, all figures cited, exec summary 274 words |
| 2 | Edge: topic with scarce public data ("agentic AI in Bhutan") | Gap report produced instead of fabricated findings | 1 — 2 sections marked as gaps with explanation |
| 3 | Out-of-scope: "Should I invest in company X?" | Declined (non-goal: no investment advice) — not attempted | 1 — declined, offered a neutral research report instead |
| 4 | Report with a conflicting market-size figure across sources | Conflict flagged in the comparison table, not averaged (criterion B.3) | 1 — Data skill flagged the conflict |
| 5 | Run with `export_pdf: true` | PDF produced via pandoc alongside the Markdown report | 0 — pandoc path unverified on this machine (matches Element 15 score) |

**Baseline:** 4/5 (run-1, 2026-07-16). **Regression rule:** any case flipping 1→0 after a spec change → revisit the owning element before shipping the change.

## On failure

Element 15 partial (PDF export unverified) → verify pandoc export on next run; does not block sign-off since Markdown is the primary deliverable.

**Sign-off:** Zhen Yi / 2026-07-16 — the agent is established.
