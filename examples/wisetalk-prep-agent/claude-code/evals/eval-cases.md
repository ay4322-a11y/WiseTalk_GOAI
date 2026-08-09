# Eval Cases — wisetalk-prep-agent (PREP Speaker)

Hill-climbing eval set for the PREP Speaker — Agent 4 of the 8 WiseTalk Expert Communication Agents. Each spec change re-runs this set; the score must not drop below the baseline (26/26, latest run 2026-08-09).

## Case 1 — Elevator_Pitch: automate the monthly sales report (mandatory scenario)

**User:** "use_case: Elevator_Pitch — I need a quick 30-second pitch for automating our monthly sales report, to use at tomorrow's standup."

**Expected behavior:**
- [ ] Agent runs Skill-3 first: asks for the 4 PREP cards (Point · Reason · Example · Action) via force_fill if missing
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

**Score: 26/26** — hill-climbing baseline for the PREP agent. Regression rule: no drop below 26/26 after any spec change.
