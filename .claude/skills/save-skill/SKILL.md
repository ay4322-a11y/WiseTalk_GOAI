---
name: save-skill
description: Save a skill into the reusable skills-library/ so future agents can copy & customize it. Use when the user wants to save, add, or promote a skill to the skills library ("save this skill", "add the SWOT skill to the library"). Do NOT use for building agents (agent-builder) or for copying a skill OUT of the library into an agent.
---

# Save Skill to Library

Input: the path to a `SKILL.md` (or skill folder) to save — ask for it if not given. Optionally which agent it came from.
Output: the skill generalized and written to `skills-library/<name>/SKILL.md`, with its line added or updated in the `skills-library/README.md` index.

## Procedure

1. **Read** the source `SKILL.md`; confirm it has the standard shape (frontmatter name/description, Input/Output, Procedure, Failure handling). If not, fix the shape as part of saving.
2. **Generalize** — find agent-specific choices (data sources, output destinations, thresholds, domain names baked into steps) and turn each back into a `{{…}}` placeholder with a short hint (e.g. `{{data sources — e.g. WebSearch, internal docs}}`). Broaden the `description` trigger from the origin agent's routing to a general "Use when… / Do NOT use for…" rule. Add or update a `## Customization points` section listing every placeholder plus anything else to adapt per agent. Add a `tags:` frontmatter line (2–4 lowercase keywords).
3. **Write** to `skills-library/<name>/SKILL.md`. If a library skill with that name already exists, show the difference and ask before overwriting (this may be an improve-back — see the library README).
4. **Index** — add or update the skill's row in the `skills-library/README.md` index table: name (linked), one-line description, tags, origin agent, today's date.
5. **Report** — show the saved path, the index line, and which parts were generalized.

## Failure handling

If the source path doesn't exist or isn't a skill file, say so and ask for the right path — don't guess among similarly named files. If the skill is so agent-specific that generalizing would hollow it out (nothing left but placeholders), say so and recommend not saving it instead of saving a useless shell.
