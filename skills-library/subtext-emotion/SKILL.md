---
name: subtext-emotion
description: Analyze the subtext of the other party's exact words — hidden intentions, defensiveness, and concerns beneath the surface, as a JSON sentiment map with emotion scores and a suggestion. Use when the user pastes or quotes the counterparty's words in a negotiation or problem-solving context ("my client said...", "my boss replied...", "here is their email"). Do NOT use for the user's own drafts or speeches, for generating replies, or for scoring battle transcripts.
license: MIT
compatibility: LLM-driven (no scripts)
metadata:
  author: WiseTalk (via skill-generator)
  version: 1.0.0
---

# Subtext & Emotion Analysis (WiseTalk Skill-6)

## Important
- Emotion scores and the hidden concern must **trace to evidence in the target text** — never attribute a motivation the words cannot support, never invent emotions.
- Sarcasm / passive-aggression detection runs **first** — when triggered, the warning response is the output; the user is advised to clarify, never coached into a sharp reply.
- Never analyze on a guessed identity — if the speaker is unknown, ask once before proceeding.

## Instructions

### Step 1: Fix the target text and identity
Identify the `target_text` (the counterparty's exact words, quoted verbatim) and `target_identity` (Client, Boss, Vendor, Stakeholder…). If the user didn't name the speaker, ask once — or use the agent's current use case as the default (e.g. `Salary_Negotiation` → the counterparty) and say so.
Done when both are known and the text is the counterparty's, not the user's own draft.

### Step 2: Apply the analysis prompt
Analyze the text with this prompt, substituting the values:

> Given the text: `[<target_text>]` from a `[<target_identity>]`. Analyze the hidden intentions, defensiveness, and specific concerns hidden beneath the words. First detect sarcasm or passive-aggressiveness. Output the results as a strict JSON object.

**Sarcasm/PA first:** if sarcasm or passive-aggressiveness is detected, skip the full map and return:
```json
{"warning": "Sarcasm detected. Best to ask for clarification before responding.", "suggestion": "<one concrete clarifying question or move, e.g. 'Ask: is the concern about the budget or about the timeline?'>"}
```

**Otherwise return the sentiment map:**
```json
{
  "emotion_score": {"<emotion>": 0.0-1.0, "...": "..."},
  "hidden_concern": "<the specific worry beneath the words>",
  "suggestion": "<one concrete next move grounded in the concern>"
}
```
Done when the output is a strict JSON object with the required keys and every score maps to a cue in the text.

### Step 3: Validate and deliver
Check the map: each `emotion_score` value is between 0.0 and 1.0; `hidden_concern` is specific (names the worry, not "they are unsure"); `suggestion` is one actionable move within the current model's domain.
If the output isn't parseable JSON: ask the model once to re-emit as strict JSON; on a second failure, deliver the analysis as prose with a note that the map failed to parse — never fabricate a map.
Done when the returned object is the validated JSON (or the documented prose fallback).

## Examples

### Example 1: Hesitation (signature case)
User says: "My client just said 'Let me think about it' after my proposal — what does she really mean?"
Actions: target_text = "Let me think about it", target_identity = "Client" → apply the prompt.
Result (shape):
```json
{"emotion_score": {"hesitation": 0.8, "interest": 0.4}, "hidden_concern": "They are worried about the budget, not the quality.", "suggestion": "Provide a cost-benefit table immediately."}
```

### Example 2: Sarcasm
User says: "My boss replied 'Oh great, ANOTHER new process, just what we needed'."
Actions: the analysis prompt detects sarcasm first → return the warning response, no emotion map.

## Troubleshooting

### Error: the map contains an emotion the text can't support
Cause: the model extrapolated beyond the words.
Solution: re-run Step 2 demanding evidence for each score; drop scores with no textual cue.

### Error: identity unknown
Cause: the user pasted words without naming the speaker.
Solution: ask once; if they can't say, use the agent's use case default and state it.

## Fallback
If the analysis prompt fails twice to produce parseable JSON: deliver the read as prose with a visible note — never fabricate a sentiment map. If the text is empty or not the counterparty's words: stop and ask for the exact text.

## Customization points

- **Analysis prompt:** Step 2's prompt is the WiseTalk PDF's system prompt. Swap the phrasing while keeping the JSON contract (`emotion_score` 0.0–1.0, `hidden_concern`, `suggestion`) if a different output shape is needed downstream.
- **Sarcasm/PA detection:** currently delegated to LLM judgment ("detect sarcasm first"). To make it stricter, add explicit marker lists (ALL-CAPS, repeated punctuation, "sure, ANOTHER…" patterns) to Step 2.
- **Emotion vocabulary:** score keys are free-form (e.g. hesitation, interest). Pin a fixed taxonomy (e.g. 6 core emotions) if a dashboard needs stable keys.
- **Identity default:** Step 1 falls back to the agent's use case (e.g. `Salary_Negotiation` → the counterparty). Replace the default resolution rule to change it.
- **JSON failure policy:** the skill re-emits once, then degrades to prose. Tighten (no re-emit) or loosen (never prose) per integration policy.
