---
name: run-evals
description: Run and score an agent's eval set (evals/eval-cases.md), append the new scores as a run column, and report regressions against the previous run. Use at the agent's eval cadence, after any spec/element change, or when asked to "run the evals", "score the eval set", or "check for regressions". Do NOT use for the one-time build validation (that is the full 04-validation-checklist) or for fixing the failures it finds.
tags: evaluation, quality, loop
---

# Run Evals

Input: the path to the agent's eval file ({{eval file location — e.g. `evals/eval-cases.md`}}) and, if grading needs it, access to run the agent on each case.
Output: the eval file updated with one new score column, plus a short report: total score vs. previous run, and any regressions with the owning element to loop back to.

## Procedure

1. **Load** — read the eval table. Confirm it has a baseline column; if not, this run *is* the baseline (label the column `run-1 (baseline)`).
2. **Execute** — for each case, run the agent on the case's input {{execution method — e.g. invoke the agent on the input, or replay against the latest real run's artifacts}}. Capture the deliverable and run log per case.
3. **Grade** — score each case **1** (acceptance criterion met, judged strictly against the criterion text) or **0** (not met). Grader: {{self-grade / the agent's checker sub-agent / human review}}. For every 0, note the one-line reason.
4. **Record** — append the scores as a new column named `run-N` (never edit earlier columns — the baseline rule). Keep the table valid markdown.
5. **Report** — total this run vs. previous run; list every **regression** (case flipping 1 → 0) with its failure reason and the owning element (1–15) to revisit per the regression rule; list improvements (0 → 1). Verdict: `IMPROVED / STABLE / REGRESSED`.

## Failure handling

If a case cannot be executed (missing input, tool unavailable), score it `–` (skipped) with the reason — never guess a score. If more than {{K, e.g. 2}} cases are skipped, stop and report the eval set as unrunnable instead of delivering a misleading total. If the eval file has no acceptance criteria (empty rows), refuse to grade and point to the eval-cases skeleton in templates/03.

## Customization points

- `description` trigger — rewrite for the owning agent's routing ("Use when…; do NOT use for…").
- Step 1 `{{eval file location}}` — the agent's actual eval path.
- Step 2 `{{execution method}}` — how a case is actually run for this agent (live invocation vs. replay).
- Step 3 grader — match the agent's Element 13 checker field (self / checker sub-agent / human).
- Failure threshold `{{K}}` — how many skips invalidate a run.
