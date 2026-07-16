# Eval cases — competitor-intel-agent

> Hill-climbing loop (spec Element 13) — **required** at Full tier. Re-scored after each spec change and monthly (Intake G cadence) via the customized [run-evals skill](../.claude/skills/run-evals/SKILL.md); one score column per run. **1** = acceptance criterion met, **0** = not met.

| # | Case (input) | Acceptance criterion | run-1 (baseline) |
|---|--------------|----------------------|:----------------:|
| 1 | Typical weekly run on the 3-competitor example list | Digest meets all 4 success criteria from Intake B; checker PASS in the run log | 1 |
| 2 | A competitor with no findings this week | Explicit "no change this week" line — nothing fabricated | 1 |
| 3 | Out-of-scope: "Should we undercut Acme's pricing?" | Declined (non-goal: no strategy advice) — not attempted | 1 |
| 4 | Seeded defect: citation stripped from one draft claim | Checker FAILs naming the criterion; only that section re-executed; PASS within 2 cycles | 1 |
| 5 | Trigger fires while a run is in progress | Second fire skipped per the dedup rule, noted in `memory/state.md` | 0 — needs an armed trigger (`docs/trigger-setup.md`); score after the first scheduled week |
| 6 | Ad-hoc: "What changed for Acme Agents?" | Routed to the mini-run; cited brief for that competitor only, in chat | 1 |

**Baseline rule:** run-1 scores (2026-07-16) are the baseline — never edit them.
**Regression rule:** any case flipping 1 → 0 after a change → loop back to the owning element in [../agent-spec.md](../../agent-spec.md), even if the total still passes.
