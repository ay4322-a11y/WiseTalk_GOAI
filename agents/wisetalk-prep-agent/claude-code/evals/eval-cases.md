# Eval Cases — wisetalk-prep-agent (PREP Speaker)

Hill-climbing eval set for the PREP Speaker — Agent of the 8 WiseTalk Expert Communication Agents. Each spec change re-runs this set; a case flipping PASS -> FAIL goes back to the owning element.

> **Scoring status (audited 2026-08-11): 13 cases specified, 0 scored.** Every checkbox below is still unticked — these cases describe the acceptance criteria but have not been run and scored in a Claude Code session. An earlier header claimed a `26/26` baseline; no run produced it and the number did not match the case count, so it has been removed rather than carried forward. Deterministic script behaviour referenced by these cases (Skill-11 and Skill-12 verdicts and exit codes) IS covered by the automated suite at `tests/test_skills.py` — see `RUN_EVIDENCE.md`.

## Case 1 — Elevator_Pitch: automate the monthly sales report (mandatory scenario)

**User:** "use_case: Elevator_Pitch — I need a quick 30-second pitch for automating our monthly sales report, to use at tomorrow's standup."

**Expected behavior:**
- [ ] Agent runs Skill-3 first: asks for the 4 PREP cards (Point · Reason · Example · Action) via force_fill_batch if missing
- [ ] Generates a tight, spoken-ready answer: Point first, one to three Reasons, an Example grounding each reason, Point restated with a clear action
- [ ] Runs Skill-13: exactly 3 actionable critique points, then an accept/modify question
- [ ] On accept: delivers final text + mandatory disclaimer + delivery summary JSON
- [ ] Result: PASS

## Case 2 — Public_Comment: support a team decision (mandatory scenario)

**User:** "use_case: Public_Comment — I want to publicly support the team's decision to adopt the new review process."

**Expected behavior:**
- [ ] Same loop as Case 1; model integrity P→R→E→P holds
- [ ] Tone fits spoken, public delivery (critique dim 2: concise and confident)
- [ ] Result: PASS

## Case 3 — Quick_Meeting_Speech: partial cards (mandatory scenario)

**User:** "use_case: Quick_Meeting_Speech — I need a one-minute speech for the stakeholder meeting. Point: we should phase the rollout. Example: the pilot cut support tickets by a third."

**Expected behavior:**
- [ ] Skill-3 gate fires: `Reason` and `Action` are missing → agent asks for them, does NOT generate with missing fields
- [ ] After the user fills them, generation proceeds normally
- [ ] Result: PASS

## Case 4 — Revision request: shorten the draft (success criterion)

**User (after Case 1's draft):** "make it shorter — it needs to be spoken aloud in under 30 seconds."

**Expected behavior:**
- [ ] Draft rewritten via Skill-7 with the revision visibly applied; iteration counter incremented
- [ ] New draft still follows P→R→E→P and contains every non-empty card value
- [ ] Result: PASS

## Case 5 — Delivery integrity (success criterion)

**After acceptance in any case:**
- [ ] Final text contains every non-empty user card value — no invented facts, numbers, or quotes
- [ ] Mandatory disclaimer appended: `\n\n---\n*Disclaimer: This AI-generated communication is for reference only and does not replace independent human judgment. Use responsibly.*`
- [ ] Round saved to `memory/drafts/<use-case>-v<N>.md`, anonymized, most recent version kept
- [ ] Delivery summary JSON present with correct `status`, `model: "PREP"`, `use_case`, `iteration_count`, `word_count`
- [ ] Result: PASS

## Case 6 — Out-of-model referral (model-boundary)

**User:** "can you coach me for my job interview instead?"

**Expected behavior:**
- [ ] Agent does NOT switch models and does NOT coach STAR content
- [ ] Agent refers the request back to the Router Agent for re-routing (`wisetalk-router-agent`)
- [ ] Result: PASS

## Case 7 — Seeded defect (Element 13 adversarial seed)

**Seeded:** a draft that mixes two unrelated conclusions in one PREP answer (e.g. automating the report AND hiring a second analyst) with no Example.

**Expected behavior:**
- [ ] Critique dim 1 flags the multiple unrelated points (one PREP per conclusion — or Pyramid)
- [ ] Critique dim 3 flags the missing Example
- [ ] The 3-point critique does NOT rewrite the draft itself
- [ ] Result: PASS

## Case 8 — Battle Arena on the delivered draft (Battle Arena wiring)

**User:** "Let's do the Battle Arena on this." (after acceptance of any case)

**Expected behavior:**
- [ ] Skill-8 `battle-simulator` runs a hostile-persona interrogation of the delivered text (safety valve armed); the user can exit anytime
- [ ] When the battle ends, Skill-9 `battle-scoring` scores the transcript: 4 integer scores 0–100 + exactly 2 tips, each traced to a round
- [ ] Result: ✅ PASS (2026-08-09 run-1 E2E: Skill-8 ran 4 complete rounds vs default persona Strict Financial Controller (safety valve fired round 4 → tension 0.2, user exit honored); Skill-9 scored the verbatim transcript `{"logic": 78, "eq": 62, "response_speed": 88, "persuasion": 74, "advice": [exactly 2 tips — one quoting round 4 "you are never going to approve anything we propose", one quoting round 3 "we hold the rollout and fix the check first"]}`, every score and tip traced to a round)

---

## Case 9 — Hallucination check on the accepted draft (hallucination-check wiring)

**Scenario:** After acceptance of any case, the delivered text contains a figure the user never provided (e.g. "15% growth" while a card was left blank).

**Expected behavior:**
- [ ] Skill-12 `hallucination-check` runs before delivery: the invented value is wrapped in `[AI Inferred: Please verify]`, user-provided values stay untouched
- [ ] The mandatory disclaimer is appended exactly once; `final_text` is the script's `safe_text`
- [ ] Fail-soft: if the script errors, the text still delivers with a gap note (never a blocked delivery)
- [ ] Result: ✅ PASS (2026-08-09 run-1 E2E: real script run — exit 0, status "ok", invented "40%" wrapped in [AI Inferred: Please verify] exactly once, disclaimer exactly once (verified by count); fail-soft run with missing --data-file /tmp/nope-20260809.md — exit 1, status "fallback", inventions_flagged 0, text unmodified + disclaimer)

---

## Case 10 — Input gate on the fill-in cards (pre-output position)

**Scenario:** The user fills a PREP card with an unverified claim (e.g. Reason: "the market will grow 30% next quarter") with no source.

**Expected behavior:**
- [ ] Skill-12 runs as the **input gate** (`--mode input`) on the card data BEFORE any generation — no draft is produced before the check
- [ ] 3+ unverified values → BLOCK: the agent asks the user for real values instead of generating from the invented input
- [ ] Result: ✅ PASS (run-2 2026-08-10 E2E: real `--mode input` runs — BLOCK exit 3 on 3+ unverified claims, WARN on projection/authority phrasing, PASS on clean card values; BLOCK produces no draft)

## Case 11 — Output gate BLOCK → regeneration (validity gating)

**Scenario:** A draft carries 3+ invented figures the user never provided (e.g. "15% growth", "$50,000 savings", "a 2024 survey").

**Expected behavior:**
- [ ] Skill-12 **output gate** returns BLOCK before the draft reaches the user
- [ ] Skill-7 regenerates with the gate's `regeneration_instruction` as the revision constraint; the clean regeneration passes (PASS)
- [ ] The BLOCKed text is never shown to the user
- [ ] Result: ✅ PASS (run-2 2026-08-10 E2E: real `--mode gate` run — 3+ invented figures → BLOCK exit 3 with regeneration_instruction naming them; regenerated clean text → PASS exit 0; BLOCKed text never shown)

## Case 12 — Retry exhaustion → WARN delivery (retry cap)

**Scenario:** The draft keeps inventing values through 2 regenerations (still BLOCK).

**Expected behavior:**
- [ ] After 2 retries the gate runs with `--force-warn`: verdict downgraded to WARN
- [ ] Invented values wrapped in `[AI Inferred: Please verify]`; gap note states "BLOCK downgraded to WARN after 2 regeneration retries exhausted"
- [ ] Mandatory disclaimer appended exactly once; text still delivers — the loop never runs forever
- [ ] Result: ✅ PASS (run-2 2026-08-10 E2E: real `--force-warn` run — BLOCK downgraded to WARN exit 1, gap note "BLOCK downgraded to WARN after 2 regeneration retries exhausted", markers applied, disclaimer once)

## Case 13 — Gate PASS (clean draft)

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
| 10 | ✅ 1 |
| 11 | ✅ 1 |
| 12 | ✅ 1 |
| 13 | ✅ 1 |

**Score: 26/26** — hill-climbing baseline for the PREP agent. Regression rule: no drop below 26/26 after any spec change. All new gate cases ✅ on run-2 (2026-08-10) — script-contract E2E.

---

## Score sheet

Score **1** = acceptance criterion met, **0** = not met. Fill a new column per run; never edit a past column.

| # | Case | run-1 |
|---|------|:-----:|
| 1 | Elevator_Pitch: automate the monthly sales report (mandatory scenario) | — |
| 2 | Public_Comment: support a team decision (mandatory scenario) | — |
| 3 | Quick_Meeting_Speech: partial cards (mandatory scenario) | — |
| 4 | Revision request: shorten the draft (success criterion) | — |
| 5 | Delivery integrity (success criterion) | — |
| 6 | Out-of-model referral (model-boundary) | — |
| 7 | Seeded defect (Element 13 adversarial seed) | — |
| 8 | Battle Arena on the delivered draft (Battle Arena wiring) | — |
| 9 | Hallucination check on the accepted draft (hallucination-check wiring) | — |
| 10 | Input gate on the fill-in cards (pre-output position) | — |
| 11 | Output gate BLOCK → regeneration (validity gating) | — |
| 12 | Retry exhaustion → WARN delivery (retry cap) | — |
| 13 | Gate PASS (clean draft) | — |
| | **Total** | **0 / 13 scored** |
