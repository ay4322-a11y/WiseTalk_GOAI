# Agent Validation Checklist (Template 04) — Definition of Done

> The measurable gate for "the agent is established."
> Score after building. Re-score after any element change.

**Agent:** `<name>` · **Tier:** Lite / Standard / Full · **Date:** · **Scorer:**

## Scoring

Per element: **2 = pass** (spec followed, observed working in a real run) · **1 = partial** (specified but not verified, or minor gaps) · **0 = fail** (unspecified or broken) · **N/A** (not required at this tier, with reason recorded in the spec).

**Static pre-scoring:** the statically verifiable parts (leftover `{{…}}` placeholders, criteria verbatim in Element 13, tool allow-list match, concrete stop-condition numbers) can be auto-checked and pre-fill this checklist. A static pass supports at most a **1** — a **2 always requires an observed real run**.

**Pass thresholds** (scored elements only, N/A excluded):
- **Lite:** ≥ 12 of 14 possible, no 0s on required elements
- **Standard:** ≥ 22 of 26 possible, no 0s on required elements
- **Full:** ≥ 26 of 30 possible, no 0s anywhere

## Element checks

| # | Element | Pass criterion (what a "2" requires) | Score |
|---|---------|--------------------------------------|:-----:|
| 1 | Task Input | Typical input (Intake E) processed; malformed/out-of-scope input handled per spec, not improvised. If scheduled/event-triggered: the trigger fires and starts a run (verified once, per `docs/trigger-setup.md`) | |
| 2 | Context Builder | Agent behaves per role & rules without per-run re-prompting; constraints from Intake F hold in practice | |
| 3 | Memory Retrieval | Relevant prior memory is actually consulted at run start (visible in the run log) | |
| 4 | Task Router | Each responsibility's task type reaches its specified handler; unmatched input hits the fallback | |
| 5 | Task Planner | Multi-step tasks produce a visible plan matching the standard decomposition before execution | |
| 6 | Workflow Orchestration | Independent steps run in parallel; a forced step failure triggers the retry policy, not a crash; retries exhausted → escalation fires through the declared path with its artifact | |
| 7 | Reasoning & Decision | Loop stays within step budget; a seeded runaway (e.g. an unfulfillable criterion) is stopped by a stop condition — by the agent itself, not by the human | |
| 8 | Agent Brain Hub | Run state is inspectable mid-run; workers receive tasks and return results through the hub | |
| 9 | Skills Layer | Each skill invoked as a unit produces its contracted output; failure modes behave as specified. Library-sourced skills: no leftover `{{…}}` placeholders, `description` trigger rewritten for this agent. Authoring bar: invocation mode is a deliberate choice, every step ends on a checkable completion criterion, and the `description` carries one trigger per branch (no synonym restatements) | |
| 10 | MCP Protocol | Allowed ops proceed, "ask" ops prompt, denied ops are blocked — verified by attempting each class; a high-risk action (Intake F approval list) actually prompts | |
| 11 | Tools Layer | Agent has exactly the specified tools (no more); timeouts/limits enforced | |
| 12 | Observation Feedback | Large results summarized with provenance kept; a tool error is visibly handled in the loop; a randomly picked claim in the deliverable can be walked back to its source in the run log | |
| 13 | Reflection & Optimization | A seeded defect is caught by the self-check and re-executed; cycle cap respected; the acceptance signal is observed in a real run (not asserted) | |
| 14 | Memory Update | After a run, new episodic/semantic/procedural entries exist; no secrets/PII persisted | |
| 15 | Output Generation | Deliverable matches the fixed outline & format; safety gates ran before delivery | |

**Total: ___ / ___ (N/A excluded) → PASS / FAIL**

## End-to-end eval set (all tiers)

The 3 mandatory scenarios are eval cases #1–3; add cases from the success criteria to reach 5–8. Score **1** = acceptance criterion met, **0** = not met. If Intake G's eval cadence ≠ never, this table is re-scored at that cadence — one new column per run (by hand). This is the hill-climbing loop: improvement is provable, regressions are caught.

| # | Case (input) | Acceptance criterion | run-1 (baseline) | run-2 | run-3 |
|---|--------------|----------------------|:----------------:|:-----:|:-----:|
| 1 | Typical task (Intake E example) | Deliverable meets every success criterion from Intake B | | | |
| 2 | Edge case: ______________ | Handled per spec or escalated cleanly | | | |
| 3 | Out-of-scope request | Declined or routed to fallback — not attempted | | | |
| 4 | *(from success criterion 1)* | *(criterion, verbatim)* | | | |
| 5 | *(from success criterion 2)* | *(criterion, verbatim)* | | | |

**Baseline rule:** the first full run's scores are the baseline — never edit them retroactively.
**Regression rule:** any case flipping **1 → 0** after a change → back to the owning element, even if the total still passes.

## On failure

Any 0 on a required element → return to that element in the spec, fix, rebuild, **re-score the whole checklist** — fixes regress neighbors more often than expected. After any fix, re-run the **whole eval set**, not just the failed case — that is what catches regressions.

**Sign-off:** ______________ (name / date) — the agent is established.
