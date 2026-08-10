# WiseTalk Agent Routing Map

The **single source of truth** for mapping user intent → use case → Expert Agent in the WiseTalk system.
Read by Skill-1 (`intent-routing`) at classification time. Update this file to change routing behavior — never edit the classification prompt itself.

> Source: *WiseTalk: Agents & Skills Technical Reference Manual* (Parts 1–2) — Agent IDs, model names, and use-case taxonomies are verbatim.

## The 8 Expert Agents

| Agent ID | Expert Agent Name | Applied Model | Use Cases (Handled by Skill-1) |
|----------|-------------------|---------------|--------------------------------|
| Agent 1 | STAR Interviewer | STAR | `Job_Interview`, `Performance_Review`, `Project_Debrief`, `Resume_Writing` |
| Agent 2 | SCRTV Reporter | SCRTV | `Project_Status_Report`, `Strategy_Proposal`, `Budget_Request`, `Issue_Escalation` |
| Agent 3 | MECE Architect | MECE/Pyramid | `Logical_Analysis`, `Report_Outlining`, `Meeting_Minutes`, `Brainstorming_Structure` |
| Agent 4 | PREP Speaker | PREP | `Elevator_Pitch`, `Quick_Meeting_Speech`, `Daily_Standup`, `Public_Comment` |
| Agent 5 | SCQA Analyst | SCQA | `Crisis_Management`, `Problem_Solving`, `Conflict_Resolution`, `Urgent_Incident` |
| Agent 6 | RIDE Negotiator | RIDE | `Salary_Negotiation`, `Client_Deal`, `Vendor_Management`, `Resource_Allocation` |
| Agent 7 | FFC Master | FFC | `Team_Recognition`, `Relationship_Building`, `Peer_Feedback`, `Ice_Breaking` |
| Agent 8 | Funnel Refiner | Funnel | `Task_Delegation`, `Complex_Instruction`, `Information_Compression`, `Executive_Summary` |

> **Agent 8 note:** The Funnel Refiner is a "reverser" — it compresses long text (Skill-5), it does not run the coaching loop (no Skill-7/Skill-13). Route compression requests here; route coaching requests elsewhere.

## Use-Case → Agent quick map (the 32 valid `use_case` values)

| Use Case | Routed Agent |
|----------|--------------|
| `Job_Interview` · `Performance_Review` · `Project_Debrief` · `Resume_Writing` | Agent 1 (STAR) |
| `Project_Status_Report` · `Strategy_Proposal` · `Budget_Request` · `Issue_Escalation` | Agent 2 (SCRTV) |
| `Logical_Analysis` · `Report_Outlining` · `Meeting_Minutes` · `Brainstorming_Structure` | Agent 3 (MECE) |
| `Elevator_Pitch` · `Quick_Meeting_Speech` · `Daily_Standup` · `Public_Comment` | Agent 4 (PREP) |
| `Crisis_Management` · `Problem_Solving` · `Conflict_Resolution` · `Urgent_Incident` | Agent 5 (SCQA) |
| `Salary_Negotiation` · `Client_Deal` · `Vendor_Management` · `Resource_Allocation` | Agent 6 (RIDE) |
| `Team_Recognition` · `Relationship_Building` · `Peer_Feedback` · `Ice_Breaking` | Agent 7 (FFC) |
| `Task_Delegation` · `Complex_Instruction` · `Information_Compression` · `Executive_Summary` | Agent 8 (Funnel) |

## Fallback rules (mandatory — three-band confidence model)

1. **High confidence (≥ 0.6):** route to the chosen Expert Agent normally. `status` = `success`.
2. **Borderline confidence (0.4 ≤ c < 0.6, with a workplace signal):** do NOT degrade silently. Return `status` = `clarify_intent` with the **top 2 candidate agents** (each with `agent`, `use_case`, `confidence`, `explanation`) and a `question_to_user` so the client disambiguates. This replaces the old behavior where borderline input fell to `GENERAL_CHAT` with no Expert Agent triggered.
3. **Low confidence (< 0.4) or clearly non-workplace input:** route to `GENERAL_CHAT` (generic AI mode; no Expert Agent). `use_case` = `General_Communication`, `status` = `fallback`.
4. **Generic input** (no specific communication model fits — e.g. "help me write an email") → default to **Agent 2 (SCRTV)** with `use_case` = `General_Communication`, `confidence` = 0.5, `status` = `weak_guess` — the default is disclosed as a guess, never presented as a confident match.
5. **Named constants:**
   - `CONFIDENCE_THRESHOLD = 0.6` (high band floor)
   - `CLARIFICATION_BAND_LOW = 0.4` (borderline band floor)
   - Max `CLARIFICATION_ROUNDS = 2` — after 2 unresolved clarification rounds, fall back to the highest-confidence candidate and disclose that routing is uncertain.
   If a constant needs tuning, change it here and in Skill-1's rules; never in the agent body.

## Versioning

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-08-09 | Initial — all 8 agents and 32 use cases from the WiseTalk spec |
| 1.1 | 2026-08-10 | Three-band confidence model — borderline (0.4–0.6) returns `clarify_intent` with top 2 candidates instead of falling to `GENERAL_CHAT`; generic default marked `weak_guess` |
