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

## Fallback rules (mandatory)

1. **Low confidence:** classification confidence < **0.6** → route to `GENERAL_CHAT` (generic AI mode; no Expert Agent). `use_case` = `General_Communication`.
2. **Generic input** (no specific communication model fits — e.g. "help me write an email") → default to **Agent 2 (SCRTV)** with `use_case` = `General_Communication`, `confidence` = 0.5.
3. **Confidence threshold constant:** `CONFIDENCE_THRESHOLD = 0.6` — if this needs tuning, change it here and in Skill-1's rules; never in the agent body.

## Versioning

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-08-09 | Initial — all 8 agents and 32 use cases from the WiseTalk spec |
