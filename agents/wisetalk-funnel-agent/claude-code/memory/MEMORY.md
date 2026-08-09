# Memory Index — Funnel Refiner (Agent 8)

Compression history, verification rounds, and user preferences for the Funnel pipeline (Elements 3, 14).

## Content Map

| File / dir | Content | Last Updated |
|------------|---------|-------------|
| drafts/ | Compressed summaries per use case — original length + summary + loss_rate (`<use-case>-v<N>.md`), newest per use case kept | — |

## Retrieval rule

Before compressing, check `drafts/` for prior rounds of the current use case — the user's previous texts, summaries, and preferences are the starting context for a follow-up session.

## Update rule

After delivering, save one round per delivery: use case, original length, compressed summary, loss_rate, and the user's accept/revision choices. Keep only the most recent version per use case. Append-on-success, prune old versions.

## Privacy rule

User identity is stored as `[User]` and organizations as `[Company]` — never real names or company names (WiseTalk compliance §7). Never store secrets or raw PII.
