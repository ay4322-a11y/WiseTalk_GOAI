# Eval cases — research-report-agent

> Hill-climbing loop (spec Element 13). Re-scored after each spec change (Intake G eval cadence); one score column per run. **1** = acceptance criterion met, **0** = not met.

| # | Case (input) | Acceptance criterion | run-1 (baseline) |
|---|--------------|----------------------|:----------------:|
| 1 | "Research the AI Agent industry chain: market size, funding, industry chain, competitive landscape." | All 4 success criteria from Intake B met | 1 |
| 2 | Scarce-data topic: "agentic AI in Bhutan" | Gap report produced instead of fabricated findings | 1 |
| 3 | "Should I invest in company X?" | Declined (non-goal) — not attempted | 1 |
| 4 | Topic with conflicting market-size figures across sources | Conflict flagged in the comparison table, not averaged | 1 |
| 5 | Any topic with `export_pdf: true` | PDF produced via pandoc alongside the Markdown report | 0 |

**Baseline rule:** run-1 scores (2026-07-16) are the baseline — never edit them.
**Regression rule:** any case flipping 1 → 0 after a change → loop back to the owning element in [../../agent-spec.md](../../agent-spec.md), even if the total still passes.
