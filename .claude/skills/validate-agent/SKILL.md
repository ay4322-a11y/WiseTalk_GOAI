---
name: validate-agent
description: Statically pre-score a built agent package against templates/04-validation-checklist.md — leftover-placeholder scan, criteria-verbatim check, tool allow-list match, concrete stop-condition numbers, responsibility coverage. Use after /agent-builder finishes or after any spec/file change, or when asked to "validate the agent", "pre-score the checklist", or "check for leftover placeholders". Do NOT use for runtime validation (running the 3 scenarios and observing real behavior) or for scoring the eval set (that is run-evals).
---

# Validate Agent (static checks)

Input: the agent package path — the folder holding `intake-form.md`, `agent-spec.md`, `validation-checklist.md`, and the generated Claude Code files. Ask for it if not given.
Output: a check report (one row per check: PASS/FAIL with `file:line` evidence), the validation checklist pre-filled where static proof suffices, and the list of what remains manual.

## Procedure

1. **Placeholder scan** — search every generated file (agent `.md`s, skills, `CLAUDE.md`, `docs/`, `memory/`, `evals/`) for `{{`. Any hit = FAIL with the path — a leftover placeholder means an uncustomized library copy or skeleton (checklist Element 9's explicit check).
2. **Criteria verbatim** — extract the success criteria and acceptance signal from intake section B; confirm each appears **verbatim** in spec Element 13 *and* in the agent body's self-check section (spec sign-off rule).
3. **Tool allow-list match** — compare each agent's `tools:` frontmatter against the spec's Element 11 inventory (plus MCP tool names from Element 10). Extra tools or missing tools = FAIL (checklist Element 11: "exactly the specified tools, no more").
4. **Concrete stop conditions** — the agent body's `## Stop conditions` block and the spec's Element 7 step budget/no-progress rule, Element 13 cycle cap, and Element 11 caps all contain actual numbers — never "reasonable", "a few", or an unfilled field (spec sign-off rule).
5. **Coverage cross-checks** — every intake C responsibility is covered by a route/skill/tool; every spec element is filled or marked "N/A because…" (spec sign-off table).
6. **Pre-fill & report** — write the results into the package's `validation-checklist.md`: a static PASS supports at most a **1** (specified, not yet verified) — a **2 always requires an observed real run**. Report: the check table with evidence, the pre-filled rows, and the remaining manual work (run the 3 scenarios, verify the trigger fires if armed, record the eval baseline).

## Failure handling

If any of the four core package files is missing, name it and stop — don't guess which folder is the package. If the spec has no Element 11 tool table or intake B has no criteria, refuse to score the dependent checks and point to the owning template instead of scoring on assumptions.
