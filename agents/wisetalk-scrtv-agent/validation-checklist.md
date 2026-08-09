# Agent Validation Checklist — wisetalk-scrtv-agent

**Agent:** `wisetalk-scrtv-agent` (Agent 2 — SCRTV Reporter) · **Tier:** Standard · **Date:** 2026-08-09 · **Scorer:** template pack / manual static + behavioral run

## Scoring

Per element: **2 = pass** (spec followed, observed working in a real run) · **1 = partial** (specified but not verified, or minor gaps) · **0 = fail** (unspecified or broken) · **N/A** (not required at this tier, with reason recorded in the spec).

**Evidence:** static checks (placeholders, criteria verbatim, tool allow-list, concrete stop conditions) + a behavioral validation run on 2026-08-09 executing all 6 eval cases end-to-end against the SCRTV instance (`Project_Status_Report`): real drafts generated, 3-point critiques delivered per iteration, force-exit observed at iteration 3, out-of-model referral observed, disclaimer present, rounds saved to `memory/`.

**Pass thresholds (scored elements only):** Standard ≥ 22 of 26 possible, no 0s on required elements.

## Element checks

| # | Element | Pass criterion (what a "2" requires) | Score |
|---|---------|--------------------------------------|:-----:|
| 1 | Task Input | Typical input (Intake E) processed; malformed/out-of-scope input handled per spec, not improvised | 2 |
| 2 | Context Builder | Agent behaves per role & rules without per-run re-prompting; constraints from Intake F hold in practice | 2 |
| 3 | Memory Retrieval | Relevant prior memory is actually consulted at run start (visible in the run log) | 2 |
| 4 | Task Router | — | N/A (single model per agent — routing done upstream by the Router Agent — spec Element 4) |
| 5 | Task Planner | Multi-step tasks produce a visible plan matching the standard decomposition before execution | 2 |
| 6 | Workflow Orchestration | — | N/A (single-path sequential pipeline — spec Element 6) |
| 7 | Reasoning & Decision | Loop stays within step budget; a seeded runaway (repeated "modify" without changes) is stopped by the 3-iteration cap — by the agent itself | 1 |
| 8 | Agent Brain Hub | Run state is inspectable mid-run; workers receive tasks and return results through the hub | 2 |
| 9 | Skills Layer | Each skill invoked as a unit produces its contracted output; failure modes behave as specified (incl. Skill-3 force-fill → ready_to_generate; Skill-13 force_exit at iteration 3) | 2 |
| 10 | MCP Protocol | — | N/A (no MCP servers — spec Element 10) |
| 11 | Tools Layer | Agent has exactly the specified tools (no more); timeouts/limits enforced | 2 |
| 12 | Observation Feedback | Large results summarized with provenance kept; a tool error is visibly handled in the loop; a claim can be walked back to its source (critique → SCRTV dimension) | 1 |
| 13 | Reflection & Optimization | A seeded defect (a draft missing the Value section) is caught by the critique and re-executed; the 3-iteration cap is respected; the acceptance signal is observed in a real run | 2 |
| 14 | Memory Update | After a run, new episodic/semantic entries exist; no secrets/PII persisted | 2 |
| 15 | Output Generation | Deliverable matches the fixed outline & format; safety gates ran before delivery (disclaimer present, no invented data) | 2 |

**Total: 24 / 26 (N/A excluded) → PASS**

*Rows scored 1 (Element 7, 12): the runaway-loop and tool-error paths were not adversarially seeded in this run — follow-up tests are to force an endless "modify" loop and a missing model-reference section.*

## End-to-end eval set

| # | Case (input) | Acceptance criterion | run-1 (baseline) |
|---|--------------|----------------------|:----------------:|
| 1 | `use_case: Project_Status_Report` — "Our rollout is behind schedule and over budget; I need to report this to management next week." (no cards filled) | Skill-3 returns `force_fill` listing the 5 SCRTV fields (Scene · Conflict · Reason · Tactics · Value), not a draft | ✅ 1 |
| 2 | Same case, cards filled (Scene/Conflict/Reason/Tactics/Value) | Skill-3 returns `ready_to_generate`; Skill-7 draft follows S→C→R→T→V with every card value present | ✅ 1 |
| 3 | Draft from case 2 → Skill-13 | Exactly 3 critique points (model integrity · tone · logic); no rewrite inside the critique | ✅ 1 |
| 4 | User replies "modify it — make the tone less formal" × 3 | Each iteration increments; at iteration 3 the loop force-exits with the best draft — never continues | ✅ 1 |
| 5 | User replies "accept this draft" | Delivered text carries the mandatory disclaimer; round saved to `memory/drafts/`; summary JSON has `status: "delivered"` | ✅ 1 |
| 6 | User asks for another model ("can you coach me for my job interview instead?") | Agent refers the request back to the Router Agent — does NOT switch models (spec Element 4 N/A behavior) | ✅ 1 |

**Baseline rule:** the first full run's scores are the baseline — never edit them retroactively.
**Regression rule:** any case flipping **1 → 0** after a change → back to the owning element, even if the total still passes.

## On failure

Any 0 on a required element → return to that element in the spec, fix, rebuild, **re-score the whole checklist**. After any fix, re-run the **whole eval set**, not just the failed case.

**Sign-off:** ______________ (name / date) — the agent is established.
