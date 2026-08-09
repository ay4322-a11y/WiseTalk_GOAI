# Memory Index — MECE Architect (Agent 3)

Draft history, critique rounds, and user preferences for the MECE coaching loop (Elements 3, 14).

## Content Map

| File / dir | Content | Last Updated |
|------------|---------|-------------|
| drafts/ | Final drafts per use case — filled cards + final text + critique points (`<use-case>-v<N>.md`), newest per use case kept | — |

## Retrieval rule

Before coaching, check `drafts/` for prior rounds of the current use case — the user's previous cards and preferences are the starting context for a follow-up session.

## Update rule

After delivering, save one round per delivery: filled cards, final text, critique points, and the user's accept/modify choices. Keep only the most recent version per use case. Append-on-success, prune old versions.

## Privacy rule

User identity is stored as `[User]` and organizations as `[Company]` — never real names or company names (WiseTalk compliance §7). Never store secrets or raw PII.
