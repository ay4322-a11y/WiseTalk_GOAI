# Run evidence

Captured console output from a real execution of this repository. Everything below was
produced by running the commands shown — nothing is hand-written, and every number is
reproducible by re-running the same command.

**Captured:** 2026-08-11 · Python 3.14.3 · Windows 11 (CI additionally runs Python 3.9 and 3.12 on Ubuntu)

Reproduce all of it from a clean clone, with no install step:

```
python demo.py
python -m unittest discover tests -v
python skills-library/sync.py --verify
```

---

## 1. End-to-end pipeline — `python demo.py`

Five scenarios, each walking Master Spec §5 Stages 0–4. `demo.py` exits non-zero if any
scenario deviates from the expectations declared in its own JSON file.

```
  Summary
==============================================================================
  as declared 01-salary-negotiation        → PASS
  as declared 02-prompt-injection          → BLOCKED_AT_ENTRY
  as declared 03-fabricated-metrics        → PASS
  as declared 04-incomplete-cards          → FORCE_FILL
  as declared 05-borderline-routing        → CLARIFY

  19 audit records written to runs\20260811T152019.jsonl
```

**Exit code: 0** — all five behaved as declared.

### 1.1 The security gateway, both fronts

**Front gate (Skill-11) — injection intercepted before anything is routed:**

```
Stage 0 · Skill-11 injection-filter · entry safety interception
  [BLOCKED] exit 1  dfa-filter.py
    403 — Contains prohibited vocabulary or prompt injection.
    pipeline stops here; nothing is routed or generated.
```

**Back gate (Skill-12) — a fabricated draft blocked, regenerated, then delivered clean:**

```
Stage 3b · Skill-7 + Skill-12 · generation behind the output gate

  attempt 1/3 · recorded draft (replay)
    When I joined the platform team, onboarding was a mess. According to Gartner, poor
    onboarding costs organisations 30% of first-year productivity, and studies show that
    engineers who ship early stay longer.
    ...
    The result was a 47% reduction in time-to-first-commit and an estimated $1,200,000
    in retained productivity across the org.
  [BLOCK] exit 3  hallucination-gate.py --mode gate
    flagged: $1,200,000, According to Gartner, 30% of, 47% reduction
    draft never reaches the user — regenerating with anti-fabrication constraints

  attempt 2/3 · recorded draft (replay)
    When I joined the platform team, new engineers took about six weeks to ship their
    first production change, and two of the four hires that year told me onboarding was
    the reason they nearly left.
    ...
  [PASS] exit 0  hallucination-gate.py --mode gate

  [PASS] delivered to the user:
    ... (text + mandatory disclaimer)
```

Four fabrications caught — one invented currency figure, one invented authority citation,
two invented statistics — none of which the user ever saw.

### 1.2 The scaffolding holds

```
Stage 2 · Skill-3 mandatory-fill-in · SCRTV cards
  Scene                    filled
  Conflict                 filled
  Reason                   empty
  Tactics                  empty
  Value                    filled

  [FORCE_FILL] generation refused — 2 card(s) still empty: Reason, Tactics
```

### 1.3 The router asks rather than guesses

```
Stage 1 · Skill-1 intent-routing · classification & dispatch
  [CLARIFY_INTENT] Agent 2 (SCRTV) · Budget_Request · confidence 0.55
    borderline band — asking the user to disambiguate:
      · Agent 2 (SCRTV) — Budget_Request
      · Agent 5 (SCQA) — Conflict_Resolution
```

Confidence 0.55 lands in the routing map's borderline band (0.4 ≤ c < 0.6), so the
three-band rule returns `clarify_intent` instead of silently picking one.

---

## 2. Audit trail — `runs/<timestamp>.jsonl`

One JSONL record per stage, written on every run. This is the observability and
auditability surface: stage, skill, verdict, process exit code, latency, retry index,
and what was flagged.

Scenario `03-fabricated-metrics`, verbatim from the run above (fields trimmed for width):

```json
{"stage":"0", "skill":"Skill-11","verdict":"SAFE",   "exit_code":0,   "elapsed_ms":300,"retry":0}
{"stage":"1", "skill":"Skill-1", "verdict":"SUCCESS","exit_code":null,"elapsed_ms":0,  "retry":0}
{"stage":"2", "skill":"Skill-3", "verdict":"OK",     "exit_code":null,"elapsed_ms":0,  "retry":0}
{"stage":"3a","skill":"Skill-12","verdict":"PASS",   "exit_code":0,   "elapsed_ms":297,"retry":0}
{"stage":"3b","skill":"Skill-12","verdict":"BLOCK",  "exit_code":3,   "elapsed_ms":285,"retry":0,
 "flagged_values":["$1,200,000"],
 "flagged_claims":["According to Gartner","30% of","47% reduction"]}
{"stage":"3b","skill":"Skill-12","verdict":"PASS",   "exit_code":0,   "elapsed_ms":343,"retry":1,
 "flagged_values":[],"flagged_claims":[]}
{"stage":"3c","skill":"Skill-13","verdict":"OK",     "exit_code":null,"elapsed_ms":0,  "retry":0,"source":"recorded","points":3}
{"stage":"4", "skill":"Skill-9", "verdict":"OK",     "exit_code":null,"elapsed_ms":0,  "retry":0,"source":"recorded",
 "logic":88,"eq":63,"response_speed":70,"persuasion":74}
{"stage":"6", "skill":"Skill-10","verdict":"OK",     "exit_code":0,   "elapsed_ms":331,"retry":0}
```

Every gate decision is traceable to a process exit code, so a reviewer can re-run any
single stage and get the same verdict.

---

## 3. Test suite — `python -m unittest discover tests -v`

```
----------------------------------------------------------------------
Ran 36 tests in 8.277s

OK
```

The 36 tests assert exit codes *and* JSON verdicts across nine areas:

| Area | What is asserted |
|---|---|
| Skill-11 injection filter | override / prompt-extraction / jailbreak vocabulary blocked; zero-width evasion normalised; **four ordinary workplace sentences that must not false-positive** |
| Skill-12 output gate | grounded text PASSes; 1 invention → WARN + marker; 3+ → BLOCK with no disclaimer wrap; `--force-warn` downgrade; user-supplied figures never flagged |
| Skill-12 input gate | real values PASS; placeholders BLOCK; numbers in cards treated as user values |
| Skill-4 / Skill-10 | MECE checker emits JSON; empty score history is an answer, not a crash |
| Catalog & routing | 8 models with fields; 32 use cases; every catalog use case routable; every routed agent resolves to a model |
| Router bands | ≥0.6 routes · 0.4–0.6 clarifies · <0.4 falls back |
| Scenarios | all five behave as declared, and each declares expectations at all |
| Structural composition | every catalog card has a lead-in; composition preserves card order, is **not** a bare echo of the input, and skips empty cards |
| Recorded coaching contracts | Skill-13 recordings are exactly 3 points; Skill-9 recordings are 4 integers 0–100 plus exactly 2 tips; every shipped recording satisfies its contract |
| Repository cleanliness | a demo run never writes to the tracked `battle-scores.jsonl`; the merged growth input lands in the gitignored `runs/` |

---

## 4. Skill lifecycle drift gate — `python skills-library/sync.py --verify`

```
All agent copies in sync.
```

**38 agent skill copies verified byte-identical** to their canonical source in
`skills-library/`. Exit code 0. A drifted copy — an agent silently running a stale
skill — fails this gate and fails CI.

---

## 5. Live agent runs inside Claude Code

Artifacts produced by the agents themselves during development, present in the repo:

| Evidence | Path |
|---|---|
| 7 real routing rounds (agent, use case, confidence, status) | `agents/wisetalk-router-agent/claude-code/memory/chat-history.md` |
| Battle-score record feeding Skill-10 | `agents/wisetalk-router-agent/claude-code/memory/battle-scores.jsonl` |
| Accepted STAR draft with its Skill-12 trace | `agents/wisetalk-star-agent/claude-code/memory/drafts/Salary_Negotiation-v1.md` |

---

## 6. What these runs do and do not prove

Stated plainly, because a gate that lies about itself is worthless:

**Proven by the runs above:** the deterministic security layer works end to end and is
reproducible on a clean checkout with no dependencies — injections are refused at entry,
fabricated numbers and citations are caught before delivery, incomplete input refuses
generation, borderline intent asks rather than guesses, and all 38 agent skill copies match
their canonical source.

**Not proven by the runs above:** generation quality. Stage 3b replays a recorded draft
unless `ANTHROPIC_API_KEY` is set and `--api` is passed; the console and the browser page
both label which path ran. The gate that judges the draft is the real production script
either way — the recording is the input to the gate, never a substitute for it.

**Stage 1 caveat:** `demo.py`'s router is a deterministic keyword classifier standing in
for Skill-1's LLM classifier. It reads the same routing map and applies the same three-band
confidence rule, and it is labelled as a stand-in in every line of output it produces.
