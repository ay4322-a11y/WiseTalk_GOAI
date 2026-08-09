---
name: mandatory-fill-in
# Model-invoked (no disable-model-invocation): the expert agent reaches this skill
# when the user enters the agent, or hits "Generate" with empty fields — Skill-3 of the WiseTalk spec.
description: Validate that the user has completed all mandatory fill-in cards for the current WiseTalk communication model (the fields are baked into the agent's instructions — the `## Model reference` section, mirrored in config/model-reference.md), asking for each missing field via force_fill. Use at the start of every generation request, and when the user clicks Generate with empty fields. Do NOT use for generating text, critiquing, or compressing — this skill only gates generation on complete input.
---

# Skill-3: Exclusive Structured Mandatory Fill-in Guidance

Input: `agent_model` (e.g. `RIDE`) + `use_case` (e.g. `Salary_Negotiation`) + `filled_data` (JSON object of the user's card values)
Output: strict JSON — `{ "action": "force_fill", "missing_fields": [...], "question": "..." }` **or** `{ "action": "ready_to_generate" }`

## Procedure

1. **Load the model's fill-in fields** — Read the `## Model reference` section in your agent instructions and extract the **Fill-in fields** table (or Read `config/model-reference.md` for the same table). Done when the field list and its guiding questions are in context; if the section is missing → stop, report `{"action": "error", "reason": "No fill-in fields defined for model <agent_model>"}`.
2. **Check completeness** — For each field in the table, check whether the corresponding key in `filled_data` is non-empty (non-whitespace). Done when every field has a pass/fail verdict.
3. **If any field is missing** — return `force_fill` naming exactly the missing fields and the guiding question from the model reference (tailored to the current `use_case`):

   ```json
   { "action": "force_fill", "missing_fields": ["Interest"], "question": "In this salary negotiation context, what specific value do you provide to the company?" }
   ```

   Done when every missing field has a targeted question; do not proceed to generation.
4. **If all fields are non-empty** — return `{ "action": "ready_to_generate", "message": "Validation passed" }`. Done when the caller can hand off to Skill-7.
5. **Skip counter** — track how many times the user declined/emptied a forced-fill question. After the **3rd skip**, accept `[AI Placeholder]` for the remaining empty fields and return `ready_to_generate` with a note listing the placeholder fields. Done when the skip count reaches 3 and the user still hasn't filled the field.

## Failure handling

- **Missing model reference section:** return `{"action": "error", "reason": "..."}` — never invent fields for an unknown model.
- **Unparseable `filled_data`:** ask the user to resubmit their card values as plain text; do not guess values.
- **User repeatedly skips:** after 3 skips, `[AI Placeholder]` passes validation per the WiseTalk spec — generation proceeds, and Skill-12 later flags any AI-inferred content.
- **Funnel model (Agent 8):** the model reference lists a single field (`OriginalText`). Validate it the same way; when complete, hand off to `funnel-compression` (Skill-5) — never to Skill-7.
