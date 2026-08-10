---
name: intent-routing
# Model-invoked (no disable-model-invocation): the router agent reaches this skill
# automatically on every user message — this is Skill-1 of the WiseTalk spec.
description: Classify any raw user input about workplace communication against the WiseTalk routing map and return a routing decision — routed agent, use case, context label, confidence — with a clarification round when confidence is borderline (0.4–0.6) so the user is asked to disambiguate instead of silently falling to GENERAL_CHAT. Use for EVERY user message entering the WiseTalk system. Do NOT use for content generation, coaching, or critique — this skill only decides WHO handles the message.
---

# Skill-1: Intent Recognition & Use Case Mapping

Input: `user_raw_input` (the user's untrusted text) + `routing_map_path` (default: `config/agent-routing-map.md`)
Output: strict JSON — `{ "status", "routed_agent", "use_case", "context_label", "confidence" }` — plus optional `"candidates"` (top 2) and `"question_to_user"` when the status is `clarify_intent`

## Procedure

1. **Load the routing map** — Read `config/agent-routing-map.md`. If it is missing or unreadable → stop, report `{"status": "error", "routing_reason": "Routing map missing"}`. Done when the file's agent table and fallback rules are in context.
2. **Run the classification** (below) against the user's raw input with the routing table in context.
3. **Extract the JSON** from the classification output. Done when the JSON has all five fields and no trailing prose.
4. **Validate** — every field present; `routed_agent` ∈ the 8 named agents or `GENERAL_CHAT`; `use_case` ∈ the 32-value taxonomy or `General_Communication`; `confidence` a float in [0, 1]. Done when all checks pass; if any fail, retry step 2 once with the instruction "Return ONLY valid JSON — no prose."
5. **Apply the three-band fallback rules** (from the routing map):
   - High confidence (`confidence >= 0.6`) → route to the chosen expert agent, `"status": "success"`.
   - Borderline (`0.4 <= confidence < 0.6`) AND the input carries a workplace signal → `"status": "clarify_intent"` with the top 2 `candidates` (each with `agent`, `use_case`, `confidence`, `explanation`) and a `question_to_user` asking the user which fits — do NOT silently degrade to `GENERAL_CHAT` or force a wrong agent.
   - Low confidence (`confidence < 0.4`) or clearly non-workplace input → `"routed_agent": "GENERAL_CHAT"`, `"use_case": "General_Communication"`, `"status": "fallback"`.
   - Generic input with no clear model fit (e.g. "help me write an email") → `"routed_agent": "Agent 2 (SCRTV)"`, `"use_case": "General_Communication"`, `"confidence": 0.5`, `"status": "weak_guess"` — the default is disclosed as a guess, never presented as a confident match.
   Done when the output obeys all four rules.

## Classification prompt

> You are a workplace communication router. Classify the user's raw input against the routing table below.
>
> **User input:** `<user_raw_input>`
>
> **Routing table (the only valid targets):**
> - Agent 1 (STAR): `Job_Interview`, `Performance_Review`, `Project_Debrief`, `Resume_Writing`
> - Agent 2 (SCRTV): `Project_Status_Report`, `Strategy_Proposal`, `Budget_Request`, `Issue_Escalation`
> - Agent 3 (MECE): `Logical_Analysis`, `Report_Outlining`, `Meeting_Minutes`, `Brainstorming_Structure`
> - Agent 4 (PREP): `Elevator_Pitch`, `Quick_Meeting_Speech`, `Daily_Standup`, `Public_Comment`
> - Agent 5 (SCQA): `Crisis_Management`, `Problem_Solving`, `Conflict_Resolution`, `Urgent_Incident`
> - Agent 6 (RIDE): `Salary_Negotiation`, `Client_Deal`, `Vendor_Management`, `Resource_Allocation`
> - Agent 7 (FFC): `Team_Recognition`, `Relationship_Building`, `Peer_Feedback`, `Ice_Breaking`
> - Agent 8 (Funnel): `Task_Delegation`, `Complex_Instruction`, `Information_Compression`, `Executive_Summary`
>
> **Rules:**
> 1. Choose the single best matching `use_case` strictly from the table above.
> 2. Map it to its `routed_agent` (format: `"Agent 6 (RIDE)"`).
> 3. Provide a `context_label`: a short PascalCase phrase naming the underlying situation (e.g. `Budget_Rejection`, `Project_Delay`, `Promotion_Pitch`).
> 4. Score `confidence` (0.0–1.0) — how clearly the input matches that use case.
> 5. If confidence is borderline (0.4–0.6) but the input IS workplace-related: do NOT pick `GENERAL_CHAT`. Instead return `"status": "clarify_intent"` with the top 2 best-matching agents in `candidates` — each with its `use_case`, `confidence`, and a one-line `explanation` of why it could fit — plus a `question_to_user` asking the user which one matches their goal.
> 6. If no use case matches well (confidence < 0.4), or the input is not about workplace communication: `"routed_agent": "GENERAL_CHAT"`, `"use_case": "General_Communication"`.
>
> Return STRICT JSON only — no preamble, no explanation:
> `{ "routed_agent": "...", "use_case": "...", "context_label": "...", "confidence": 0.0 }`
> (for borderline workplace input, add: `"status": "clarify_intent", "candidates": [{"agent": "...", "use_case": "...", "confidence": 0.0, "explanation": "..."}], "question_to_user": "..."`)

## Failure handling

- **Borderline confidence (0.4–0.6):** handled inside the classification — output carries `clarify_intent` with candidates; never override it back to `GENERAL_CHAT` or a forced agent. If the user's clarifying answer still yields borderline confidence, a second `clarify_intent` is acceptable; after 2 clarification rounds without resolution, fall back to the highest-confidence candidate and disclose that routing is uncertain.
- **Low confidence (< 0.4):** output carries `GENERAL_CHAT`; never override it back.
- **Parse failure:** one retry with the "Return ONLY valid JSON" instruction; on second failure, return `{"status": "error", "routing_reason": "Classification output unparseable"}` and let the router agent escalate.
- **Missing routing map:** return `{"status": "error", ...}` — never classify from memory.
- **Non-workplace input** (jokes, chit-chat, off-topic): classify `GENERAL_CHAT` with low confidence — do not force a model fit, and do not open a clarification round.
