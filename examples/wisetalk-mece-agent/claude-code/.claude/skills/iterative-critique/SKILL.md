---
name: iterative-critique
# Model-invoked (no disable-model-invocation): the expert agent reaches this skill
# immediately after Skill-7 outputs the first draft — Skill-13 of the WiseTalk spec.
description: Critique a drafted communication text against the current WiseTalk model's critique dimensions (baked into the agent's instructions — the `## Model reference` section, mirrored in config/model-reference.md) — model integrity, tone & audience fit, logic & persuasion gaps — returning exactly 3 actionable points and an accept/modify question. Use after every language-polishing output, until the 3-iteration cap force-exits. Do NOT use for generating or rewriting text — this skill only critiques; rewrites go back to language-polishing.
---

# Skill-13: Iterative Critique & Revision Loop (The Coaching Brain)

Input: `draft_text` (the Skill-7 output) + `use_case` (e.g. `Salary_Negotiation`) + `iteration_count` (1-based) + `max_iterations` (default 3) + optional `user_revision_request`
Output: strict JSON — `{ "action": "display_critique", "iteration": N, "critique_points": [...exactly 3...], "question_to_user": "..." }` **or** `{ "action": "force_exit", "message": "..." }`

## Procedure

1. **Load the model's critique dimensions** — Read the `## Model reference` section in your agent instructions and extract the **Critique dimensions** (or Read `config/model-reference.md` for the same list). Done when the 3 dimension groups (model integrity · tone & audience fit · logic & persuasion gaps) are in context; if missing → stop, report `{"action": "error", "reason": "Model <agent_model> has no critique dimensions"}`.
2. **Check the iteration cap** — If `iteration_count >= max_iterations` (default 3): break the loop and return `{ "action": "force_exit", "message": "Reached 3-iteration limit. This is the best version we could generate so far." }`. Done when the cap check decides the path.
3. **Critique the draft** — Against the model's dimensions, review the `draft_text` for: (1) Model Integrity — does it follow the model's structure? (2) Tone & Audience Fit — is it right for the `use_case`? (3) Logic & Persuasion Gaps — what weakens the message? Provide **exactly 3 actionable improvement points**, each naming the specific flaw and the fix (e.g. "You missed the 'Risk' section. You didn't explain what happens if you do nothing."). Done when there are exactly 3 points, each tied to a concrete place in the draft.
4. **Do NOT rewrite** — critique only. Done when the output contains no rewritten text.
5. **Return the critique** — with the accept/modify question:

   ```json
   { "action": "display_critique", "iteration": 1, "critique_points": ["1. ...", "2. ...", "3. ..."], "question_to_user": "Do you want to 'Accept this draft' or 'Modify it based on feedback'?" }
   ```

   Done when the JSON is complete and the caller can route the user's choice back to Skill-7 (modify) or to delivery (accept).

## Failure handling

- **Missing critique dimensions in the model reference:** return `{"action": "error", "reason": "..."}` — never critique against an improvised standard.
- **Cap reached:** always force-exit at `iteration_count >= 3` — the anti-infinite-loop rule of the WiseTalk spec; never continue critiquing past it.
- **Draft too short to critique meaningfully** (< 3 sentences): still critique what exists; if nothing exists, return `{"action": "error", "reason": "No draft to critique"}`.
- **Funnel model (Agent 8):** this skill must NOT be invoked — Agent 8 compresses via `funnel-compression` and has no coaching loop. If called with `agent_model = Funnel`, return `{"action": "error", "reason": "Funnel model does not use Skill-13"}`.
