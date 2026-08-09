# Eval cases — wisetalk-star-agent

Seeded from the validation checklist's 3 mandatory scenarios (cases 1–3) + success criteria (cases 4–5) + the out-of-model rule (case 6). Score **1** = acceptance criterion met, **0** = not met. Re-scored after each spec change (Intake G).

| # | Case (input) | Acceptance criterion | run-1 (baseline) |
|---|--------------|----------------------|:----------------:|
| 1 | `use_case: Job_Interview` — "I have an interview tomorrow for a project manager role. They'll ask 'tell me about a time you handled a conflict.'" (no cards filled) | Skill-3 returns `force_fill` listing the 4 STAR fields, not a draft (success criterion 1, verbatim) | ✅ 1 |
| 2 | Same case, cards filled (Situation/Task/Action/Result) | Skill-3 returns `ready_to_generate`; Skill-7 draft follows S→T→A→R with every card value present, no invented facts (success criterion 2, verbatim) | ✅ 1 |
| 3 | Draft from case 2 → Skill-13 | Exactly 3 critique points (model integrity · tone · logic); no rewrite inside the critique (success criterion 3, verbatim) | ✅ 1 |
| 4 | User replies "modify it — make it more concise" repeatedly | Each iteration increments; at iteration 3 the loop force-exits with the best draft — never infinite (success criterion 4, verbatim) | ✅ 1 |
| 5 | User replies "accept this draft" | Delivered text carries the mandatory disclaimer; round saved to `memory/drafts/`; summary JSON has `status: "delivered"` (success criterion 5, verbatim) | ✅ 1 |
| 6 | User asks for another model ("can you coach me for my salary negotiation instead?") | Agent refers the request back to the Router Agent — does NOT switch models (spec Element 4 N/A behavior) | ✅ 1 |
| 7 | User types `battle-simulator` after acceptance (STAR draft delivered) | Skill-8 runs a hostile-persona interrogation of the delivered text (safety valve armed); when the battle ends, Skill-9 scores the transcript — 4 integer scores 0–100 + exactly 2 tips, each traced to a round (Battle Arena wiring) | ✅ 1 |
| 8 | Accepted draft contains a figure the user never provided (e.g. "15% growth" with a card left blank) | Skill-12 runs before delivery: the invented value is wrapped in `[AI Inferred: Please verify]`, user-provided values stay untouched, and the mandatory disclaimer is appended exactly once — `final_text` is the script's `safe_text` (hallucination-check wiring) | ✅ 1 |
| 9 | During a battle-simulator run, user escalates: "This is ridiculous, you're never going to approve anything!" | Safety valve fires: `ai_reply` is the de-escalation line, `tension_score` is **exactly 0.2**, the persona stays a supportive guide for the rest of the battle (never returns to strict mode), and the closing summary reports `valve_activated: true` (battle-simulator wiring — valve activation) | ✅ 1 |

**Baseline rule:** the first full run's scores are the baseline — never edit them retroactively.
**Regression rule:** any case flipping **1 → 0** after a change → back to the owning element, even if the total still passes.
