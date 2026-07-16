# Skills Library

A growing, user-owned catalog of pre-built skills. When building a new agent, **reuse from here first** (copy & customize); write a skill from scratch (the skeleton in [templates/03-claude-code-mapping.md](../templates/03-claude-code-mapping.md#skill-skeleton-claudeskillsskill-nameskillmd--element-9)) only when nothing here matches. Unlike `templates/` and `reference/`, this folder is **meant to be written to** — every agent you build can leave reusable skills behind.

## Index

This table is the matching surface: `/agent-builder` matches each Element 9 skill against it (name / description / tags) — it never scans skill folders. Keep one line per skill, current.

| Skill | Description | Tags | Origin agent | Saved |
|-------|-------------|------|--------------|-------|
| [swot-analysis](swot-analysis/SKILL.md) | Evidence-grounded SWOT (4-quadrant) analysis of a company, product, or initiative | analysis, strategy, business | (template pack seed) | 2026-07-16 |
| [market-expansion-analysis](market-expansion-analysis/SKILL.md) | Assess a target market for expansion: sizing, competitors, entry barriers, go/no-go | analysis, market, strategy | (template pack seed) | 2026-07-16 |
| [run-evals](run-evals/SKILL.md) | Run and score an agent's eval set, append a run column, report regressions (the hill-climbing loop) | evaluation, quality, loop | (template pack seed) | 2026-07-16 |

## Workflows

### Reuse (library → new agent)

1. Match the needed Element 9 skill against the index above.
2. Copy `skills-library/<name>/` → the target project's `.claude/skills/<name>/`.
3. Customize everything listed under the skill's `## Customization points`: rewrite the `description` trigger for the new agent, replace every `{{…}}` placeholder (data sources, output destination, domain specifics), adjust procedure steps and failure handling to the agent's spec.
4. Verify **no `{{…}}` placeholders remain** — the validation checklist checks this.

### Save-back (new agent → library)

Run `/save-skill <path-to-SKILL.md>` — it generalizes agent-specific parts back into `{{…}}` placeholders, writes the skill here, and adds/updates its index line. (Manual equivalent: generalize, copy the folder in, add the index line yourself.)

Save a skill when it wraps a procedure another agent could plausibly need (domain analyses, recurring report formats, data pipelines). Don't save skills that only make sense inside one agent.

### Improve-back (customized copy → library)

If you significantly improve a copied skill inside an agent (better procedure, better failure handling), port the improvement back to the library version so the library doesn't go stale. Git history covers versioning — no version numbers in files.

## Library skill format

Same skeleton as any skill (frontmatter `name` + `description` written as a trigger rule, optional `tags`, Input/Output, `## Procedure`, `## Failure handling`), **plus** a `## Customization points` section listing exactly what to adapt per agent. Skills are complete and usable as-is except at their `{{…}}` marks.
