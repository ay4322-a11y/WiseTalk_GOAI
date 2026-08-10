# WiseTalk — Workplace Communication Coaching Workbench

WiseTalk is an AI-native workplace communication coaching system. It helps users draft, critique, and improve workplace communications using 8 proven communication models: STAR, SCRTV, MECE, PREP, SCQA, RIDE, FFC, and Funnel. The system is a **coaching loop** — Select Model → Fill Mandatory Cards → Receive Critique → Battle Simulation — not a generic chatbot.

## When to route to WiseTalk

Route the user's message to the `wisetalk-router-agent` when any of these are true:

- The user describes a workplace communication scenario (interview, performance review, report, proposal, budget request, pitch, negotiation, feedback, recognition, delegation, crisis response, conflict)
- The user asks for help drafting or improving a work message, email, presentation, or speech
- The user asks how to communicate better at work, or describes a difficult conversation or persuasion challenge in a professional context
- The user mentions a communication framework (STAR, SCRTV, MECE, PREP, SCQA, RIDE, FFC, Funnel) and wants coaching in it

Do NOT route to WiseTalk when:

- The user asks general questions unrelated to workplace communication
- The user asks about code, system configuration, or how WiseTalk itself works (that's this project's engineering work — read the spec in `_wisetalk_extracted.md`)
- The user is chit-chatting or making small talk

## How to route

Use the Agent tool to invoke `wisetalk-router-agent`. It classifies the need against the routing map (32 use cases × 8 experts) and dispatches to the correct Expert Agent with conversation context. The router never generates content itself.

## Available agents

| Agent | Model | Use cases |
|-------|-------|-----------|
| `wisetalk-router-agent` | Router | Intent classification & dispatch (entry gatekeeper) |
| `wisetalk-star-agent` | STAR | Job Interview · Performance Review · Project Debrief · Resume Writing |
| `wisetalk-scrtv-agent` | SCRTV | Status Report · Strategy Proposal · Budget Request · Issue Escalation |
| `wisetalk-mece-agent` | MECE | Logical Analysis · Report Outlining · Meeting Minutes · Brainstorming |
| `wisetalk-prep-agent` | PREP | Elevator Pitch · Quick Speech · Daily Standup · Public Comment |
| `wisetalk-scqa-agent` | SCQA | Crisis Management · Problem Solving · Conflict Resolution · Urgent Incident |
| `wisetalk-ride-agent` | RIDE | Salary Negotiation · Client Deal · Vendor Management · Resource Allocation |
| `wisetalk-ffc-agent` | FFC | Team Recognition · Relationship Building · Peer Feedback · Ice Breaking |
| `wisetalk-funnel-agent` | Funnel | Task Delegation · Complex Instruction · Information Compression · Executive Summary |

## Project structure

- Master spec: `_wisetalk_extracted.md` (the authoritative pipeline: injection filter → routing → fill-in cards → **hallucination-gated generation** → critique → battle → delivery wrap)
- Agent definitions: `agents/wisetalk-*-agent/` (each has its own `claude-code/` workspace)
- Shared skills library: `skills-library/` (canonical source — edit skills here, never in agent copies)
- Sync skills to agents: `python skills-library/sync.py --all` (run after any library skill edit)
- Templates: `templates/` (build-system docs for adding new agents)
