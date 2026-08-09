# Memory Index — WiseTalk Router Agent

Conversation history records used by Skill-2 (`context-memory`) for cross-agent context inheritance.

## Content Map

| File | Content | Last Updated |
|------|---------|-------------|
| chat-history.md | Rolling conversation history — last 10 rounds, < 4000 tokens (Skill-2 source, Element 14 target) | — |

## Retrieval rule

On every invocation, read `chat-history.md` to build the `chat_history_string` via Skill-2.
After every invocation, append the new turn and prune to the 10-round rolling window (Element 14).

## Privacy rule

User identity is stored as `[User]` and organizations as `[Company]` — never real names or company names (WiseTalk compliance §7).
