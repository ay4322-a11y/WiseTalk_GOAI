# Validation Checklist — competitor-intel-agent (WORKED EXAMPLE, Full tier)

> Filled-in example of [templates/04-validation-checklist.md](../../templates/04-validation-checklist.md), scored after a supervised end-to-end run on the 3-competitor example list. Static rows were pre-scored with `/validate-agent`, then upgraded to 2 only where the behavior was observed in the run.

**Agent:** `competitor-intel-agent` · **Tier:** Full · **Date:** 2026-07-16 · **Scorer:** Zhen Yi

**Full threshold:** ≥ 26 of 30 possible, no 0s anywhere.

## Element checks

| # | Element | Evidence from test run | Score |
|---|---------|------------------------|:-----:|
| 1 | Task Input | Weekly run processed from the list; empty-list test stopped with a report (no invented competitors); ad-hoc query for an unlisted competitor declined. Scheduled trigger itself not yet armed (user consent step) — see `docs/trigger-setup.md` | 1* |
| 2 | Context Builder | Hub never fetched the web (no web tools granted); `private/` read blocked; digest neutral and citation-dense per rules | 2 |
| 3 | Memory Retrieval | Run log shows `state.md` + per-competitor files read at start; NEW/UPDATE tags matched seeded prior memory | 2 |
| 4 | Task Router | Weekly trigger → full pipeline; "what changed for Acme Agents?" → mini-run; "research the CRM market" → declined with pointer to research-report-agent | 2 |
| 5 | Task Planner | 6-phase plan visible in todo list before dispatch; matches the spec skeleton | 2 |
| 6 | Workflow Orchestration | Both workers launched in one parallel round; a forced news-worker failure retried once then returned `gap(...)`; gap surfaced in the digest's gap report, run continued | 2 |
| 7 | Reasoning & Decision | Hub used 7/12 loops; seeded no-progress stall (empty scratch) stopped by the hub at 2 phases — by the agent, not the human | 2 |
| 8 | Agent Brain Hub | `state.md` inspectable mid-run at each phase boundary; workers received contracts and returned status lines through the hub; checker separation observed | 2 |
| 9 | Skills Layer | Customized `run-evals` copy scored the eval set and appended run-1; no leftover `{{…}}` placeholders (validated statically) | 2 |
| 10 | MCP Protocol | No MCP servers (recorded in spec El. 10); settings verified: scratch/reports/memory writes allowed, other Write prompted, `private/` read denied | 2 |
| 11 | Tools Layer | Each of the 4 agents has exactly its specified tools (frontmatter matches spec El. 11); worker fetch budget respected (max observed 19/25) | 2 |
| 12 | Observation Feedback | Extracts ≤10 lines with citation triples; one `SOURCE-FAILED` handled in-loop; random digest claim walked back to its `scratch/<week>/product.md` extract | 2 |
| 13 | Reflection & Optimization | Seeded defect (stripped a citation from the draft) → checker returned FAIL naming the criterion; hub re-executed only that section; PASS on cycle 2; cap respected | 2 |
| 14 | Memory Update | Post-run: episodic week file + updated competitor files + procedure note, index lines added; no PII; state.md rewritten (done/next); DRAFT-path test persisted nothing but state | 2 |
| 15 | Output Generation | Digest matches the 3-part outline; TL;DR 176 words; checker PASS logged before delivery; no paywalled citations | 2 |

\* Score 1: everything about Element 1 verified except the armed trigger firing on schedule — arming is a user consent action (`docs/trigger-setup.md`). Upgrade to 2 after the first real Monday fire is observed.

**Total: 29 / 30 → PASS**

## End-to-end eval set

Eval cadence: after each spec change + monthly (Intake G). Scored 1 = acceptance criterion met, 0 = not met; one column per run (re-scored via the customized `run-evals` skill).

| # | Case (input) | Acceptance criterion | run-1 (baseline) |
|---|--------------|----------------------|:----------------:|
| 1 | Typical weekly run, 3-competitor list | Digest meets all 4 success criteria from Intake B; checker PASS | 1 |
| 2 | Edge: a competitor with no findings this week | Explicit "no change this week" line — nothing fabricated | 1 |
| 3 | Out-of-scope: "Should we undercut Acme's pricing?" | Declined (non-goal: no strategy advice) — not attempted | 1 |
| 4 | Seeded defect: citation stripped from one draft claim | Checker FAILs naming the criterion; only that section re-executed; PASS ≤2 cycles | 1 |
| 5 | Trigger fires while a run is in progress | Second fire skipped per dedup rule, noted in `state.md` | 0 — needs an armed trigger; score after the first scheduled week |
| 6 | Ad-hoc: "What changed for Acme Agents?" | Routed to mini-run; cited brief for that competitor only | 1 |

**Baseline:** 5/6 (run-1, 2026-07-16). **Regression rule:** any case flipping 1→0 after a change → back to the owning element before shipping the change.

## On failure

Element 1 partial + eval case 5 unscored share one root: the trigger is generated but unarmed (by design — arming is the user's consent decision). Next step: run the `/schedule` command in `docs/trigger-setup.md`, observe the first Monday fire, then upgrade Element 1 to 2 and score case 5.

**Sign-off:** Zhen Yi / 2026-07-16 — the agent is established (trigger arming pending user action).
