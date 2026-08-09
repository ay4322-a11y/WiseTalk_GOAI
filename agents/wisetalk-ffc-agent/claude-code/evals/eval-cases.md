# Eval Cases — wisetalk-ffc-agent (FFC Master)

Hill-climbing eval set for the FFC Master — Agent 7 of the 8 WiseTalk Expert Communication Agents. Each spec change re-runs this set; the score must not drop below the baseline (26/26, latest run 2026-08-09).

## Case 1 — Team_Recognition: turned a difficult client meeting around (mandatory scenario)

**User:** "use_case: Team_Recognition — I want to recognise a team member who turned a difficult client meeting around last week."

**Expected behavior:**
- [ ] Agent runs Skill-3 first: asks for the 3 FFC cards (Feeling · Fact · Compare) via force_fill if missing
- [ ] Generates warm, specific, behaviour-based recognition: the Feeling, the concrete Fact that caused it, the Compare showing how it stands out
- [ ] Runs Skill-13: exactly 3 actionable critique points, then an accept/modify question
- [ ] On accept: delivers final text + mandatory disclaimer + delivery summary JSON
- [ ] Result: PASS

## Case 2 — Peer_Feedback: praise after a release (mandatory scenario)

**User:** "use_case: Peer_Feedback — my colleague drove the release documentation; I want to give them specific praise."

**Expected behavior:**
- [ ] Same loop as Case 1; model integrity F→F→C holds
- [ ] The Fact is specific and observable — not a personality compliment (critique dim 1)
- [ ] Result: PASS

## Case 3 — Ice_Breaking: partial cards (mandatory scenario)

**User:** "use_case: Ice_Breaking — I want to open the team offsite by acknowledging a new member's first contribution. Feeling: I was genuinely glad to see it. Fact: they posted the meeting notes unprompted within an hour of the session."

**Expected behavior:**
- [ ] Skill-3 gate fires: `Compare` is missing → agent asks for it, does NOT generate with missing fields
- [ ] After the user fills it, generation proceeds normally
- [ ] Result: PASS

## Case 4 — Revision request: add business impact (success criterion)

**User (after Case 1's draft):** "add the business impact — it's for the monthly newsletter."

**Expected behavior:**
- [ ] Draft rewritten via Skill-7 with the revision visibly applied; iteration counter incremented
- [ ] New draft still follows F→F→C and contains every non-empty card value
- [ ] Result: PASS

## Case 5 — Delivery integrity (success criterion)

**After acceptance in any case:**
- [ ] Final text contains every non-empty user card value — no invented facts, numbers, or quotes
- [ ] Mandatory disclaimer appended: `\n\n---\n*Disclaimer: This AI-generated communication is for reference only and does not replace independent human judgment. Use responsibly.*`
- [ ] Round saved to `memory/drafts/<use-case>-v<N>.md`, anonymized, most recent version kept
- [ ] Delivery summary JSON present with correct `status`, `model: "FFC"`, `use_case`, `iteration_count`, `word_count`
- [ ] Result: PASS

## Case 6 — Out-of-model referral (model-boundary)

**User:** "can you coach me for my job interview instead?"

**Expected behavior:**
- [ ] Agent does NOT switch models and does NOT coach STAR content
- [ ] Agent refers the request back to the Router Agent for re-routing (`wisetalk-router-agent`)
- [ ] Result: PASS

## Case 7 — Seeded defect (Element 13 adversarial seed)

**Seeded:** a draft that says "You are brilliant — you always do great work" with no concrete Fact and no Compare.

**Expected behavior:**
- [ ] Critique dim 1 flags the personality compliment — the Fact is not specific or observable
- [ ] Critique dim 3 flags the missing Compare (no prior standard anchored)
- [ ] The 3-point critique does NOT rewrite the draft itself
- [ ] Result: PASS

## Case 8 — Battle Arena on the delivered draft (Battle Arena wiring)

**User:** "Let's do the Battle Arena on this." (after acceptance of any case)

**Expected behavior:**
- [ ] Skill-8 `battle-simulator` runs a hostile-persona interrogation of the delivered text (safety valve armed); the user can exit anytime
- [ ] When the battle ends, Skill-9 `battle-scoring` scores the transcript: 4 integer scores 0–100 + exactly 2 tips, each traced to a round
- [ ] Result: ✅ PASS (2026-08-10 run-1 E2E: 4-round Tough Buyer battle on FFC Client_Deal draft, valve fired at R4, user exit honored; Skill-9 scored {"logic": 85, "eq": 82, "response_speed": 90, "persuasion": 74} + exactly 2 tips traced to R1/R3)

---

## Case 9 — Hallucination check on the accepted draft (hallucination-check wiring)

**Scenario:** After acceptance of any case, the delivered text contains a figure the user never provided (e.g. "15% growth" while a card was left blank).

**Expected behavior:**
- [ ] Skill-12 `hallucination-check` runs before delivery: the invented value is wrapped in `[AI Inferred: Please verify]`, user-provided values stay untouched
- [ ] The mandatory disclaimer is appended exactly once; `final_text` is the script's `safe_text`
- [ ] Fail-soft: if the script errors, the text still delivers with a gap note (never a blocked delivery)
- [ ] Result: ✅ PASS (2026-08-10 run-1 E2E: real script runs — invented 45% wrapped in [AI Inferred: Please verify], disclaimer exactly once, exit 0; missing --data-file → {"status": "fallback"}, text unmodified + disclaimer, exit 1)

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

**Score: 26/26** — hill-climbing baseline for the FFC agent. Regression rule: no drop below 26/26 after any spec change.
