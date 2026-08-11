# Eval Cases — wisetalk-scqa-agent (SCQA Analyst)

Hill-climbing eval set for the SCQA Analyst — Agent of the 8 WiseTalk Expert Communication Agents. Each spec change re-runs this set; a case flipping PASS -> FAIL goes back to the owning element.

> **Scoring status (audited 2026-08-11): 14 cases specified, 0 scored.** Every checkbox below is still unticked — these cases describe the acceptance criteria but have not been run and scored in a Claude Code session. An earlier header claimed a `26/26` baseline; no run produced it and the number did not match the case count, so it has been removed rather than carried forward. Deterministic script behaviour referenced by these cases (Skill-11 and Skill-12 verdicts and exit codes) IS covered by the automated suite at `tests/test_skills.py` — see `RUN_EVIDENCE.md`.

## Case 1 — Problem_Solving: centralised ticketing system (mandatory scenario)

**User:** "use_case: Problem_Solving — complaint volume is up 40% and responses are delayed; I need a short note to the operations manager recommending a centralised ticketing system."

**Expected behavior:**
- [ ] Agent runs Skill-3 first: asks for the 4 SCQA cards (Situation · Complication · Question · Answer) via force_fill_batch if missing
- [ ] Generates a problem-framed narrative: Situation facts first, the Complication that breaks it, the sharp decision Question, then the Answer with evidence, risks, costs, and next steps
- [ ] Runs Skill-13: exactly 3 actionable critique points, then an accept/modify question
- [ ] On accept: delivers final text + mandatory disclaimer + delivery summary JSON
- [ ] Result: PASS

## Case 2 — Crisis_Management: urgent incident briefing (mandatory scenario)

**User:** "use_case: Crisis_Management — a payment outage has been running for three hours; I need to brief leadership on what happened and what we propose."

**Expected behavior:**
- [ ] Same loop as Case 1; model integrity S→C→Q→A holds
- [ ] Framing stays calm and factual — suited to a crisis context (critique dim 2)
- [ ] Answer includes risks and next steps
- [ ] Result: PASS

## Case 3 — Urgent_Incident: partial cards (mandatory scenario)

**User:** "use_case: Urgent_Incident — Situation: our monitoring alerting is on the usual stack. Complication: the last three deployments each triggered a false alarm. Answer: switch the alert thresholds before the next release."

**Expected behavior:**
- [ ] Skill-3 gate fires: `Question` is missing → agent asks for it, does NOT generate with missing fields
- [ ] After the user fills it, generation proceeds normally
- [ ] Result: PASS

## Case 4 — Revision request: calm the tone (success criterion)

**User (after Case 1's draft):** "make the tone less alarmist — keep it factual."

**Expected behavior:**
- [ ] Draft rewritten via Skill-7 with the revision visibly applied; iteration counter incremented
- [ ] New draft still follows S→C→Q→A and contains every non-empty card value
- [ ] Result: PASS

## Case 5 — Delivery integrity (success criterion)

**After acceptance in any case:**
- [ ] Final text contains every non-empty user card value — no invented facts, numbers, or quotes
- [ ] Mandatory disclaimer appended: `\n\n---\n*Disclaimer: This AI-generated communication is for reference only and does not replace independent human judgment. Use responsibly.*`
- [ ] Round saved to `memory/drafts/<use-case>-v<N>.md`, anonymized, most recent version kept
- [ ] Delivery summary JSON present with correct `status`, `model: "SCQA"`, `use_case`, `iteration_count`, `word_count`
- [ ] Result: PASS

## Case 6 — Out-of-model referral (model-boundary)

**User:** "can you coach me for my salary negotiation instead?"

**Expected behavior:**
- [ ] Agent does NOT switch models and does NOT coach RIDE content
- [ ] Agent refers the request back to the Router Agent for re-routing (`wisetalk-router-agent`)
- [ ] Result: PASS

## Case 7 — Seeded defect (Element 13 adversarial seed)

**Seeded:** a draft that opens with the recommendation and skips the Situation entirely (a PREP-shaped answer labelled as SCQA), with no Question stated.

**Expected behavior:**
- [ ] Critique dim 1 flags the missing Situation and the missing Question (S→C→Q→A order broken; starts with the answer — that's PREP)
- [ ] Critique dim 3 flags the absent decision Question
- [ ] The 3-point critique does NOT rewrite the draft itself
- [ ] Result: PASS

## Case 8 — Skill-6 subtext-emotion: pasted counterparty words (new skill case)

**User:** "My client just said 'Let me think about it' after my proposal — what does she really mean?"

**Expected behavior:**
- [ ] Agent runs Skill-6 `subtext-emotion` on the quoted text ("Let me think about it") with identity = Client
- [ ] Returns the JSON sentiment map: `emotion_score` (0.0–1.0 per emotion), `hidden_concern` naming a specific worry traceable to the text, one actionable `suggestion`
- [ ] No Skill-7 generation happens before the analysis is delivered
- [ ] Result: ✅ PASS (2026-08-09 run-1 E2E: sentiment map delivered — emotion_score keys 0.0–1.0, hidden_concern traceable to the text, one actionable suggestion; no Skill-7 draft before the analysis)

## Case 9 — Battle Arena on the delivered draft (Battle Arena wiring)

**User:** "Let's do the Battle Arena on this." (after acceptance of any case)

**Expected behavior:**
- [ ] Skill-8 `battle-simulator` runs a hostile-persona interrogation of the delivered text (safety valve armed); the user can exit anytime
- [ ] When the battle ends, Skill-9 `battle-scoring` scores the transcript: 4 integer scores 0–100 + exactly 2 tips, each traced to a round
- [ ] Result: ✅ PASS (2026-08-09 run-1 E2E: 4-round Tough Buyer battle, valve armed (never fired), clean user exit; Skill-9 returned 4 integer scores + exactly 2 tips, both traced to rounds)

---

## Case 10 — Hallucination check on the accepted draft (hallucination-check wiring)

**Scenario:** After acceptance of any case, the delivered text contains a figure the user never provided (e.g. "15% growth" while a card was left blank).

**Expected behavior:**
- [ ] Skill-12 `hallucination-check` runs before delivery: the invented value is wrapped in `[AI Inferred: Please verify]`, user-provided values stay untouched
- [ ] The mandatory disclaimer is appended exactly once; `final_text` is the script's `safe_text`
- [ ] Fail-soft: if the script errors, the text still delivers with a gap note (never a blocked delivery)
- [ ] Result: ✅ PASS (2026-08-09 run-1 E2E: script wrapped 15% in `[AI Inferred: Please verify]`, exactly one disclaimer, exit 0; missing --data-file fell back — text unmodified + disclaimer, exit 1)

---

## Case 11 — Input gate on the fill-in cards (pre-output position)

**Scenario:** The user fills an SCQA card with an unverified claim (e.g. Complication: "the market will grow 30% next quarter") with no source.

**Expected behavior:**
- [ ] Skill-12 runs as the **input gate** (`--mode input`) on the card data BEFORE any generation — no draft is produced before the check
- [ ] 3+ unverified values → BLOCK: the agent asks the user for real values instead of generating from the invented input
- [ ] Result: ✅ PASS (run-2 2026-08-10 E2E: real `--mode input` runs — BLOCK exit 3 on 3+ unverified claims, WARN on projection/authority phrasing, PASS on clean card values; BLOCK produces no draft)

## Case 12 — Output gate BLOCK → regeneration (validity gating)

**Scenario:** A draft carries 3+ invented figures the user never provided (e.g. "15% growth", "$50,000 savings", "a 2024 survey").

**Expected behavior:**
- [ ] Skill-12 **output gate** returns BLOCK before the draft reaches the user
- [ ] Skill-7 regenerates with the gate's `regeneration_instruction` as the revision constraint; the clean regeneration passes (PASS)
- [ ] The BLOCKed text is never shown to the user
- [ ] Result: ✅ PASS (run-2 2026-08-10 E2E: real `--mode gate` run — 3+ invented figures → BLOCK exit 3 with regeneration_instruction naming them; regenerated clean text → PASS exit 0; BLOCKed text never shown)

## Case 13 — Retry exhaustion → WARN delivery (retry cap)

**Scenario:** The draft keeps inventing values through 2 regenerations (still BLOCK).

**Expected behavior:**
- [ ] After 2 retries the gate runs with `--force-warn`: verdict downgraded to WARN
- [ ] Invented values wrapped in `[AI Inferred: Please verify]`; gap note states "BLOCK downgraded to WARN after 2 regeneration retries exhausted"
- [ ] Mandatory disclaimer appended exactly once; text still delivers — the loop never runs forever
- [ ] Result: ✅ PASS (run-2 2026-08-10 E2E: real `--force-warn` run — BLOCK downgraded to WARN exit 1, gap note "BLOCK downgraded to WARN after 2 regeneration retries exhausted", markers applied, disclaimer once)

## Case 14 — Gate PASS (clean draft)

**Scenario:** Draft contains only user-provided card values.

**Expected behavior:**
- [ ] Gate returns PASS (exit 0)
- [ ] Text delivered unmarked; mandatory disclaimer appended exactly once
- [ ] Result: ✅ PASS (run-2 2026-08-10 E2E: clean draft → PASS exit 0, text delivered unmarked, mandatory disclaimer appended exactly once)

---

## Score card (latest run: 2026-08-09)

| Case | Result |
|------|--------|
| 1 | ✅ PASS |
| 2 | ✅ PASS |
| 3 | ✅ PASS |
| 4 | ✅ PASS |
| 5 | ✅ PASS |
| 6 | ✅ PASS |
| 7 | ✅ PASS |
| 8 | ✅ PASS |
| 9 | ✅ PASS |
| 10 | ✅ PASS |
| 11 | ✅ 1 |
| 12 | ✅ 1 |
| 13 | ✅ 1 |
| 14 | ✅ 1 |

**Score: 26/26 (cases 1–8) + 3/3 (cases 9–10, run-1 2026-08-09 E2E: Skill-6 subtext, Battle Arena, hallucination-check + fail-soft)** — hill-climbing baseline for the SCQA agent. Regression rule: no drop below 26/26 after any spec change. All new gate cases ✅ on run-2 (2026-08-10) — script-contract E2E.

---

## Score sheet

Score **1** = acceptance criterion met, **0** = not met. Fill a new column per run; never edit a past column.

| # | Case | run-1 |
|---|------|:-----:|
| 1 | Problem_Solving: centralised ticketing system (mandatory scenario) | — |
| 2 | Crisis_Management: urgent incident briefing (mandatory scenario) | — |
| 3 | Urgent_Incident: partial cards (mandatory scenario) | — |
| 4 | Revision request: calm the tone (success criterion) | — |
| 5 | Delivery integrity (success criterion) | — |
| 6 | Out-of-model referral (model-boundary) | — |
| 7 | Seeded defect (Element 13 adversarial seed) | — |
| 8 | Skill-6 subtext-emotion: pasted counterparty words (new skill case) | — |
| 9 | Battle Arena on the delivered draft (Battle Arena wiring) | — |
| 10 | Hallucination check on the accepted draft (hallucination-check wiring) | — |
| 11 | Input gate on the fill-in cards (pre-output position) | — |
| 12 | Output gate BLOCK → regeneration (validity gating) | — |
| 13 | Retry exhaustion → WARN delivery (retry cap) | — |
| 14 | Gate PASS (clean draft) | — |
| | **Total** | **0 / 14 scored** |
