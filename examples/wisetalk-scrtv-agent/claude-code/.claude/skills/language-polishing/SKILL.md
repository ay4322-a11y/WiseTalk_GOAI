---
name: language-polishing
# Model-invoked (no disable-model-invocation): the expert agent reaches this skill
# when Skill-3 returns ready_to_generate, or when Skill-13 requests a rewrite — Skill-7 of the WiseTalk spec.
description: Synthesize the user's filled data into a polished, professional-grade communication text following the current WiseTalk model's generation prompt (baked into the agent's instructions — the `## Model reference` section, mirrored in config/model-reference.md), applying any user revision request. Use when Skill-3 has validated the fields and the user wants the final text, or when a critique iteration asks for a rewrite. Do NOT use for critiquing, compressing, or validating fields — this skill only generates.
---

# Skill-7: Exclusive Language Polishing & Final Generation

Input: `agent_model` (e.g. `RIDE`) + `use_case` (e.g. `Salary_Negotiation`) + `filled_data` (JSON, validated by Skill-3) + optional `user_revision_request` (e.g. "Make the tone less aggressive")
Output: strict JSON — `{ "final_text": "...", "word_count": N }`

## Procedure

1. **Load the model's generation prompt** — Read the `## Model reference` section in your agent instructions and extract the **Generation prompt** (or Read `config/model-reference.md` for the same text). Done when the model's synthesis prompt is in context; if missing → stop, report `{"action": "error", "reason": "Model <agent_model> has no generation prompt"}`.
2. **Synthesize** — Follow the model's prompt: combine the fragmented `filled_data` into one fully persuasive, logically sound, professional-grade text. Every non-empty user field must appear in the final text — no invented numbers, quotes, or facts (see Skill-12's hallucination check on the way out).
3. **Apply revision request** — If `user_revision_request` is present, strictly apply it to the rewrite (tone, length, audience, etc.) while keeping model integrity. Done when the revision is visibly reflected in the output.
4. **Count words** — Compute `word_count` of `final_text`. Done when the count matches the delivered text.
5. **Return** — the JSON object with `final_text` and `word_count`. Done when both fields are present and the text is ready for Skill-13's critique.

## Failure handling

- **Missing generation prompt in the model reference:** return `{"action": "error", "reason": "..."}` — never improvise a model structure.
- **Placeholder values** (`[AI Placeholder]` from Skill-3 skips): synthesize around them and mark the spot with `[AI Inferred: Please verify]` so Skill-12's hallucination check can keep it flagged.
- **Empty `filled_data`:** refuse to generate — return a message asking the user to complete the cards first (Skill-3's job).
- **Funnel model (Agent 8):** this skill must NOT be invoked — Agent 8 uses `funnel-compression` instead. If called with `agent_model = Funnel`, return `{"action": "error", "reason": "Funnel model does not use Skill-7 — use funnel-compression"}`.
