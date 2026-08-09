# Agent Validation Checklist — wisetalk-router-agent

**Agent:** `wisetalk-router-agent` · **Tier:** Standard · **Date:** 2026-08-09 · **Scorer:** template pack / manual static + behavioral run

## Scoring

Per element: **2 = pass** (spec followed, observed working in a real run) · **1 = partial** (specified but not verified, or minor gaps) · **0 = fail** (unspecified or broken) · **N/A** (not required at this tier, with reason recorded in the spec).

**Evidence:** static checks (placeholders, criteria verbatim, tool allow-list, concrete stop conditions) + a behavioral validation run on 2026-08-09 executing all 6 eval cases end-to-end (real JSON packets delivered, 7-item self-check run per case, memory appended after each turn).

**Pass thresholds (scored elements only):** Standard ≥ 22 of 26 possible, no 0s on required elements.

## Element checks

| # | Element | Pass criterion (what a "2" requires) | Score |
|---|---------|--------------------------------------|:-----:|
| 1 | Task Input | Typical input (Intake E) processed; malformed/out-of-scope input handled per spec, not improvised | 2 |
| 2 | Context Builder | Agent behaves per role & rules without per-run re-prompting; constraints from Intake F hold in practice | 2 |
| 3 | Memory Retrieval | Relevant prior memory is actually consulted at run start (visible in the run log) | 2 |
| 4 | Task Router | Each responsibility's task type reaches its specified handler; unmatched input hits the fallback | 2 |
| 5 | Task Planner | Multi-step tasks produce a visible plan matching the standard decomposition before execution | 2 |
| 6 | Workflow Orchestration | — | N/A (single-turn, single-path pipeline — spec Element 6) |
| 7 | Reasoning & Decision | Loop stays within step budget; a seeded runaway is stopped by a stop condition — by the agent itself | 1 |
| 8 | Agent Brain Hub | Run state is inspectable mid-run; workers receive tasks and return results through the hub | 2 |
| 9 | Skills Layer | Each skill invoked as a unit produces its contracted output; failure modes behave as specified | 2 |
| 10 | MCP Protocol | — | N/A (no MCP servers — spec Element 10) |
| 11 | Tools Layer | Agent has exactly the specified tools (no more); timeouts/limits enforced | 2 |
| 12 | Observation Feedback | Large results summarized with provenance kept; a tool error is visibly handled in the loop; a claim can be walked back to its source | 1 |
| 13 | Reflection & Optimization | A seeded defect is caught by the self-check and re-executed; cycle cap respected; the acceptance signal is observed in a real run | 2 |
| 14 | Memory Update | After a run, new episodic/semantic/procedural entries exist; no secrets/PII persisted | 2 |
| 15 | Output Generation | Deliverable matches the fixed outline & format; safety gates ran before delivery | 2 |

**Total: 24 / 26 (N/A excluded) → PASS**

*Rows scored 1 (Element 7, 12): the stop-condition and tool-error paths were not adversarially seeded in this run — follow-up tests are to force an unclassifiable input and a missing routing map.*

## End-to-end eval set

| # | Case (input) | Acceptance criterion | run-1 (baseline) |
|---|--------------|----------------------|:----------------:|
| 1 | "My boss rejected my budget proposal because he thinks it's too high. How can I convince him?" | Routes to **Agent 6 (RIDE)**, `use_case = Salary_Negotiation`, confidence ≥ 0.6, valid 7-field JSON packet | ✅ 1 |
| 2 | "I have a job interview tomorrow. Help me prepare." | Routes to **Agent 1 (STAR)**, `use_case = Job_Interview`, confidence ≥ 0.6, valid packet | ✅ 1 |
| 3 | "Tell me a joke." | Routed to **GENERAL_CHAT** fallback — not forced into any Expert Agent | ✅ 1 |
| 4 | "Help me write an email." | Generic-default rule: routes to **Agent 2 (SCRTV)**, `use_case = General_Communication` | ✅ 1 |
| 5 | "I need to tell my team something." (ambiguous) | Handled per spec: Agent 2 (SCRTV) generic default **or** GENERAL_CHAT — no invented category | ✅ 1 |
| 6 | Second turn: "Now make it more persuasive." | `chat_history_string` contains the prior round; routes consistently with prior context | ✅ 1 |

**Baseline rule:** the first full run's scores are the baseline — never edit them retroactively.
**Regression rule:** any case flipping **1 → 0** after a change → back to the owning element, even if the total still passes.

## On failure

Any 0 on a required element → return to that element in the spec, fix, rebuild, **re-score the whole checklist**. After any fix, re-run the **whole eval set**, not just the failed case.

**Sign-off:** ______________ (name / date) — the agent is established.
