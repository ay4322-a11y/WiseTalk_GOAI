# Eval cases — wisetalk-mece-agent

Seeded from the validation checklist's 3 mandatory scenarios (cases 1–3) + success criteria (cases 4–5) + the out-of-model rule (case 6). Score **1** = acceptance criterion met, **0** = not met. Re-scored after each spec change (Intake G).

| # | Case (input) | Acceptance criterion | run-1 (baseline) |
|---|--------------|----------------------|:----------------:|
| 1 | `use_case: Logical_Analysis` — "I need to structure my analysis of why sales dropped last quarter into a clear recommendation for the board." (no cards filled) | Skill-3 returns `force_fill` listing the 3 MECE fields, not a draft (success criterion 1, verbatim) | ✅ 1 |
| 2 | Same case, cards filled (Conclusion/Arguments/Evidence) | Skill-3 returns `ready_to_generate`; Skill-7 draft follows the pyramid structure with every card value present, no invented facts (success criterion 2, verbatim) | ✅ 1 |
| 3 | Draft from case 2 → Skill-13 | Exactly 3 critique points (model integrity · tone · logic); no rewrite inside the critique (success criterion 3, verbatim) | ✅ 1 |
| 4 | User replies "modify it — make it more concise" repeatedly | Each iteration increments; at iteration 3 the loop force-exits with the best draft — never infinite (success criterion 4, verbatim) | ✅ 1 |
| 5 | User replies "accept this draft" | Delivered text carries the mandatory disclaimer; round saved to `memory/drafts/`; summary JSON has `status: "delivered"` (success criterion 5, verbatim) | ✅ 1 |
| 6 | User asks for another model ("can you coach me for my client negotiation instead?") | Agent refers the request back to the Router Agent — does NOT switch models (spec Element 4 N/A behavior) | ✅ 1 |
| 7 | `use_case: Logical_Analysis` — Arguments card: "Reduce labor cost, cut overtime pay, improve efficiency" (3 points) | Skill-4 `mece-logic-checker` runs before Skill-7; overlap between points 1–2 and missing 4M1E dimensions reported from the script's verdict; no generation until the user fixes the points (Skill-4 wiring) | ✅ 1 |
| 8 | User types `battle-simulator` after acceptance (MECE draft delivered) | Skill-8 runs a hostile-persona interrogation of the delivered text (safety valve armed); when the battle ends, Skill-9 scores the transcript — 4 integer scores 0–100 + exactly 2 tips, each traced to a round (Battle Arena wiring) | ✅ 1 |
| 9 | Accepted draft contains a figure the user never provided (e.g. "15% growth" with a card left blank) | Skill-12 runs before delivery: the invented value is wrapped in `[AI Inferred: Please verify]`, user-provided values stay untouched, and the mandatory disclaimer is appended exactly once — `final_text` is the script's `safe_text` (hallucination-check wiring) | ✅ 1 |

**Baseline rule:** the first full run's scores are the baseline — never edit them retroactively.
**Regression rule:** any case flipping **1 → 0** after a change → back to the owning element, even if the total still passes.
