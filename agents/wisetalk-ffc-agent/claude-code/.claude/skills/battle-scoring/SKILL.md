---
name: battle-scoring
description: Score a completed battle transcript — impartial 0–100 judgment on logic, EQ, on-the-spot responsiveness, and persuasion, with exactly 2 actionable tips (WiseTalk Skill-9). Use when the Simulation Battle Arena round ends (user exits or the loop finishes), or when the user asks to score a battle transcript. Do NOT use for critiquing drafts or speeches (that is the iterative-critique loop), for running the battle itself (battle-simulator), or for trend analysis of past scores (growth-trends).
license: MIT
compatibility: LLM-driven (no scripts)
metadata:
  author: WiseTalk (via skill-generator)
  version: 1.0.0
---

# Multi-Dimensional Quantitative Scoring (WiseTalk Skill-9)

## Important
- **Impartial judge**: score the USER's defense only — never the persona, never the battle outcome. Valve activation is neither penalized nor rewarded.
- **Every score traces to evidence**: cite the exchange each score comes from; every tip quotes the user's actual words. Never score a transcript you weren't given — ask for it.
- **The contract is fixed**: 4 integer scores 0–100 + exactly 2 tips. Never add a dimension, never deliver fewer or more tips.

## Instructions

### Step 1: Receive the transcript
Take the full battle transcript from Skill-8 (the `chat_history`). Count the rounds — a round is one user turn + one `ai_reply` exchange. Order matters: first exclude incomplete rounds (a round needs both a user turn and an `ai_reply`), then apply the <3 rule to the complete-round count:
- Fewer than 3 complete rounds: return `{"error": "Insufficient data for accurate scoring."}` and suggest running a longer battle — never score.
- No transcript provided: ask for it once.
- Partial/interrupted transcript: score only the complete rounds and state the count in the report.
Done when: the transcript is in hand and the complete-round count is known.

### Step 2: Apply the judge prompt
Analyze the transcript with the Master Spec's judge prompt:
> You are an impartial communication judge. Based on the transcript, score the user from 0 to 100 on: `Logic_Clarity`, `Emotional_Empathy`, `On_the_Spot_Responsiveness`, and `Persuasiveness`. Provide exactly 2 actionable tips for improvement.

Expected output — the contract, verbatim shape:
```json
{"logic": 80, "eq": 72, "response_speed": 95, "persuasion": 65, "advice": ["You forgot to use hard data when defending your point.", "Use 'we' instead of 'I' to sound more collaborative."]}
```
If the output misses a key, holds a non-integer or out-of-range score, or has fewer/more than 2 tips: ask the model once to re-emit against the contract; on a second failure, trim to the contract shape yourself and note it.
Done when: the object parses with exactly the 5 keys — scores as 0–100 integers, `advice` exactly 2 strings.

### Step 3: Deliver with evidence
Deliver the score report with per-dimension evidence — one line per dimension naming the exchange it came from (e.g. "Logic 80: in round 2 you answered the ROI question with numbers, but in round 4 you repeated an estimate without backing") — and the 2 tips quoting the user's own words. Then state the persistence hook: Skill-10 `growth-trends` reads historical scores when the dashboard loads.
Done when: scores + evidence + tips are delivered and the Skill-10 hook is stated.

## Examples

### Example 1: 5-round salary negotiation battle (signature case)
User says: "score the battle we just did" after a 5-round Salary_Negotiation arena.
Actions: 5 rounds ≥ 3 → apply the judge prompt → deliver.
Result:
```json
{"logic": 80, "eq": 72, "response_speed": 95, "persuasion": 65, "advice": ["You forgot to use hard data when defending your point.", "Use 'we' instead of 'I' to sound more collaborative."]}
```
plus one evidence line per dimension and the Skill-10 hook.

### Example 2: Too short
User says: "score that" after a 2-round battle.
Actions: round count 2 < 3 → error path.
Result: `{"error": "Insufficient data for accurate scoring."}` — no scores invented.

## Troubleshooting

### Error: the model adds a 5th dimension or a 3rd tip
Cause: contract drift.
Solution: re-emit against the contract (Step 2); on a second failure, trim to the 5-key object yourself and note it.

### Error: scores don't match the transcript
Cause: the judge generalized instead of reading the rounds.
Solution: re-run Step 2 demanding one cited exchange per score; drop or re-score any dimension with no evidence.

### Error: the user asks to score a draft, not a battle
Cause: confusion with the critique loop (Skill-13).
Solution: clarify — drafts get 3 critique points during the coaching loop; battle-scoring runs only on arena transcripts.

## Fallback
If the transcript is missing: ask for it — never score an invented battle. If the transcript has fewer than 3 rounds: return the Master Spec error verbatim. If the judge output won't parse: re-emit once, then deliver the best-effort scores with a gap note — never fabricate a clean report.
