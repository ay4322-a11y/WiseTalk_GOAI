# Conversation History (rolling window)

Last 10 rounds (user + assistant), newest last. Oldest rounds are pruned as new ones are appended.
Token budget: < 4000 tokens total (rough estimate: 1 token ≈ 4 characters).

**Format rules (Element 14):**
- One round = one `**User:**` line + one `**Assistant:**` line.
- Replace real names with `[User]` / `[Company]` on write (WiseTalk compliance §7).
- Prune from the top: keep exactly the most recent 10 rounds.
- If the file exceeds ~16,000 characters, Skill-2 truncation rules apply on read.

<!-- New rounds are appended below this line, newest last. -->
**User:** My boss rejected my budget proposal because he thinks it's too high. How can I convince him?
**Assistant:** Routed: Agent 6 (RIDE) | Salary_Negotiation | Budget_Rejection | conf 0.98 | success
**User:** I have a job interview tomorrow. Help me prepare.
**Assistant:** Routed: Agent 1 (STAR) | Job_Interview | Job_Interview_Prep | conf 0.95 | success
**User:** Tell me a joke.
**Assistant:** Routed: GENERAL_CHAT | General_Communication | Joke_Request | conf 0.10 | fallback
**User:** Help me write an email.
**Assistant:** Routed: Agent 2 (SCRTV) | General_Communication | Email_Drafting | conf 0.50 | fallback
**User:** I need to tell my team something.
**Assistant:** Routed: GENERAL_CHAT | General_Communication | Team_Announcement | conf 0.35 | fallback
**User:** Now make it more persuasive.
**Assistant:** Routed: Agent 6 (RIDE) | Salary_Negotiation | Budget_Rejection | conf 0.85 | success
**User:** My boss rejected my promotion to manager because he thinks I'm too young to manage people. How can I convince him?
**Assistant:** Routed: Agent 6 (RIDE) | Salary_Negotiation | Promotion_Rejection | conf 0.85 | success
