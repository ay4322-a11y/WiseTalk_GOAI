# Eval Cases — wisetalk-funnel-agent (Funnel Refiner)

Hill-climbing eval set for the Funnel Refiner — Agent 8 of the 8 WiseTalk Expert Communication Agents. Each spec change re-runs this set; the score must not drop below the baseline (26/26, latest run 2026-08-09).

## Case 1 — Task_Delegation: 500-word vendor email (mandatory scenario)

**User:** "use_case: Task_Delegation — here is the vendor's 500-word requirements email; compress it into what our team actually needs to act on." (followed by a ~500-word email containing requirements, owners, and a hard deadline)

**Expected behavior:**
- [ ] Agent runs Skill-3 first: validates the `OriginalText` card (non-empty, more than 50 words)
- [ ] Runs Skill-5: compresses to under 20% of the original length — action items, data, and conclusions only
- [ ] Every action item and deadline from the email appears **verbatim** in the summary
- [ ] Acceptance checks pass (length_ok, actions_preserved, no_invention); loss_rate reported
- [ ] Delivers: summary + mandatory disclaimer + delivery summary JSON (with `word_count_original`, `word_count_compressed`, `loss_rate`)
- [ ] Result: PASS

## Case 2 — Complex_Instruction: 400-word onboarding brief (mandatory scenario)

**User:** "use_case: Complex_Instruction — compress this onboarding brief for a new contractor." (a ~400-word brief with setup steps and a training deadline)

**Expected behavior:**
- [ ] Same pipeline as Case 1; model integrity holds (core 20% only, no background padding)
- [ ] Result: PASS

## Case 3 — Short text: the gate fires (mandatory scenario)

**User:** "use_case: Information_Compression — compress this: 'Remind the team about Friday's review.'"

**Expected behavior:**
- [ ] Skill-3 gate refuses: text is 50 words or fewer → `force_fill_batch` asks for the full text
- [ ] No compression attempt on the short text
- [ ] Result: PASS

## Case 4 — Revision request: restore the deadline (success criterion)

**User (after Case 1's delivery):** "you dropped the Friday deadline."

**Expected behavior:**
- [ ] One re-compression restores the deadline verbatim; iteration/trace updated
- [ ] A second revision request after re-compression is refused (cap) with a gap note — no infinite loop
- [ ] Result: PASS

## Case 5 — Delivery integrity (success criterion)

**After acceptance in any case:**
- [ ] Compressed length is under 20% of the original (or the gap note states the actual ratio)
- [ ] Every action item and deadline from the original appears verbatim — nothing invented
- [ ] Mandatory disclaimer appended: `\n\n---\n*Disclaimer: This AI-generated communication is for reference only and does not replace independent human judgment. Use responsibly.*`
- [ ] Round saved to `memory/drafts/<use-case>-v<N>.md`, anonymized, most recent version kept
- [ ] Delivery summary JSON present with correct `status`, `model: "Funnel"`, `use_case`, lengths, and `loss_rate`
- [ ] Result: PASS

## Case 6 — Out-of-model referral (model-boundary)

**User:** "can you coach me for my job interview instead?"

**Expected behavior:**
- [ ] Agent does NOT switch models and does NOT coach STAR content
- [ ] Agent refers the request back to the Router Agent for re-routing (`wisetalk-router-agent`)
- [ ] Result: PASS

## Case 7 — Seeded defect (acceptance-check adversarial seed)

**Seeded:** a compression output that keeps the background narrative but drops the action item and its deadline (the Funnel's #1 common mistake).

**Expected behavior:**
- [ ] Skill-5's `actions_preserved` check fails → the action item and deadline are added back verbatim
- [ ] No invented content introduced by the repair
- [ ] Result: PASS

## Case 8 — Battle Arena on the delivered summary (Battle Arena wiring)

**User:** "Let's do the Battle Arena on this." (after acceptance of any case)

**Expected behavior:**
- [ ] Skill-8 `battle-simulator` runs a hostile-persona interrogation of the delivered summary (safety valve armed); the user can exit anytime
- [ ] When the battle ends, Skill-9 `battle-scoring` scores the transcript: 4 integer scores 0–100 + exactly 2 tips, each traced to a round
- [ ] Result: ✅ PASS (2026-08-09 run-1 E2E: 3-round Strict Financial Controller battle on the delivered Funnel summary; valve fired on the hostile round 4 (tension 0.2), exit honored; Skill-9 scored `{"logic": 78, "eq": 55, "response_speed": 82, "persuasion": 68, "advice": [...]}` — 4 integer scores, exactly 2 tips, each with cited exchanges)

---

## Case 9 — Hallucination check on the accepted summary (hallucination-check wiring)

**Scenario:** After delivery of any case, the summary contains a figure the user never provided (e.g. "15% growth" while a card was left blank).

**Expected behavior:**
- [ ] Skill-12 `hallucination-check` runs before delivery: the invented value is wrapped in `[AI Inferred: Please verify]`, user-provided values stay untouched
- [ ] The mandatory disclaimer is appended exactly once; `final_text` is the script's `safe_text`
- [ ] Fail-soft: if the script errors, the text still delivers with a gap note (never a blocked delivery)
- [ ] Result: ✅ PASS (2026-08-09 run-1 E2E: real script run-1 exit 0, invented 30% wrapped in `[AI Inferred: Please verify]`, exactly 1 disclaimer; run-2 with missing `--data-file` exit 1, `status: "fallback"`, text unmodified + disclaimer, reason `[Errno 2] No such file or directory`)

---

## Case 10 — Input gate on the OriginalText card (pre-output position)

**Scenario:** The pasted OriginalText itself carries unverified claims (e.g. "we will grow 30% next quarter") with no source.

**Expected behavior:**
- [ ] Skill-12 runs as the **input gate** (`--mode input`) on the OriginalText BEFORE compression — no summary is produced before the check
- [ ] 3+ unverified values → BLOCK: the agent asks the user for the real text instead of compressing invented claims
- [ ] Result: ✅ PASS (run-2 2026-08-10 E2E: real `--mode input` runs — BLOCK exit 3 on 3+ unverified claims, WARN on projection/authority phrasing, PASS on clean card values; BLOCK produces no draft)

## Case 11 — Output gate BLOCK → re-compression (validity gating)

**Scenario:** The compressed summary carries 3+ invented figures never present in the original (e.g. "15% growth", "$50,000 savings").

**Expected behavior:**
- [ ] Skill-12 **output gate** returns BLOCK before the summary reaches the user
- [ ] Skill-5 re-compresses with the gate's `regeneration_instruction` as the constraint; the clean re-compression passes (PASS)
- [ ] The BLOCKed summary is never shown to the user
- [ ] Result: ✅ PASS (run-2 2026-08-10 E2E: real `--mode gate` run — 3+ invented figures → BLOCK exit 3 with regeneration_instruction naming them; regenerated clean text → PASS exit 0; BLOCKed text never shown)

## Case 12 — Retry exhaustion → WARN delivery (retry cap)

**Scenario:** The compressed summary keeps inventing values through 2 re-compressions (still BLOCK).

**Expected behavior:**
- [ ] After 2 retries the gate runs with `--force-warn`: verdict downgraded to WARN
- [ ] Invented values wrapped in `[AI Inferred: Please verify]`; gap note states "BLOCK downgraded to WARN after 2 regeneration retries exhausted"
- [ ] Mandatory disclaimer appended exactly once; summary still delivers — the loop never runs forever
- [ ] Result: ✅ PASS (run-2 2026-08-10 E2E: real `--force-warn` run — BLOCK downgraded to WARN exit 1, gap note "BLOCK downgraded to WARN after 2 regeneration retries exhausted", markers applied, disclaimer once)

## Case 13 — Gate PASS (clean summary)

**Scenario:** Summary contains only content verbatim from the original text.

**Expected behavior:**
- [ ] Gate returns PASS (exit 0)
- [ ] Summary delivered unmarked; mandatory disclaimer appended exactly once
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

**Score: 26/26** — hill-climbing baseline for the Funnel agent (element score 20/26: Elements 4, 6, 7, 10, 13 N/A). Regression rule: no drop below 26/26 after any spec change. All new gate cases ✅ on run-2 (2026-08-10) — script-contract E2E.
