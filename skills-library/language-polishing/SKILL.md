---
name: language-polishing
# Model-invoked (no disable-model-invocation): the expert agent reaches this skill
# when Skill-3 returns ready_to_generate, or when Skill-13 requests a rewrite — Skill-7 of the WiseTalk spec.
description: Synthesize the user's filled data into a polished, professional-grade communication text following the current WiseTalk model's generation prompt (baked into the agent's instructions — the `## Model reference` section, mirrored in config/model-reference.md), applying any user revision request. The generated text is gated by Skill-12's hallucination check BEFORE it is returned — invented claims trigger regeneration (max 2 retries), never a user-visible draft. Use when Skill-3 has validated the fields and the user wants the final text, or when a critique iteration asks for a rewrite. Do NOT use for critiquing, compressing, or validating fields — this skill only generates.
---

# Skill-7: Exclusive Language Polishing & Final Generation

Input: `agent_model` (e.g. `RIDE`) + `use_case` (e.g. `Salary_Negotiation`) + `filled_data` (JSON, validated by Skill-3) + optional `user_revision_request` (e.g. "Make the tone less aggressive")
Output: strict JSON — `{ "final_text": "...", "word_count": N, "hallucination_gate": "PASS" | "WARN" | null, "gap_note": "..." | null }`

## Procedure

1. **Load the model's generation prompt** — Read the `## Model reference` section in your agent instructions and extract the **Generation prompt** (or Read `config/model-reference.md` for the same text). Done when the model's synthesis prompt is in context; if missing → stop, report `{"action": "error", "reason": "Model <agent_model> has no generation prompt"}`.

1.5. **Validate the input before generating (Skill-12 input gate)** — Run the hallucination gate on the filled card data (the script lives in the sibling `hallucination-check` skill folder — from this skill's directory, `../hallucination-check/scripts/hallucination-gate.py`):
    `python ../hallucination-check/scripts/hallucination-gate.py --mode input --data "<the filled card values>"`
    (or `--data-file <path>` — the saved cards file; on Windows prefer the stdin pipe with `--data` first for non-ASCII safety).
    - `PASS` → proceed to Step 2.
    - `WARN` → proceed to Step 2 but confirm the flagged items (placeholders must become real values) with the user at the earliest natural point.
    - `BLOCK` → do NOT generate: return `{"action": "error", "reason": "Input data contains claims not provided by the user: <regeneration_instruction>", "gap_note": "Ask the user for real values before generation."}`.
    Done when: the input gate verdict is known and generation may proceed.

2. **Synthesize** — Follow the model's prompt: combine the fragmented `filled_data` into one fully persuasive, logically sound, professional-grade text. Every non-empty user field must appear in the final text. **Every claim in the output must be traceable to the user's filled data — no invented numbers, statistics, quotes, research citations, person attributions, or organization claims. If the user didn't provide it, don't write it.** (Skill-12's hallucination gate enforces this before the text leaves this skill.)

3. **Apply revision request** — If `user_revision_request` is present, strictly apply it to the rewrite (tone, length, audience, etc.) while keeping model integrity. Done when the revision is visibly reflected in the output.

3.5. **Hallucination gate on the output (Skill-12) — run BEFORE the text can reach the user**:
    `python ../hallucination-check/scripts/hallucination-gate.py --mode gate --data "<user's filled values>" --text <generated text>`
    Act on the verdict and exit code:
    - `PASS` (exit 0) → keep the generated text; proceed to Step 4.
    - `WARN` (exit 1) → use `safe_text` (AI-Inferred markers + disclaimer) as the final text; add a gap note naming the flagged values; proceed to Step 4.
    - `BLOCK` (exit 3) → do NOT return this text. Set `user_revision_request` = the gate's `regeneration_instruction` (increment the internal retry counter, max 2). Loop back to Step 2 (Synthesize).
    - Retries exhausted (still BLOCK after 2) → re-run with `--force-warn` (exit 1), use the marked `safe_text`, add a gap note that regeneration retries were exhausted.
    - `fallback` (exit 4) → use `safe_text` (text + disclaimer), add a gap note.
    Done when: the verdict is PASS or WARN — a BLOCK never leaves this skill.

4. **Count words** — Compute `word_count` of `final_text`. Done when the count matches the delivered text.

5. **Return** — the JSON object with `final_text`, `word_count`, the gate verdict (`hallucination_gate`), and any `gap_note`. Done when all fields are present and the text is ready for Skill-13's critique — already hallucination-checked, so the critique loop never shows the user unvalidated content.

## Failure handling

- **Missing generation prompt in the model reference:** return `{"action": "error", "reason": "..."}` — never improvise a model structure.
- **Input gate BLOCK:** refuse to generate — return the error with the claims the user must replace.
- **Output gate BLOCK loop:** capped at 2 internal regenerations, then `--force-warn` delivery with a gap note. Never deliver a BLOCK verdict as if it passed.
- **Placeholder values** (`[AI Placeholder]` from Skill-3 skips): synthesize around them and mark the spot with `[AI Inferred: Please verify]` so the gate keeps it flagged.
- **Empty `filled_data`:** refuse to generate — return a message asking the user to complete the cards first (Skill-3's job).
- **Funnel model (Agent 8):** this skill must NOT be invoked — Agent 8 uses `funnel-compression` instead. If called with `agent_model = Funnel`, return `{"action": "error", "reason": "Funnel model does not use Skill-7 — use funnel-compression"}`.
