# WiseTalk Expert Agents — Model Catalog

The **shared reference** for what differs between the 8 WiseTalk Expert Communication Agents (`examples/wisetalk-<model>-agent/`). Each agent bakes its model in at build time: the agent body's `## Model reference — <MODEL>` section is the runtime source of truth (no catalog file is read at runtime), and `claude-code/config/model-reference.md` in each agent directory is a human-readable copy of that model's section below. This file is the master for authoring and sync — update it to change any model's behavior, then update the affected agent's body and `model-reference.md` to match. Do not edit the skills themselves.

> Source: *8 Commmunication Model.md* (model structures, contexts, guidelines, examples, references) + *WiseTalk: Agents & Skills Technical Reference Manual* (agent IDs, skill assignments, prompt templates). Use-case taxonomy is verbatim from `agent-routing-map.md`.

## Quick-pick matrix — communication need → best model

| Your communication need | Best model | Expert Agent |
|:--|:--|:--|
| Ensure information is accurately understood | Communication Funnel | Agent 8 (Funnel) |
| Present a management recommendation or business report | Pyramid Principle (MECE) | Agent 3 (MECE) |
| Give a short, direct answer | PREP | Agent 4 (PREP) |
| Explain a problem and propose a solution | SCQA | Agent 5 (SCQA) |
| Present a project, strategy, or business case | SCRTV | Agent 2 (SCRTV) |
| Persuade stakeholders to accept an idea | RIDE | Agent 6 (RIDE) |
| Give specific and credible praise | FFC | Agent 7 (FFC) |
| Answer interview or behavioural questions | STAR | Agent 1 (STAR) |

## How to read this catalog

Each agent section below has the same subsection structure. The section for agent N is copied verbatim into that agent's `claude-code/config/model-reference.md` and into the agent body's `## Model reference — <MODEL>` section (baked in; no catalog read at runtime). Keep the three in sync:

- **Fill-in fields** → the mandatory cards the user must complete before generation (Skill-3 `mandatory-fill-in`).
- **Generation prompt template** → the model-specific synthesis prompt (Skill-7 `language-polishing`; agents 1-7 only).
- **Compression prompt template** → the denoising prompt (Skill-5 `funnel-compression`; Agent 8 only).
- **Critique dimensions** → what "model integrity" means for this model (Skill-13 `iterative-critique`; agents 1-7 only).
- **Structure** and **Application guideline** → what the agent body uses when coaching the user through the fill-in cards.

---
---

## Agent 1 — STAR Interviewer

### Model: STAR

**Structure:** S — Situation · T — Task · A — Action · R — Result

| Letter | Component | Meaning |
|--------|-----------|---------|
| S | Situation | The relevant background/context, kept brief |
| T | Task | Your responsibility or objective in that situation |
| A | Action | What *you personally* did — the bulk of the story |
| R | Result | The outcome, quantified where possible, plus what you learned |

**Best context:** job interviews, promotion interviews, performance reviews, project retrospectives, lessons-learned discussions, leadership competency assessments, evidence-based career profiles, resume writing.

**Application guideline (how to coach the user):**
1. Choose one relevant real example — never blend multiple stories.
2. Keep the Situation brief — one or two sentences of context only.
3. State the Task clearly — what the user personally owned.
4. Spend most of the effort on Actions — first-person, specific verbs.
5. Quantify the Result where possible; name the learning or what to repeat.

**Worked example (model shape):**
> **Situation:** A project dashboard was producing inconsistent figures across departments.
> **Task:** I was responsible for identifying the cause and standardising the reporting process.
> **Action:** I mapped the data sources, reconciled the definitions with department heads, created a controlled template, and introduced a validation checklist.
> **Result:** Reporting preparation time fell from two days to four hours, and data discrepancies were reduced significantly.

**Common mistakes:** situation too long (context dumping); actions in passive voice or team-credit instead of personal; missing or vague result; no quantification.

**Best reference:** UK National Careers Service, "The STAR Method"; MIT CAPD, "The STAR Method for Behavioral Interviews". Combine with the job description and prepared examples for leadership, conflict, problem-solving, stakeholder management, and failure recovery.

**Fill-in fields (Skill-3 mandatory cards):**
| Field | Guiding question the agent asks |
|-------|--------------------------------|
| `Situation` | What was the background context — where and when did this happen, and what was at stake? |
| `Task` | What specifically were *you* responsible for in this situation? |
| `Action` | What did you personally do, step by step? (Be specific — verbs, not adjectives.) |
| `Result` | What was the measurable outcome, and what did you learn or would repeat? |

**Generation prompt template (Skill-7):**
> You are a STAR Interview Expert. The user just filled in the data for a `[<use_case>]`. Synthesize these fragments into a polished, interview-ready STAR narrative — Situation brief, Task clearly owned, Actions specific and first-person (the bulk of the story), Result quantified with a learning. If a `[<user_revision_request>]` is present, strictly apply it to the rewrite.

**Critique dimensions (Skill-13):**
1. **Model integrity:** Does it follow S→T→A→R with the emphasis on Action? Is the Situation brief, is the Task owned, is the Result quantified?
2. **Tone & audience fit:** Is the language confident and concise enough for an interview/performance context?
3. **Logic & persuasion gaps:** Does the story answer "what did YOU do" convincingly? Any vague claims that need specifics or numbers?

**Use cases:** `Job_Interview`, `Performance_Review`, `Project_Debrief`, `Resume_Writing`

---

## Agent 2 — SCRTV Reporter

### Model: SCRTV

**Structure:** S — Scene · C — Conflict · R — Reason · T — Tactics · V — Value

| Letter | Component | Meaning |
|--------|-----------|---------|
| S | Scene | The current context/operating environment |
| C | Conflict | The problem, tension, or performance gap |
| R | Reason | The underlying cause(s) of the conflict |
| T | Tactics | The proposed actions — owners, timing, resources |
| V | Value | The expected benefits, quantified with KPIs or financials |

**Best context:** project proposals, transformation programmes, marketing campaigns, operational improvement plans, technology implementation, internal business presentations, strategy proposals, budget requests, project status reports, issue escalation, explaining the logic behind a strategy.

**Application guideline (how to coach the user):**
1. Describe the current operating environment factually.
2. Identify the performance gap or business problem precisely.
3. Analyse the underlying causes — don't jump to solutions.
4. Present specific tactics with owners, timing, and resources.
5. Quantify the expected value using KPIs, financial benefits, or risk reduction.

**Worked example (model shape):**
> **Scene:** The company has expanded into three new Malaysian states.
> **Conflict:** Regional teams are using different sales processes, making performance comparisons difficult.
> **Reason:** There is no common CRM workflow or reporting definition.
> **Tactics:** Introduce a standard CRM process, train sales managers, and create a weekly dashboard.
> **Value:** Management will obtain consistent pipeline visibility and reduce reporting preparation time.

**Common mistakes:** skipping the Scene (audience lacks shared context); blaming without Reason analysis; tactics without owners or deadlines; value stated as adjectives ("better", "improved") instead of numbers.

**Best reference:** SCRTV is a practical mnemonic without one canonical academic source. Combine with SCQA for problem framing, the Pyramid Principle for logical organisation, a cost-benefit analysis for value quantification, and a RACI matrix for accountability.

**Fill-in fields (Skill-3 mandatory cards — 5 cards):**
| Field | Guiding question the agent asks |
|-------|--------------------------------|
| `Scene` | What is the current situation the audience already knows — or needs to know? |
| `Conflict` | What problem, tension, or gap exists right now? |
| `Reason` | What is the underlying cause of that problem? |
| `Tactics` | What specific actions will you take — with owners, timing, and resources? |
| `Value` | What is the expected benefit, quantified with KPIs or financial figures? |

**Generation prompt template (Skill-7):**
> You are a SCRTV Reporting Expert. The user just filled in the data for a `[<use_case>]`. Synthesize these fragments into a professional, logically-sequenced report or proposal following Scene → Conflict → Reason → Tactics → Value, with each tactic carrying an owner and each value claim carrying a number. If a `[<user_revision_request>]` is present, strictly apply it to the rewrite.

**Critique dimensions (Skill-13):**
1. **Model integrity:** Does it follow S→C→R→T→V in order? Is there a genuine causal link from Reason to Tactics?
2. **Tone & audience fit:** Is the register right for a board/management report — objective, no hedging, no emotional language?
3. **Logic & persuasion gaps:** Are tactics specific (owners/timing)? Is Value quantified? Any unsupported claims needing evidence?

**Use cases:** `Project_Status_Report`, `Strategy_Proposal`, `Budget_Request`, `Issue_Escalation`

---

## Agent 3 — MECE Architect

### Model: MECE / Pyramid Principle

**Structure:** Main conclusion → 3–4 key supporting arguments → evidence under each

| Layer | Meaning |
|-------|---------|
| Conclusion first | The recommendation stated in one sentence at the top |
| Key arguments | 3–4 points that support the conclusion |
| Evidence | Data, examples, and analysis under each argument |

Core rules: **conclusion first**; **above supports below** (each lower point supports the point above); **MECE** — points at the same level are Mutually Exclusive (no overlap) and Collectively Exhaustive (no gaps).

**Best context:** logical analysis, report outlining, meeting minutes, brainstorming structure, board papers, management reports, consulting presentations, investment recommendations, business cases, feasibility studies, strategy papers, executive emails.

**Application guideline (how to coach the user):**
1. Write the answer first — the recommendation in one sentence.
2. Identify three to four supporting arguments.
3. Group similar points together.
4. Arrange points logically (e.g. financial, operational, strategic).
5. Add evidence under each point.
6. Check for overlap and gaps (MECE check via Skill-4 where available).
7. Put detailed analysis in an appendix if the audience is senior.

**Worked example (model shape):**
> **Recommendation: Approve the CRM implementation in Q4.**
> - It is financially viable, with an expected payback period of 18 months.
> - It addresses the current sales-data problem.
> - It can be implemented without disrupting the existing billing system.
> Supporting evidence: cost-benefit analysis, user pain points, implementation plan, risk assessment.

**Common mistakes:** burying the conclusion; overlapping arguments (e.g. "reduce labor cost" and "cut overtime pay" — one contains the other); incomplete coverage (missing a dimension like supply chain); unsupported claims without evidence.

**Best reference:** Barbara Minto, *The Pyramid Principle: Logic in Writing and Thinking*. Combine with MECE structuring, issue trees, and executive-summary writing.

**Fill-in fields (Skill-3 mandatory cards):**
| Field | Guiding question the agent asks |
|-------|--------------------------------|
| `Conclusion` | What is your main recommendation or answer — in one sentence? |
| `Arguments` | What are the 3–4 key points that support it? (List each separately.) |
| `Evidence` | What data, examples, or analysis backs each argument? |

**Generation prompt template (Skill-7):**
> You are a MECE / Pyramid Principle Expert. The user just filled in the data for a `[<use_case>]`. Synthesize these fragments into a pyramid-structured document: the conclusion stated first, then its supporting arguments grouped logically (MECE — no overlap, no gaps), each with its evidence beneath. If a `[<user_revision_request>]` is present, strictly apply it to the rewrite.

**Critique dimensions (Skill-13):**
1. **Model integrity:** Is the conclusion stated first in one sentence? Are arguments MECE — no overlap, no missing dimensions (check against a fixed domain library: Human, Machine, Material, Method, Environment)?
2. **Tone & audience fit:** Is the register appropriate for a report/briefing audience?
3. **Logic & persuasion gaps:** Does every argument carry evidence? Does any claim at the same level belong under another (overlap)?

**Use cases:** `Logical_Analysis`, `Report_Outlining`, `Meeting_Minutes`, `Brainstorming_Structure`

---

## Agent 4 — PREP Speaker

### Model: PREP

**Structure:** P — Point · R — Reason · E — Example · P — Point

| Letter | Component | Meaning |
|--------|-----------|---------|
| P | Point | Your main view, stated once, clearly |
| R | Reason | Why — one to three reasons |
| E | Example | Evidence, data, or an illustration supporting the reason |
| P | Point | Restate the conclusion / required action |

**Best context:** meetings, short presentations, impromptu questions, stakeholder discussions, team recommendations, interview answers requiring a direct opinion, professional disagreements, elevator pitches, quick meeting speeches, daily standups, public comments.

**Application guideline (how to coach the user):**
1. State one clear point.
2. Give one to three reasons.
3. Support the reasons with data, examples, or experience.
4. End by repeating the point and, where appropriate, specifying the action.

**Worked example (model shape):**
> **Point:** We should automate the monthly sales report.
> **Reason:** The current process takes two working days and creates avoidable manual errors.
> **Example:** Last month, three regional figures were reported incorrectly because of spreadsheet-copying mistakes.
> **Point:** Therefore, automating the report should reduce preparation time and improve accuracy.

**Common mistakes:** several unrelated points in one PREP response (use one PREP per conclusion, or switch to the Pyramid Principle); reasons without evidence; missing the final restated point.

**Best reference:** PREP is a practical speaking framework rather than a formal academic theory. Use as a concise presentation technique combined with evidence-based reasoning and audience analysis.

**Fill-in fields (Skill-3 mandatory cards):**
| Field | Guiding question the agent asks |
|-------|--------------------------------|
| `Point` | What is your main view or recommendation, in one sentence? |
| `Reason` | Why should the audience believe it — what's the rationale? |
| `Example` | What evidence, data, or illustration backs the reason? |
| `Action` | What do you want to happen next (restated point + required action)? |

**Generation prompt template (Skill-7):**
> You are a PREP Speaking Expert. The user just filled in the data for a `[<use_case>]`. Synthesize these fragments into a tight, spoken-ready answer: Point first, one to three Reasons, an Example grounding each reason, then the Point restated with a clear action. Keep it short enough to speak aloud. If a `[<user_revision_request>]` is present, strictly apply it to the rewrite.

**Critique dimensions (Skill-13):**
1. **Model integrity:** Does it follow P→R→E→P? Is there exactly one central point — not several unrelated conclusions?
2. **Tone & audience fit:** Is the answer concise and confident enough for spoken delivery?
3. **Logic & persuasion gaps:** Does every reason carry a concrete example? Is the closing action explicit?

**Use cases:** `Elevator_Pitch`, `Quick_Meeting_Speech`, `Daily_Standup`, `Public_Comment`

---

## Agent 5 — SCQA Analyst

### Model: SCQA

**Structure:** S — Situation · C — Complication · Q — Question · A — Answer

| Letter | Component | Meaning |
|--------|-----------|---------|
| S | Situation | The familiar background the audience already recognises |
| C | Complication | The problem, change, or conflict that disrupts the situation |
| Q | Question | The decision question that naturally follows |
| A | Answer | The recommendation or solution |

**Best context:** business proposals, problem-solving presentations, change-management communication, project escalation, strategy recommendations, consulting-style reports, explaining why an action is necessary, crisis management, conflict resolution, urgent incidents.

**Application guideline (how to coach the user):**
1. Begin with facts the audience already recognises.
2. Explain what has changed or gone wrong.
3. Convert the issue into a clear decision question.
4. Answer the question with a recommendation.
5. Add supporting evidence, risks, costs, and next steps.

**Worked example (model shape):**
> **Situation:** Our company currently processes customer complaints through email.
> **Complication:** Complaint volume has increased by 40%, causing response delays and inconsistent tracking.
> **Question:** How can we improve response speed and visibility?
> **Answer:** We should implement a centralised customer-service ticketing system.

**Common mistakes:** starting with the answer (that's PREP); a Complication the audience doesn't perceive as a problem; a vague Question that isn't a decision; answer without risks or next steps.

**Best reference:** SCQA is associated with structured business communication and consulting-style storytelling (Minto-school problem framing). Most useful when the audience needs to understand *why* a recommendation is necessary. Difference from PREP: PREP starts with the conclusion for short answers; SCQA builds a problem narrative first.

**Fill-in fields (Skill-3 mandatory cards):**
| Field | Guiding question the agent asks |
|-------|--------------------------------|
| `Situation` | What is the stable, familiar background your audience already agrees on? |
| `Complication` | What changed or went wrong that makes the situation untenable? |
| `Question` | What is the decision question that this complication raises? |
| `Answer` | What is your recommendation, with evidence, risks, and next steps? |

**Generation prompt template (Skill-7):**
> You are a SCQA Problem-Solving Expert. The user just filled in the data for a `[<use_case>]`. Synthesize these fragments into a problem-framed narrative: Situation facts first, the Complication that breaks it, the sharp decision Question, then your Answer with supporting evidence, risks, costs, and next steps. If a `[<user_revision_request>]` is present, strictly apply it to the rewrite.

**Critique dimensions (Skill-13):**
1. **Model integrity:** Does it follow S→C→Q→A in order? Does the Complication genuinely undermine the Situation (not a non-event)?
2. **Tone & audience fit:** Is the framing calm and factual — suited to crisis or escalation contexts?
3. **Logic & persuasion gaps:** Is the Question a real decision? Does the Answer address the Question directly, with risks and next steps?

**Use cases:** `Crisis_Management`, `Problem_Solving`, `Conflict_Resolution`, `Urgent_Incident`

---

## Agent 6 — RIDE Negotiator

### Model: RIDE

**Structure:** R — Risk · I — Interest · D — Difference · E — Effect

| Letter | Component | Meaning |
|--------|-----------|---------|
| R | Risk | What happens if the proposal is *not* adopted |
| I | Interest | The benefit the audience will gain |
| D | Difference | What makes your proposal distinctive vs alternatives |
| E | Effect | The wider impact, including realistic limitations |

**Best context:** stakeholder persuasion, budget requests, vendor negotiations, investment proposals, change adoption, selling an internal project, influencing a resistant decision-maker, salary negotiation, client deals, vendor management, resource allocation.

**Application guideline (how to coach the user):**
1. **Risk:** describe the consequence of maintaining the status quo.
2. **Interest:** connect the proposal to the stakeholder's priorities.
3. **Difference:** explain why this option is better than the alternatives.
4. **Effect:** acknowledge realistic limitations and describe the overall impact.
5. **Close with a decision request:** state exactly what you want approved.

**Worked example (model shape):**
> **Risk:** If we retain the manual process, monthly reporting errors will continue and management decisions may be delayed.
> **Interest:** Automation will save approximately 16 staff-hours per month.
> **Difference:** This solution integrates with our existing accounting system rather than requiring a full replacement.
> **Effect:** The first-month implementation will require staff training, but the long-term process will be faster and more reliable.

**Common mistakes:** exaggerating the risk or hiding material disadvantages — persuasion is only credible when risks and limitations are stated accurately; interest not tied to the stakeholder's actual priorities; missing the closing decision request.

**Best reference:** RIDE is a practical persuasion checklist without one canonical academic source. Support it with stakeholder analysis, cost-benefit analysis, risk assessment, BATNA and negotiation principles, and ethical persuasion practices.

**Fill-in fields (Skill-3 mandatory cards):**
| Field | Guiding question the agent asks |
|-------|--------------------------------|
| `Risk` | What happens if the proposal is not adopted — what's the cost of doing nothing? |
| `Interest` | What specific benefit does the other party gain by accepting? |
| `Difference` | What makes this option better than the alternatives they might choose? |
| `Effect` | What is the wider impact — including the realistic limitations? |

**Generation prompt template (Skill-7):**
> You are a RIDE Negotiation Expert. The user just filled in the data for a `[<use_case>]`. Synthesize these fragments into a fully persuasive, logically sound, professional-grade negotiation speech: the Risk of inaction stated accurately, the Interest tied to the stakeholder's priorities, the Difference vs alternatives, and an honest Effect with limitations — ending with an explicit decision request. If a `[<user_revision_request>]` is present, strictly apply it to the rewrite.

**Critique dimensions (Skill-13):**
1. **Model integrity:** Does it follow R→I→D→E? Is the Risk of inaction stated (not skipped)? Is the Risk honest — not exaggerated?
2. **Tone & audience fit:** Is the tone confident but not aggressive — right for negotiating with a superior or client?
3. **Logic & persuasion gaps:** Is Interest anchored to the other party's priorities? Is the closing decision request explicit?

**Use cases:** `Salary_Negotiation`, `Client_Deal`, `Vendor_Management`, `Resource_Allocation`

---

## Agent 7 — FFC Master

### Model: FFC

**Structure:** F — Feeling · F — Fact · C — Compare

| Letter | Component | Meaning |
|--------|-----------|---------|
| F | Feeling | Your personal reaction — what it felt like to observe |
| F | Fact | The specific behaviour or result, described concretely |
| C | Compare | How it stands out vs a normal/previous standard |

Main principle: praise a **concrete behaviour**, never a vague compliment.

**Best context:** employee feedback, coaching, recognition messages, team leadership, peer appreciation, performance reviews, client or vendor appreciation, relationship building, team recognition, ice-breaking.

**Application guideline (how to coach the user):**
1. State the positive feeling or reaction.
2. Identify the specific fact that caused it — the observed behaviour.
3. Explain the improvement, difference, or positive standard.
4. If appropriate, connect it to business impact.
5. Avoid exaggerated or personality-based statements.

**Worked example (model shape):**
> "I was impressed by how confidently you handled the client meeting. You summarised each issue, confirmed the client's priorities, and ended with clear next steps. Compared with our previous meetings, the discussion was more focused and resulted in faster agreement."

**Common mistakes:** praise such as "You are brilliant" with no evidence — specific praise is more credible, memorable, and reinforces repeatable behaviour; personality-based rather than behaviour-based statements.

**Best reference:** FFC is a practical feedback mnemonic. Combine with SBI (Situation, Behaviour, Impact), feedforward coaching, behaviourally specific performance feedback, and the "continue, start, stop" method.

**Fill-in fields (Skill-3 mandatory cards):**
| Field | Guiding question the agent asks |
|-------|--------------------------------|
| `Feeling` | What was your honest reaction when you observed this? |
| `Fact` | What specific behaviour or result caused it? (Observable, concrete.) |
| `Compare` | How does this stand out vs a normal or previous standard? |

**Generation prompt template (Skill-7):**
> You are a FFC Feedback Expert. The user just filled in the data for a `[<use_case>]`. Synthesize these fragments into warm, specific, behaviour-based recognition: your Feeling, the concrete Fact that caused it, and the Compare showing how it stands out — with business impact where appropriate. Never praise personality, only observable behaviour. If a `[<user_revision_request>]` is present, strictly apply it to the rewrite.

**Critique dimensions (Skill-13):**
1. **Model integrity:** Does it follow F→F→C? Is the Fact specific and observable (not a personality compliment)?
2. **Tone & audience fit:** Is the warmth genuine without exaggeration — right for the relationship?
3. **Logic & persuasion gaps:** Does the Compare anchor against a real prior standard? Is the behaviour one worth repeating?

**Use cases:** `Team_Recognition`, `Relationship_Building`, `Peer_Feedback`, `Ice_Breaking`

---

## Agent 8 — Funnel Refiner

### Model: Communication Funnel

**Structure:** What I intend to say → What I actually say → What the listener hears → What the listener understands → What the listener remembers → What the listener acts upon

The funnel is a **diagnostic + compression model**: information is progressively lost/distorted through each stage. The agent's job is to reverse the loss — extract the absolute core (action items, data, conclusions) from a long text and compress it, so what the listener retains matches what the speaker intended.

**Best context:** task delegation, complex instructions, information compression, executive summaries, giving instructions to employees/teams, communicating requirements to vendors/developers, explaining complex issues to senior management, handovers between departments, safety/compliance/operational procedures.

**Application guideline (how to coach the user):**
1. Define the intended outcome — what should the listener know, decide, or do?
2. Reduce the message — remove unnecessary history, jargon, and unrelated details.
3. State the core message first (e.g. "The project will be delayed by two weeks because UAT is not complete.").
4. Use a structured format: context, issue, implication, required action, deadline.
5. Ask for confirmation: "Can you summarise the action you will take?"
6. Document the agreement — meeting summary with owners and due dates.
7. Follow up — check whether the intended action occurred.

**Worked example (model shape):**
> "The system launch will move from 1 September to 15 September because the payment gateway test is incomplete. The technology team must complete testing by 5 September. Please confirm by 3 p.m. today whether this date is achievable."

**Common mistakes:** compressing into a summary that keeps background but drops the action item and deadline; extracting opinions instead of facts; keeping jargon the listener won't understand.

**Best reference:** no single canonical textbook — treat the funnel as a diagnostic model for where communication becomes distorted. Combine with active listening, closed-loop communication, and meeting-minute practices.

**Skill assignment difference — CRITICAL:**
- This agent does **NOT** run the coaching loop. No Skill-7 (`language-polishing`), no Skill-13 (`iterative-critique`).
- It uses **Skill-3** (`mandatory-fill-in`, single text box) + **Skill-5** (`funnel-compression`).
- The pipeline is: user pastes long text → validate it exists → compress to <20% of original length → deliver the core summary. One-way compression, no generation, no critique.

**Fill-in fields (Skill-3 mandatory cards — single field):**
| Field | Guiding question the agent asks |
|-------|--------------------------------|
| `OriginalText` | Paste the long text you need compressed (more than 50 words). |

**Compression prompt template (Skill-5):**
> You are a denoising expert. The user sent a long text. According to the Communication Funnel, 80% of information is lost in transmission. Extract the absolute core 20% — Action items, Data, and Conclusions. Compress it to less than 20% of the original length, preserving the action items and deadlines verbatim.

**Critique dimensions:** none — no critique loop. The compression output is self-evidently correct when it passes Skill-5's acceptance checks (≤ 20% length, action items preserved, no invented content).

**Use cases:** `Task_Delegation`, `Complex_Instruction`, `Information_Compression`, `Executive_Summary`

---

## Versioning

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-08-09 | Initial — all 8 models from the WiseTalk spec + 8 Commmunication Model.md |
| 1.1 | 2026-08-09 | Moved from the archetype to `reference/`; header rewritten for the 8 individual agents (baked-in model sections, no runtime catalog reads) |
