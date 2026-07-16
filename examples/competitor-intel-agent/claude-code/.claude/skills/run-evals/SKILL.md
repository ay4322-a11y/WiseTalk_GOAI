---
name: run-evals
description: Run and score competitor-intel-agent's eval set (evals/eval-cases.md), append the new scores as a run column, and report regressions against the previous run. Use after each spec change, at the monthly cadence, or when asked to "run the evals" or "check for regressions". Do NOT use for the one-time build validation (that is the validation checklist) or for fixing the failures it finds.
tags: evaluation, quality, loop
---

# Run Evals

> Customized from the template pack's [skills-library/run-evals](../../../../../../skills-library/run-evals/SKILL.md) for this agent (spec Element 9).

Input: `evals/eval-cases.md` and a session able to invoke `competitor-intel-agent` on each case.
Output: the eval file updated with one new score column, plus a short report: total score vs. previous run, and any regressions with the owning element to loop back to.

## Procedure

1. **Load** — read the eval table. Confirm it has a baseline column; if not, this run *is* the baseline (label the column `run-1 (baseline)`).
2. **Execute** — cases 1–4 and 6: invoke `competitor-intel-agent` on the case's input in a supervised session (case 4 requires seeding the defect into the draft before the checker phase). Case 5 requires an armed trigger — observe the next scheduled fire instead of invoking; if the trigger is not yet armed, skip it with that reason.
3. **Grade** — score each case **1** (criterion met, judged strictly against the criterion text) or **0** (not met). Grader: `competitor-intel-checker` for digest-quality criteria; human observation for routing, decline, and trigger behavior (cases 3, 5, 6). For every 0, note the one-line reason.
4. **Record** — append the scores as a new column named `run-N` (never edit earlier columns — the baseline rule). Keep the table valid markdown.
5. **Report** — total this run vs. previous run; list every **regression** (1 → 0) with its failure reason and the owning element (1–15) per the regression rule; list improvements (0 → 1). Verdict: `IMPROVED / STABLE / REGRESSED`.

## Failure handling

If a case cannot be executed (missing input, tool unavailable, trigger unarmed), score it `–` (skipped) with the reason — never guess a score. If more than 2 cases are skipped, stop and report the eval set as unrunnable instead of delivering a misleading total. If the eval file has no acceptance criteria, refuse to grade and point to the eval-cases skeleton in templates/03.
