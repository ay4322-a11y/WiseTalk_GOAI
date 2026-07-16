---
name: validate-agent
description: Statically pre-score a built agent package against templates/04-validation-checklist.md — leftover-placeholder scan, criteria-verbatim check, tool allow-list match, concrete stop-condition numbers, responsibility coverage. Use after /agent-builder finishes or after any spec/file change, or when asked to "validate the agent", "pre-score the checklist", or "check for leftover placeholders". Do NOT use for runtime validation (running the 3 scenarios and observing real behavior) or for scoring the eval set (that is run-evals).
---

# Validate Agent (static checks)

Input: the agent package path — the folder holding `intake-form.md`, `agent-spec.md`, `validation-checklist.md`, and the generated Claude Code files. Ask for it if not given.
Output: a check report (one row per check: PASS/FAIL with `file:line` evidence), the validation checklist pre-filled where static proof suffices, and the list of what remains manual.

## Procedure

Run the commands as written (from the package root; `<cc>` = the generated `claude-code/` tree) — the checks are deterministic, not re-derived per run.

1. **Placeholder scan** — a leftover placeholder means an uncustomized library copy or skeleton (checklist Element 9's explicit check). The literal `{{…}}` (ellipsis) is allowed — it's how docs *mention* placeholders.
   `grep -rn '{{' <cc> | grep -v '{{…}}'` → any output = FAIL with the path.
2. **Criteria verbatim** — extract each success criterion and the acceptance signal from intake section B, then for each:
   `grep -Fc "<criterion text>" agent-spec.md <cc>/.claude/agents/<agent-name>.md` → count must be ≥1 in the spec (Element 13) **and** ≥1 in the agent body's self-check; 0 anywhere = FAIL (spec sign-off rule). If a checker agent exists, also require ≥1 in its grading procedure.
3. **Tool allow-list match** — list what each agent actually holds:
   `grep -H '^tools:' <cc>/.claude/agents/*.md` → compare each line against the spec's Element 11 inventory (plus MCP tool names from Element 10). Extra tools or missing tools = FAIL (checklist Element 11: "exactly the specified tools, no more").
4. **Concrete stop conditions** — surface every stop-condition line:
   `grep -n -A5 '^## Stop conditions' <cc>/.claude/agents/*.md` and `grep -nE 'budget|no.progress|cycle|cap' agent-spec.md` → every budget/cap must contain an actual number; the words "reasonable", "a few", "several", or an unfilled field = FAIL (spec sign-off rule). Quick screen: `grep -rniE 'max (a few|several|reasonable)' <cc> agent-spec.md` must return nothing.
5. **Coverage cross-checks** — every intake C responsibility ID (R1…Rn) is covered by a route/skill/tool: check the spec's sign-off table and Element 4 routing rows against intake C; every spec element is filled or marked "N/A because…" (`grep -c 'N/A because' agent-spec.md` should equal the number of skipped elements for the tier).
6. **Pre-fill & report** — write the results into the package's `validation-checklist.md`: a static PASS supports at most a **1** (specified, not yet verified) — a **2 always requires an observed real run**. Report: the check table with evidence, the pre-filled rows, and the remaining manual work (run the 3 scenarios, verify the trigger fires if armed, record the eval baseline).

## Failure handling

If any of the four core package files is missing, name it and stop — don't guess which folder is the package. If the spec has no Element 11 tool table or intake B has no criteria, refuse to score the dependent checks and point to the owning template instead of scoring on assumptions.
