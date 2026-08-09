# Skills Library — WiseTalk Shared Tools

The 8 skills in this library are the **shared capability layer of the WiseTalk system** — the "X" in the 1+8+X+Security architecture. Each is a complete, deterministic, tested skill (WiseTalk Skills 4–12), stored once here and copied into the agents that use them at build time.

## Index

| Skill | WiseTalk # | Description | Tags | Origin agent | Saved |
|-------|-----------|-------------|------|--------------|-------|
| [mece-logic-checker](mece-logic-checker/SKILL.md) | Skill-4 | Deterministic MECE check on argument points — keyword overlap between points and missing 4M1E dimensions | mece, logic, structure, quality | wisetalk-mece-agent | 2026-08-09 |
| [subtext-emotion](subtext-emotion/SKILL.md) | Skill-6 | Decode the other party's hidden intentions and concerns from their exact words — JSON sentiment map with a suggestion | subtext, emotion, negotiation, sentiment | wisetalk-scqa-agent, wisetalk-ride-agent | 2026-08-09 |
| [battle-simulator](battle-simulator/SKILL.md) | Skill-8 | Enter the Simulation Battle Arena — relentless role-play interrogation of the accepted draft by a strict persona, with an emotional safety valve | battle, roleplay, interrogation, persona, practice | all 8 expert agents | 2026-08-09 |
| [battle-scoring](battle-scoring/SKILL.md) | Skill-9 | Score a completed battle transcript — impartial 0–100 judgment on logic, EQ, responsiveness, persuasion + exactly 2 tips | battle, scoring, judge, feedback, radar | all 8 expert agents | 2026-08-09 |
| [injection-filter](injection-filter/SKILL.md) | Skill-11 | Prompt-injection & sensitive-keyword interceptor on every incoming user message before routing — deterministic DFA + regex filter, fail-closed, blocks with the spec's verbatim reason | injection, security, filter, block, gateway | wisetalk-router-agent | 2026-08-09 |
| [hallucination-check](hallucination-check/SKILL.md) | Skill-12 | Post-validator on every accepted draft before delivery — wraps invented numeric claims in the AI-Inferred marker and appends the mandatory disclaimer, fail-soft | hallucination, disclaimer, verify, security, fail-soft | all 8 expert agents | 2026-08-09 |
| [growth-trends](growth-trends/SKILL.md) | Skill-10 | Aggregate battle-score history into weekly/monthly growth trends — deterministic bucket averages + weak-point detection, graceful empty-history (user-invoked: type `growth-trends`) | trends, growth, dashboard, weak-point, aggregate | wisetalk-router-agent | 2026-08-09 |
| [funnel-compression](funnel-compression/SKILL.md) | Skill-5 | Compress a long text to less than 20% of its length — extract the absolute core (action items, data, conclusions), preserve deadlines verbatim, report loss_rate | compression, funnel, denoise, summarization | wisetalk-funnel-agent | 2026-08-10 |

## How the skills are used

Each skill is copied into the agents that need it at build time:

| Skill | Copied into |
|-------|-------------|
| mece-logic-checker | wisetalk-mece-agent |
| subtext-emotion | wisetalk-scqa-agent, wisetalk-ride-agent |
| battle-simulator | all 8 expert agents |
| battle-scoring | all 8 expert agents |
| growth-trends | wisetalk-router-agent |
| injection-filter | wisetalk-router-agent |
| hallucination-check | all 8 expert agents |
| funnel-compression | wisetalk-funnel-agent |

**Security architecture note:** the two security skills sit at opposite ends of every request. `injection-filter` (Skill-11) is the **pre-interceptor** — it checks every incoming user message before routing. `hallucination-check` (Skill-12) is the **post-validator** — it runs on every accepted draft right before delivery. Together they form the Two-Front Security Gateway.

## Library skill format

Each skill folder follows the same skeleton (frontmatter `name` + `description` written as a trigger rule, Input/Output, `## Procedure`, `## Failure handling`). A skill folder may carry **sibling files** — reference or scripts the procedure points at (`injection-filter/scripts/dfa-filter.py`, `hallucination-check/scripts/hallucination-detect.py`, `growth-trends/scripts/aggregate-scores.py`, `mece-logic-checker/scripts/mece-check.py`). Copy the whole folder, siblings included.

The WiseTalk build process keeps the library version and the per-agent copies in sync: the agent's copy is the same skill with the model's fields baked in; this library is the canonical source of the shared logic.
