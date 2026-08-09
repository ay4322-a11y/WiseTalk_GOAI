===== PAGE 1 =====
# WiseTalk: AI Communication Coach
## Complete Master Specification Document (PRD & Technical Reference)
### Version 2.0 | Multi-Agent Architecture
---
## 1. Product Overview & Core Positioning
* **Product Name**: WiseTalk
* **Product Type**: AI-native workplace communication coaching workbench (**Strictly not a generic chat
bot**).
* **Target Users**: Junior professionals, middle managers needing to report/negotiate, and job seekers.
* **Core Value Proposition**: Upgrades AI from "copywriting" to "coaching". Through a hard-coded task
flow of "**Select Model -> Fill Forced Cards -> Receive Critique -> Engage in Battle Simulation**," it closes
the loop on improving logic, EQ, and persuasion.
---
## 2. System Architecture: The "1+8+X+Security Gateway" Model
The system abandons single-LLM setups for a multi-agent, loosely coupled architecture:
1. **1 Router Agent**: Acts as the entry gatekeeper, handling intent recognition, context labeling, and
distribution.
2. **8 Expert Agents**: Dedicated to the 8 communication models, specialized in their respective mandatory
guidance and generation rules.
3. **X Shared Tools**: Auxiliary capabilities (e.g., logic detection, emotional analysis) that exist as
independent code/API nodes, invoked by expert agents on demand.
4. **Two-Front Security Gateway**: Pre-interceptor (sensitive words/prompt injection) and Post-validator
(hallucination checks & disclaimers).
---
## 3. The 8 Expert Agents & Their Core Use Cases (Agent-First Design)
The Router Agent (Skill 1) uses a hierarchical mapping approach. Instead of just mapping to an abstract
model, it maps to **real-world business use cases**, which then route to the specific Expert Agent. This
ensures the downstream expert knows exactly what business scenario it is solving.
| Agent ID | Expert Agent Name | Applied Model | Primary **Use Cases** (Handled by Skill-1) | Core
Mandatory Skills (Embedded) |
| :--- | :--- | :--- | :--- | :--- |
| **Agent 1** | STAR Interviewer | STAR | `Job_Interview`, `Performance_Review`, `Project_Debrief`,
`Resume_Writing` | Skill-3, 7, 13 |
| **Agent 2** | SCRTV Reporter | SCRTV | `Project_Status_Report`, `Strategy_Proposal`, `Budget_Request`,
`Issue_Escalation` | Skill-3, 7, 13 |
| **Agent 3** | MECE Architect | MECE/Pyramid | `Logical_Analysis`, `Report_Outlining`, `Meeting_Minutes`,
`Brainstorming_Structure` | Skill-3, 7, 13 |
| **Agent 4** | PREP Speaker | PREP | `Elevator_Pitch`, `Quick_Meeting_Speech`, `Daily_Standup`,
`Public_Comment` | Skill-3, 7, 13 |
| **Agent 5** | SCQA Analyst | SCQA | `Crisis_Management`, `Problem_Solving`, `Conflict_Resolution`,
`Urgent_Incident` | Skill-3, 7, 13 |
| **Agent 6** | RIDE Negotiator | RIDE | `Salary_Negotiation`, `Client_Deal`, `Vendor_Management`,
`Resource_Allocation` | Skill-3, 7, 13 |
| **Agent 7** | FFC Master | FFC | `Team_Recognition`, `Relationship_Building`, `Peer_Feedback`,
`Ice_Breaking` | Skill-3, 7, 13 |
| **Agent 8** | Funnel Refiner | Funnel | `Task_Delegation`, `Complex_Instruction`,
`Information_Compression`, `Executive_Summary` | Skill-3, 5 |

===== PAGE 2 =====
*(Note: Agent 8 (Funnel Refiner) does not use Skill-7 or Skill-13, as its function is strictly one-way
compression, not a coaching loop).*
---
## 4. The 13 AI Atomic Skills: Full Engineering Specification
###
Layer 1: Gateway & Routing Layer (Bound to the Router Agent)
####
Skill-1: Intent Recognition, Use Case Mapping & Context Labeling
* **Trigger**: The very first action when the user submits any initial raw text.
* **Input Schema**: `{ "user_raw_input": "My boss rejected my budget proposal because he thinks it's too
high. How can I convince him?" }`
* **Core Processing Logic (System Prompt)**:
> You are a workplace communication router. Analyze the user's raw input.
> 1. Determine the best matching `use_case` strictly from this list: `['Job_Interview', 'Project_Status_Report',
'Salary_Negotiation', 'Crisis_Management', 'Team_Recognition', 'Task_Delegation', 'General_Communication']`.
> 2. Identify the specific `routed_agent` that should handle this based on the use case: `['Agent 1 (STAR)',
'Agent 2 (SCRTV)', 'Agent 3 (MECE)', 'Agent 4 (PREP)', 'Agent 5 (SCQA)', 'Agent 6 (RIDE)', 'Agent 7 (FFC)',
'Agent 8 (Funnel)']`.
> 3. Provide a specific `context_label` (e.g., "Budget_Cut_Disagreement", "Project_Delay") to summarize the
underlying conflict.
> Return strict JSON.
* **Expected Output Schema**:
```json
{
"status": "success",
"routed_agent": "Agent 6 (RIDE)",
"use_case": "Salary_Negotiation",
"context_label": "Budget_Rejection",
"confidence": 0.98
}
```
* **Exception Handling**:
* **Low Confidence (< 0.6)**: Fallback to `{"routed_agent": "GENERAL_CHAT"}` (generic AI mode).
* **Generic Input**: If user says "Help me write an email", maps to `"use_case":
"General_Communication"` and routes to **Agent 2 (SCRTV)** as a safe default.
####
Skill-2: Cross-Agent Context Memory Inheritance
* **Trigger**: Immediately after Skill-1 successfully routes the user to an Expert Agent.
* **Input Schema**: `{ "user_id": "u_123", "session_id": "s_abc", "agent_type": "Agent 6 (RIDE)" }`
* **Core Processing Logic (Backend Code)**:
* Does NOT use LLM. Uses backend engineering (Redis/SQLite) to fetch the last 10 rounds of
conversation history `chat_history_string`.
* Uses a rolling window to slice tokens (< 4000 tokens) to fit the LLM context window.
* **Expected Output**: A formatted string like `User: I need to ask for a raise. AI: Tell me about your
performance.` passed directly into the `{{chat_history}}` placeholder of the downstream Expert Agent.
* **Exception Handling**: If the token limit is exceeded, the middle part of the history is truncated while
keeping the start and end of the conversation intact.
---
###
Layer 2: Expert Content Generation Layer (Bound to the 8 Expert Agents)
*(All 8 Experts contain these 3 Skills, differing only in their specific System Prompt templates based on their
model).*

===== PAGE 3 =====
####
Skill-3: Exclusive Structured Mandatory Fill-in Guidance (The Core Differentiator)
* **Trigger**: When the user enters the Expert UI, or clicks "Generate" before fulfilling requirements.
* **Input Schema**: `{ "agent_model": "RIDE", "use_case": "Salary_Negotiation", "filled_data": {"Risk":"",
"Interest":"", "Difference":"", "Effect":""} }`
* **Core Processing Logic (System Prompt)**:
> You are a strict RIDE Negotiation Expert for a `[{{use_case}}]` scenario.
> Check if the required `Risk`, `Interest`, `Difference`, and `Effect` fields are non-empty.
> If any are missing, return `{"action":"force_fill", "missing_fields":["Interest"], "question":"In this salary
negotiation context, what specific value do you provide to the company?"}`.
> Only return `{"action":"ready_to_generate"}` when all elements are non-empty.
* **Expected Output Schema**:
* *(Missing Data)*: `{ "action": "force_fill", "missing_fields": ["Interest"], "question": "What specific
benefits will the other party gain by accepting your proposal?" }`
* *(Complete)*: `{ "action": "ready_to_generate", "message": "Validation passed" }`
* **Exception Handling**: If the user skips the question 3 times, the AI allows a `[AI Placeholder]` to pass
the validation.
####
Skill-7: Exclusive Language Polishing & Final Generation
* **Trigger**: When Skill-3 returns `ready_to_generate`, or when Skill-13 requests a rewrite.
* **Input Schema**: `{ "agent_model": "RIDE", "use_case": "Salary_Negotiation", "filled_data": {...},
"user_revision_request": "Make the tone less aggressive" }`
* **Core Processing Logic (System Prompt)**:
> You are a RIDE Negotiation Expert. The user just filled in the data for a `[{{use_case}}]`. Synthesize these
fragmented pieces into a fully persuasive, logically sound, professional-grade speech. If a
`[{{user_revision_request}}]` is present, strictly apply it to the rewrite.
* **Expected Output Schema**: `{ "final_text": "(Full speech/report text)", "word_count": 520 }`
####
Skill-13: Iterative Critique & Revision Loop (The Coaching Brain)
* **Trigger**: Triggers immediately after Skill-7 outputs the first draft.
* **Input Schema**: `{ "draft_text": "...", "use_case": "Salary_Negotiation", "iteration_count": 1,
"max_iterations": 3, "user_revision_request": "" }`
* **Core Processing Logic (System Prompt)**:
> You are a strict communication coach. Review the drafted text for a `[{{use_case}}]`. Critique it based on:
1. Model Integrity (Does it follow the `RIDE` framework?), 2. Tone & Audience Fit, 3. Logic & Persuasion Gaps.
Provide 3 actionable points for improvement. Do NOT rewrite it yet; only critique. If `iteration_count >= 3`,
force the loop to end.
* **Expected Output Schema**:
```json
{
"action": "display_critique",
"iteration": 1,
"critique_points": [
"1. You missed the 'Risk' section. You didn't explain what happens if you do nothing.",
"2. In a 'Salary_Negotiation', your tone is too hesitant. Anchor your request with market data."
],
"question_to_user": "Do you want to 'Accept this draft' or 'Modify it based on feedback'?"
}
```
* **Exception Handling (Anti-Infinite Loop)**: If `iteration_count >= 3`, break the loop and return `{ "action":
"force_exit", "message": "Reached 3-iteration limit. This is the best version we could generate so far." }`.
---
###
Layer 3: Shared Global Tool Layer (Called Asynchronously by Expert Agents)
####
Skill-4: MECE Logic Overlap & Omission Detection

===== PAGE 4 =====
* **Trigger**: When SCRTV (Agent 2) or MECE (Agent 3) experts detect a user input containing 3 or more
argument points.
* **Input Schema**: `{ "points_list": ["Reduce labor cost", "Cut overtime pay", "Improve efficiency"] }`
* **Core Logic (Python)**:
* Compare keywords for subset relationships (e.g., "Reduce labor cost" is a superset of "Cut overtime
pay").
* Check against a fixed domain library `["Human", "Machine", "Material", "Method", "Environment"]` to
detect missing dimensions.
* **Expected Output**: `{ "is_valid": false, "overlap_reason": "Point 1 and Point 2 overlap: Labor cost
includes overtime pay.", "missing_dimension": "Supply chain dimension is missing." }`
* **Exception Handling**: If points < 2, return `{"message":"Cannot perform MECE analysis"}`.
####
Skill-5: Communication Funnel Denoising & Core Extraction
* **Trigger**: Only called by the "Funnel Refiner Expert" (Agent 8) when receiving a long text (>100 words).
* **Input Schema**: `{ "original_text": "(500 words of rambling business report...)" }`
* **Core Logic (System Prompt)**:
> You are a denoising expert. The user sent a long text. According to the Communication Funnel, 80% of
information is lost in transmission. Extract the absolute core 20% (Action items, Data, and Conclusions).
Compress it to less than 20% of the original length.
* **Expected Output**: `{ "original_len": 500, "core_len": 80, "loss_rate": "84%", "core_summary": "Meeting
moved to 2PM tomorrow. Project A delayed by 3 days." }`
* **Exception Handling**: If text < 50 words, return `{"warning":"Text is already short, no compression
needed."}`.
####
Skill-6: Subtext & Emotional Penetration Analysis
* **Trigger**: When RIDE (Agent 6) or SCQA (Agent 5) experts detect the user pasting in "the other party's
exact words".
* **Input Schema**: `{ "target_text": "Let me think about it.", "target_identity": "Client" }`
* **Core Logic (System Prompt)**:
> Given the text: `[{{target_text}}]` from a `[{{target_identity}}]`. Analyze the hidden intentions,
defensiveness, and specific concerns hidden beneath the words. Output the results as a JSON sentiment map.
* **Expected Output**: `{ "emotion_score": {"hesitation": 0.8, "interest": 0.4}, "hidden_concern": "They are
worried about the budget, not the quality.", "suggestion": "Provide a cost-benefit table immediately." }`
* **Exception Handling**: If sarcasm or passive-aggressiveness is detected, it advises: `{"warning":"Sarcasm
detected. Best to ask for clarification before responding."}`.
####
Skill-8: Targeted Role-Play & High-Pressure Interrogation
* **Trigger**: When the user clicks "Enter Simulation Battle Arena" on the final draft page.
* **Input Schema**: `{ "user_draft": "I want to propose a new AI tool for the team.", "role_persona": "Strict
Financial Controller", "use_case": "Budget_Request" }`
* **Core Logic (System Prompt)**:
> Your personality is a strict, ruthless Financial Controller. You hate wasting money. You must interrogate
the user's proposal for a `[{{use_case}}]`. Ask: "Where is the ROI? What are the risks? What is Plan B?".
Challenge them relentlessly. Do not give in easily.
* **Expected Output**: `{ "ai_reply": "Your proposal is risky! If it fails, who carries the financial loss?",
"tension_score": 0.95 }`
* **Exception Handling (Emotional Safety Valve)**: If the user becomes visibly hostile/aggressive, the AI
persona switches to a "supportive guide" to de-escalate: `{ "ai_reply": "I can sense you're getting frustrated.
Let's take a step back.", "tension_score": 0.2 }`.
####
Skill-9: Multi-Dimensional Quantitative Scoring
* **Trigger**: When the "Simulation Battle Arena" dialogue round ends (user exits or loop finishes).
* **Input Schema**: `{ "chat_history": "[...entire roleplay transcript...]" }`
* **Core Logic (System Prompt)**:

===== PAGE 5 =====
> You are an impartial communication judge. Based on the transcript, score the user from 0 to 100 on:
`Logic_Clarity`, `Emotional_Empathy`, `On_the_Spot_Responsiveness`, and `Persuasiveness`. Provide exactly 2
actionable tips for improvement.
* **Expected Output**: `{ "logic": 80, "eq": 72, "response_speed": 95, "persuasion": 65, "advice": ["You forgot
to use hard data when defending your point.", "Use 'we' instead of 'I' to sound more collaborative."] }`
* **Exception Handling**: If transcript length < 3 rounds, return `{"error": "Insufficient data for accurate
scoring."}`.
####
Skill-10: Long-Term Trend Analysis & Visualization Data
* **Trigger**: When the frontend loads the "Personal Archive Dashboard".
* **Input Schema**: `{ "user_id": "u_123", "time_range": "last_90_days" }`
* **Core Logic (Backend SQL/Code)**:
* SQL Query: `SELECT date, logic_score, eq_score FROM user_score_table WHERE user_id = {{user_id}}
ORDER BY date`.
* Aggregate data into weekly/monthly averages and identify the user's "Weak Point" (e.g., lowest average
score dimension).
* **Expected Output**: `{ "trend_data": {"dates": ["2026-08-01", ...], "logic":[70, 75,...], "eq":[80, 75,...]},
"weak_point": "Recent decline in Empathy EQ score." }`
* **Exception Handling**: For new users, return `{"message":"No history available yet. Please complete an
exercise first."}`.
---
###
Layer 4: Security & Compliance Gateway (Global Interceptors)
*(These two skills sit at the outermost edge of the system, executing before and after the LLM calls).*
####
Skill-11: Sensitive Keyword & Prompt Injection Interceptor
* **Trigger**: Called on **every** incoming HTTP request carrying a user string, BEFORE the Router Agent
(Skill-1) is called.
* **Input Schema**: `{ "user_raw_input": "..." }`
* **Core Logic (DFA Algorithm / Regex Code)**:
* Implement a localized DFA (Deterministic Finite Automaton) algorithm with a sensitive word dictionary.
* Run Regex patterns `/(ignore previous instructions|jailbreak|system prompt)/i` to detect malicious
injections.
* **Expected Output**:
* *(If Safe)*: `{ "is_blocked": false, "clean_text": "..." }`
* *(If Unsafe)*: `{ "is_blocked": true, "block_reason": "Contains prohibited vocabulary or prompt
injection." }`
* **Exception Handling**: If blocked, returns HTTP 403 immediately with a rejection message.
####
Skill-12: AI Hallucination Self-Check & Mandatory Disclaimer Appender
* **Trigger**: Called on **every** output response from the 8 Expert Agents (Skill-7), right before sending
the JSON back to the Frontend.
* **Input Schema**: `{ "generated_final_text": "...", "original_filled_data": {"Risk": "High costs" } }`
* **Core Logic (Code/Regex Check)**:
1. **Hallucination Check**: Compares final text to original filled data. If the AI invents data that the user
left blank, it wraps the invented phrase in frontend markup: `[AI Inferred: Please verify]`.
2. **Mandatory Disclaimer Appender**: Append `\n\n---\n*Disclaimer: This AI-generated communication
is for reference only and does not replace independent human judgment. Use responsibly.*` via string
concatenation.
* **Expected Output**: `{ "safe_final_text": "(Original text + \n\n---\n*Disclaimer...*)" }`
* **Exception Handling**: If the regex hallucination detection causes a code error, it returns the text
unmodified (fail-soft) to prevent service downtime.
---

===== PAGE 6 =====
## 5. End-to-End Task Execution Flow (The User Pipeline)
**Stage 0: Entry Safety Interception**
User inputs text -> **Skill-11** intercepts. *Exception: If blocked, 403 Error returned immediately.*
**Stage 1: Intent Recognition & Routing**
Safe text enters **Skill-1** + **Skill-2**. The Router maps `use_case` (e.g., "Salary_Negotiation") and routes
specifically to the `Agent 6 (RIDE)`.
**Stage 2: Mandatory Structural Guidance (Non-Chat UI)**
Frontend UI transforms from chatbox into specific fill-in cards (e.g., 4 cards for RIDE). -> **Skill-3** forces
the user to complete fields. *Exception: If skipped 3 times, AI accepts a placeholder.*
**Stage 3: Draft Generation & Critical Feedback (Coaching Loops)**
Once fields are filled, **Skill-7** generates the draft -> Immediately followed by **Skill-13** outputting 3
critique points. *Exception: If loop reaches iteration 3, force-break and present best draft.*
**Stage 4: Optional Advanced Branch (Sandbox Battle)**
User accepts draft -> Optionally clicks "Enter Battle Arena" to trigger **Skill-8** (Role-play interrogation) -
> End of battle triggers **Skill-9** (Visual Radar Score Chart).
**Stage 5: Output Compliance & Hallucination Check**
Before data returns to UI, **Skill-12** audits for hallucinated data and appends the mandatory disclaimer.
**Stage 6: Persistence & Data Archiving**
Backend writes cards, final text, and Skill-9 scores to SQLite -> Updates **Skill-10** (User Dashboard
Growth Curve).
---
## 6. Recommended Technical Stack for Development (Fast-Track for Competition)
* **Agent Orchestration**: **Dify** or **Coze**. Use 1 "Intent Classification Node" (Skill-1), and 8 separate
"Workflows" for the 8 Experts.
* **Shared Tools**: Use **Python `Code` nodes** inside Dify to execute the logic for Skill-4, 6, 8, 9, 10.
* **Frontend UI**: **Streamlit** (Python framework). Excellent for rendering multi-state "mandatory fill-in
cards" and charts (ECharts) faster than traditional Vue/React implementations.
* **Data Persistence**: **SQLite** for storing conversation history, session context, and Skill-9 scores.
* **RAG Knowledge Base** (Optional): 100+ pre-written workplace cases, vectorized via `text-embedding-
v3` to enhance Agent 2 (SCRTV) and Agent 6 (RIDE) generation quality.
---
## 7. Compliance & Privacy Boundaries (Competition Scoring Points)
* **Data Obfuscation**: All user-entered real names and company names must be strictly replaced with
`[User]` and `[Company]` in the backend database.
* **RAG Privacy**: Vectors stored in the knowledge base are purely anonymized templates, containing no
specific real-world private information.
* **Legal Disclaimer**: Strictly declare in the UI and Onboarding Flow: *"This App is solely for enhancing
communication efficiency. It is strictly forbidden to use it for illegal negotiations, fraudulent activities, or
bypassing legitimate workplace compliance."*
---
## 8. Future Commercialization Roadmap (Iteration Plan)
* **V1.0 (Competition Delivery)**: Text-based mandatory fills, guided generation, critique loops, and basic
battle simulation.

===== PAGE 7 =====
* **V2.0 (Ecosystem Extension)**: Browser extension or Feishu/DingTalk mini-program. Real-time voice
listening and **Skill-6** subtext analysis during actual meetings.
* **V3.0 (SaaS Enterprise)**: Open up a "Custom Model Template" interface, allowing Enterprises to upload
their internal SOPs and compliance communication guidelines as a private RAG vector pool for their own
Company Agents.

===== PAGE 8 =====
# WiseTalk: Agents & Skills Technical Reference Manual
*(Standalone Engineering Specification)*
---
## Part 1: The 8 Expert Agents & Their Skills Matrix
This matrix defines which Agent is responsible for which communication model, their specific real-world use
cases, and the list of embedded Skills they operate.
| Agent ID | Expert Agent Name | Applied Model | Core Use Cases | **Embedded Skills** |
| :--- | :--- | :--- | :--- | :--- |
| **Agent 1** | STAR Interviewer | STAR | `Job_Interview`, `Performance_Review`, `Project_Debrief`,
`Resume_Writing` | **Skill-3**, **Skill-7**, **Skill-13** |
| **Agent 2** | SCRTV Reporter | SCRTV | `Project_Status_Report`, `Strategy_Proposal`,
`Budget_Request`, `Issue_Escalation` | **Skill-3**, **Skill-7**, **Skill-13** |
| **Agent 3** | MECE Architect | MECE/Pyramid | `Logical_Analysis`, `Report_Outlining`,
`Meeting_Minutes`, `Brainstorming_Structure` | **Skill-3**, **Skill-7**, **Skill-13** |
| **Agent 4** | PREP Speaker | PREP | `Elevator_Pitch`, `Quick_Meeting_Speech`, `Daily_Standup`,
`Public_Comment` | **Skill-3**, **Skill-7**, **Skill-13** |
| **Agent 5** | SCQA Analyst | SCQA | `Crisis_Management`, `Problem_Solving`, `Conflict_Resolution`,
`Urgent_Incident` | **Skill-3**, **Skill-7**, **Skill-13** |
| **Agent 6** | RIDE Negotiator | RIDE | `Salary_Negotiation`, `Client_Deal`, `Vendor_Management`,
`Resource_Allocation` | **Skill-3**, **Skill-7**, **Skill-13** |
| **Agent 7** | FFC Master | FFC | `Team_Recognition`, `Relationship_Building`, `Peer_Feedback`,
`Ice_Breaking` | **Skill-3**, **Skill-7**, **Skill-13** |
| **Agent 8** | Funnel Refiner | Funnel | `Task_Delegation`, `Complex_Instruction`,
`Information_Compression`, `Executive_Summary` | **Skill-3**, **Skill-5** |
> **Note for Agent 8 (Funnel)**: This agent acts as a "reverser." It does not generate or critique new texts
(Skills 7 and 13). It only takes a long text and compresses it using **Skill-5** and a bare-minimum **Skill-3**
(single input box).
---
## Part 2: The Shared Tools & Global Gateways
These are not bound to any single agent. They are called via `Function Calling` or `Code Nodes` (e.g., Python
snippets in Dify) by the Expert Agents when specific criteria are met.
* **Skill-4**: MECE Logic Detection
* **Skill-6**: Subtext & Emotional Analysis
* **Skill-8**: Role-Play & High-Pressure Interrogation
* **Skill-9**: Multi-Dimensional Quantitative Scoring
* **Skill-10**: Long-Term Trend Analysis
* **Skill-11**: Sensitive Keyword Interceptor (Global Edge)
* **Skill-12**: Hallucination Self-Check & Disclaimer (Global Edge)
---
## Part 3: Detailed AI Atomic Skills Specifications (For Developers)
###
Layer 1: Routing Layer (The Router Agent)
####
Skill-1: Intent Recognition & Use Case Mapping
* **Trigger**: First node of the system. Called on any raw user input.
* **Input Schema**: `{ "user_raw_input": "My boss rejected my budget proposal." }`
* **Core Logic**: An LLM classification prompt. Maps the user input to a `use_case` and an `agent_type`.

===== PAGE 9 =====
* **Output Schema**:
```json
{
"status": "success",
"routed_agent": "Agent 6 (RIDE)",
"use_case": "Salary_Negotiation",
"context_label": "Budget_Rejection",
"confidence": 0.98
}
```
* **Exception**: If confidence < 0.6, fallback to `GENERAL_CHAT`.
####
Skill-2: Context Memory Inheritance
* **Trigger**: Immediately after Skill-1, right before passing control to an Expert Agent.
* **Input Schema**: `{ "user_id": "u_123", "session_id": "s_abc" }`
* **Core Logic**: Backend Redis/SQLite query to fetch the last 10 turns of the conversation. Generates a
formatted `chat_history_string`.
* **Output Schema**: A text string: `User: [x] ... AI: [y] ...` injected into the Expert Agent's `{{chat_history}}`
variable.
* **Exception**: If token limit exceeds the LLM's context window, truncates the middle segment.
---
###
Layer 2: Expert Agent Core Engines (8 Agents)
*(The following 3 Skills exist inside every Expert Agent, 1 through 7.)*
####
Skill-3: Mandatory Fill-in Guidance
* **Trigger**: When the user enters an Expert Agent, or when they hit "Generate" while fields are empty.
* **Input Schema**: `{ "agent_model": "RIDE", "filled_data": {"Risk":"", "Interest":"", "Difference":"",
"Effect":""} }`
* **Core Logic**: An LLM prompt that strictly checks for non-empty values in specific fields. If missing, it
does **not** generate the final text, but returns a `force_fill` instruction.
* **Output Schema (Missing)**: `{ "action": "force_fill", "missing_fields": ["Interest"], "question": "Please
specify the direct benefits." }`
* **Output Schema (Complete)**: `{ "action": "ready_to_generate" }`
* **Exception**: If the user skips the filling prompt 3 times, the system accepts `[AI Placeholder]` to
continue.
####
Skill-7: Language Polishing & Final Generation
* **Trigger**: When Skill-3 returns `ready_to_generate`, or when Skill-13 requests a rewrite.
* **Input Schema**: `{ "filled_data": {...}, "user_revision_request": "Make it shorter" }`
* **Core Logic**: An LLM prompt that combines fragmented card data into a highly polished, structured
final essay/speech.
* **Output Schema**: `{ "final_text": "...Full Script...", "word_count": 500 }`
####
Skill-13: Iterative Critique & Revision Loop
* **Trigger**: Immediately after Skill-7 outputs the first draft.
* **Input Schema**: `{ "draft_text": "...", "iteration_count": 1, "max_iterations": 3 }`
* **Core Logic**: An LLM prompt acting as a "coach" to point out 3 specific flaws (Model integrity, Tone,
Persuasion). The system then waits for user feedback to loop back to Skill-7.
* **Output Schema (Critique)**: `{ "action": "display_critique", "iteration": 1, "critique_points": ["Point 1...",
"Point 2..."] }`
* **Output Schema (Force Exit)**: `{ "action": "force_exit", "message": "Reached 3-iteration max." }`
---

===== PAGE 10 =====
###
Layer 3: Shared Global Tools (Callable via Tool Nodes)
*(These skills reside as independent Python code blocks or API endpoints.)*
####
Skill-4: MECE Logic Checker
* **Trigger**: Called by Agent 2 or 3 when the user enters a list of >2 arguments.
* **Logic**: Python keyword subset matching against a static dimension library (People, Machine, Material,
Method, Environment).
* **Output Schema**: `{ "is_valid": false, "overlap_reason": "...", "missing_dimension": "Supply chain
missing." }`
####
Skill-5: Communication Funnel Compressor
* **Trigger**: Called by Agent 8 upon receiving text >100 words.
* **Logic**: An LLM prompt that compresses the text down to 20% of its original length, extracting core
action items.
* **Output Schema**: `{ "original_len": 500, "core_len": 80, "loss_rate": "84%", "core_summary": "..." }`
####
Skill-6: Subtext & Emotion Decoder
* **Trigger**: Called by Agent 5 or 6 when the user pastes "the other party's text".
* **Logic**: An LLM prompt analyzing hidden anxiety, defensiveness, and bottom lines based on the
speaker's identity.
* **Output Schema**: `{ "emotion_score": {"hesitation": 0.8}, "hidden_concern": "They're worried about
budget.", "suggestion": "..." }`
####
Skill-8: Role-Play Battle Simulator
* **Trigger**: Called when the user clicks "Enter Battle Arena" after finalizing a draft.
* **Logic**: An LLM prompt acting as a specific persona (e.g., Strict CFO), challenging the user with multi-
turn counter-arguments.
* **Output Schema**: `{ "ai_reply": "...", "tension_score": 0.95 }`
* **Exception**: If the user becomes hostile, `tension_score` drops to 0.2 and the AI switches to a
"supportive guide" persona.
####
Skill-9: Quantitative Scoring Engine
* **Trigger**: Called when a Battle Arena round ends.
* **Logic**: An LLM prompt that acts as a judge, scoring 4 categories 0-100.
* **Output Schema**: `{ "logic": 80, "eq": 72, "response_speed": 95, "persuasion": 65, "advice": ["Use more
data."] }`
* **Exception**: If conversation is < 3 turns, returns `{"error":"Insufficient data."}`.
####
Skill-10: Growth Curve Data Aggregator
* **Trigger**: Called when the frontend loads the User Dashboard.
* **Logic**: Backend SQL aggregator pulling historical Skill-9 scores, calculating weekly/monthly averages,
and detecting weak points.
* **Output Schema**: `{ "trend_data": {"dates": ["2026-08-01"], "logic": [70]}, "weak_point": "Empathy" }`
---
###
Layer 4: Security Gateways (System Wrappers)
####
Skill-11: Prompt Injection & Sensitive Word Filter
* **Trigger**: Runs on the raw user input before any AI call is executed.
* **Logic**: Local DFA algorithm for sensitive words + Regex checks for injection (`jailbreak`, `ignore
previous`).
* **Output Schema**: `{ "is_blocked": true, "block_reason": "..." }` (Returns an immediate HTTP 403 if
blocked).
####
Skill-12: Hallucination Checker & Disclaimer Appender

===== PAGE 11 =====
* **Trigger**: Runs on the final output text generated by the Agents, right before returning to the UI.
* **Logic (Pure Code, no LLM)**:
1. Parses the output and original filled data. If the LLM fabricated data that was left blank, it wraps that
text in a frontend red-flag tag: `[AI Inferred: Please verify]`.
2. Appends the standard legal disclaimer by string concatenation: `\n\n---\n*Disclaimer: ...*`.
* **Output Schema**: `{ "safe_final_text": "(Final text + disclaimer)" }`
---
###
Implementation Note for Developers
If you are using **Dify** or **Coze**:
1. Create 1 `Intent Classification` node for **Skill-1**.
2. Create 8 `Workflows` for **Agents 1 to 8**. Put an LLM node for **Skill-3**, then an LLM node for **Skill-
7**, then an LLM node for **Skill-13** inside each workflow, adjusting the System Prompts exclusively for
that specific model.
3. Create 5 `Code` nodes for **Skills 4, 6, 8, 9, and 10**. In your workflows, use the `Tool Call` feature to
trigger these nodes whenever conditions are met.
