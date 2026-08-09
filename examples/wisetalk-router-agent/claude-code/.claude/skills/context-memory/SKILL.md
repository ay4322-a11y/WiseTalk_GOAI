---
name: context-memory
# Model-invoked (no disable-model-invocation): the router agent reaches this skill
# automatically right after Skill-1 routes — this is Skill-2 of the WiseTalk spec.
description: Fetch the last 10 rounds of conversation history from memory and format them as a chat_history_string for injection into a downstream Expert Agent. Use after intent-routing has produced a routing decision, on every routed message. Do NOT use for storing new history — appending is the router agent's Element 14 responsibility.
---

# Skill-2: Cross-Agent Context Memory Inheritance

Input: none beyond the current session (reads `memory/chat-history.md`)
Output: `chat_history_string` — formatted conversation history, or `""` when no history exists

## Procedure

1. **Locate the history file** — Glob for `memory/chat-history.md`. Done when found or confirmed missing.
2. **Read the last 10 rounds** — Read the file; take the 10 most recent `**User:**`/`**Assistant:**` pairs (most recent last). Done when 10 rounds (or all available, if fewer) are extracted.
3. **Estimate token count** — rough estimate: `characters / 4`. Done when the count is known.
4. **Apply the rolling window** — if the estimate exceeds 4000 tokens:
   - Keep the **first 2 rounds** and the **last 3 rounds**, drop the middle.
   - Re-estimate; if still over 4000, keep **first 1 + last 2**.
   - Never split a round in half. Done when ≤ 4000 tokens or 3 rounds remain.
5. **Format** — one round per two lines, newest last:

   ```
   User: <user message>
   Assistant: <assistant reply>
   ```

   Done when every extracted round appears in order.
6. **Return** — the formatted string, or `""` if the file is missing/empty.

## Failure handling

- **Missing or empty `chat-history.md`:** return `""` — this is a first-turn conversation, no prior context needed.
- **Token overflow after maximum truncation:** return the remaining 3 rounds with a note in the trace that history was truncated.
- **Malformed history** (unparseable round markers): return `""` and note the malformed line — never guess at content.
- **Never include data the user did not write** — history is reproduced as stored, with names already anonymized to `[User]` / `[Company]`.
