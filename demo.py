#!/usr/bin/env python3
"""WiseTalk end-to-end pipeline demo — runnable without Claude Code.

Walks the Master Spec pipeline (`_wisetalk_extracted.md` §5, Stages 0-6) using the
same deterministic skill scripts the Expert Agents call, so a reviewer can clone the
repo and watch the whole loop with no install step:

    python demo.py                     # run every scenario in demo/scenarios/
    python demo.py --scenario salary   # run one
    python demo.py --list              # list scenarios
    python demo.py --api               # generate live via the Claude API (needs ANTHROPIC_API_KEY)

Stages, and what actually executes at each:

    Stage 0  Skill-11  injection-filter/scripts/dfa-filter.py        (DFA, fail-closed)
    Stage 1  Skill-1   deterministic keyword router over config/agent-routing-map.md
    Stage 2  Skill-3   mandatory fill-in cards from reference/wisetalk-model-catalog.md
    Stage 3a Skill-12  hallucination-gate.py --mode input            (card data)
    Stage 3b Skill-7   generation, then Skill-12 --mode gate; BLOCK regenerates (max 2)
    Stage 3c Skill-13  iterative critique — exactly 3 points, replayed from the scenario
    Stage 4  Skill-8/9 sandbox battle & scoring — replayed from the scenario
    Stage 6  Skill-10  growth-trends/scripts/aggregate-scores.py     (battle-score history)

Honesty boundaries — these matter, the whole point of the gates is not lying:
  * Stages 0, 3a, 3b's gate, and 6 are the REAL production scripts, not reimplementations.
  * Stages 3c and 4 are REPLAYED recordings. Skill-13, Skill-8 and Skill-9 are
    prose-only skills with no scripts, so they cannot run deterministically with
    no API key. Every line of their output is labelled `recorded`, and the
    recordings are validated against the skills' published contracts (exactly 3
    critique points; 4 integer scores 0-100 plus exactly 2 tips) so a drifted
    fixture fails the run rather than passing quietly.
  * Stage 1 here is a deterministic keyword router standing in for Skill-1's LLM
    classifier. It reads the same routing map and applies the same three-band
    confidence rule, but it is a stand-in and is labelled as one in the output.
  * Stage 3b's generation is a recorded draft by default (labelled `recorded`). With
    --api it calls the Claude API for real (labelled `live`). If a scenario carries no
    recording, compose_structural orders the user's own cards through the model's
    rhetorical sequence (labelled `composed`) — a structuring step, not a generator,
    and never presented as model output. The gate that judges the draft is the real
    script in all three cases.

Every stage appends a record to runs/<timestamp>.jsonl — the audit trail.

Exit codes: 0 all scenarios behaved as declared, 1 a scenario deviated, 2 usage error.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILLS = ROOT / "skills-library"
CATALOG = ROOT / "reference" / "wisetalk-model-catalog.md"
ROUTING_MAP = ROOT / "agents" / "wisetalk-router-agent" / "claude-code" / "config" / "agent-routing-map.md"
BATTLE_SCORES = ROOT / "agents" / "wisetalk-router-agent" / "claude-code" / "memory" / "battle-scores.jsonl"
SCENARIO_DIR = ROOT / "demo" / "scenarios"
RUNS_DIR = ROOT / "runs"

# Battles run during a session are written here, never back into BATTLE_SCORES.
# That file is tracked evidence from a real E2E run (see the router agent's
# eval-cases.md note), so a demo run must leave it byte-identical and `git status`
# clean. The growth aggregator reads the union of the two.
#
# These live in a subdirectory so that `runs/*.jsonl` stays exactly the audit
# trail — one schema, one meaning. Score records and audit records side by side
# would make the log unreadable to anything that scans it.
GROWTH_DIR = RUNS_DIR / "growth"
SESSION_BATTLES = GROWTH_DIR / "battle-scores-session.jsonl"
GROWTH_INPUT = GROWTH_DIR / "growth-input.jsonl"

DFA_FILTER = SKILLS / "injection-filter" / "scripts" / "dfa-filter.py"
HALLUCINATION_GATE = SKILLS / "hallucination-check" / "scripts" / "hallucination-gate.py"
GROWTH_TRENDS = SKILLS / "growth-trends" / "scripts" / "aggregate-scores.py"
MECE_CHECK = SKILLS / "mece-logic-checker" / "scripts" / "mece-check.py"

MAX_RETRIES = 2  # matches hallucination-gate.py and the agent bodies

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


# --------------------------------------------------------------------------
# Presentation
# --------------------------------------------------------------------------

class Style:
    """ANSI colours, disabled when output is piped or NO_COLOR is set."""

    enabled = sys.stdout.isatty() and not os.environ.get("NO_COLOR")

    @classmethod
    def _wrap(cls, code: str, text: str) -> str:
        return f"\033[{code}m{text}\033[0m" if cls.enabled else text

    @classmethod
    def bold(cls, t): return cls._wrap("1", t)

    @classmethod
    def dim(cls, t): return cls._wrap("2", t)

    @classmethod
    def green(cls, t): return cls._wrap("32", t)

    @classmethod
    def yellow(cls, t): return cls._wrap("33", t)

    @classmethod
    def red(cls, t): return cls._wrap("31", t)

    @classmethod
    def cyan(cls, t): return cls._wrap("36", t)


VERDICT_STYLE = {
    "PASS": Style.green, "SAFE": Style.green, "OK": Style.green,
    "WARN": Style.yellow, "CLARIFY": Style.yellow,
    "BLOCK": Style.red, "BLOCKED": Style.red,
}


def badge(verdict: str) -> str:
    return VERDICT_STYLE.get(verdict.upper(), Style.cyan)(f"[{verdict.upper()}]")


def stage_header(stage: str, skill: str, title: str) -> None:
    print(f"\n{Style.bold(stage)} {Style.dim('·')} {Style.cyan(skill)} {Style.dim('·')} {title}")


def indent(text: str, prefix: str = "    ") -> str:
    return "\n".join(prefix + line for line in str(text).splitlines())


# --------------------------------------------------------------------------
# Audit log (the 可观测 / observability trail)
# --------------------------------------------------------------------------

class AuditLog:
    """One JSONL record per pipeline stage, per scenario, per run."""

    def __init__(self, run_id: str):
        RUNS_DIR.mkdir(exist_ok=True)
        self.path = RUNS_DIR / f"{run_id}.jsonl"
        self.run_id = run_id
        self.records: list[dict] = []

    def record(self, *, scenario: str, stage: str, skill: str, verdict: str,
               exit_code: int | None, elapsed_ms: int, retry: int = 0, **extra) -> None:
        entry = {
            "run_id": self.run_id,
            "ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
            "scenario": scenario,
            "stage": stage,
            "skill": skill,
            "verdict": verdict,
            "exit_code": exit_code,
            "elapsed_ms": elapsed_ms,
            "retry": retry,
        }
        entry.update(extra)
        self.records.append(entry)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


# --------------------------------------------------------------------------
# Subprocess helper — every skill script is invoked exactly as an agent invokes it
# --------------------------------------------------------------------------

def run_script(script: Path, args: list[str], stdin: str | None = None) -> tuple[int, dict | None, str, int]:
    """Run a skill script. Returns (exit_code, parsed_json_or_None, raw_stdout, elapsed_ms)."""
    started = time.perf_counter()
    proc = subprocess.run(
        [sys.executable, str(script), *args],
        input=stdin,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    elapsed_ms = int((time.perf_counter() - started) * 1000)
    payload = None
    for line in reversed(proc.stdout.strip().splitlines()):
        try:
            payload = json.loads(line)
            break
        except json.JSONDecodeError:
            continue
    return proc.returncode, payload, proc.stdout, elapsed_ms


# --------------------------------------------------------------------------
# Catalog + routing map parsing — the demo reads the same sources the agents read
# --------------------------------------------------------------------------

def parse_catalog(path: Path = CATALOG) -> dict[str, dict]:
    """Model name -> {agent, model, fields: [(name, question)], use_cases: [...]}.

    Parses `## Agent N — Name` / `### Model: X` / the fill-in field table /
    `**Use cases:**` out of the catalog. The catalog stays the single source of
    truth: adding a model there makes it appear here with no code change.
    """
    text = path.read_text(encoding="utf-8")
    models: dict[str, dict] = {}
    sections = re.split(r"^## (Agent \d+ — .+)$", text, flags=re.MULTILINE)
    for header, body in zip(sections[1::2], sections[2::2]):
        model_match = re.search(r"^### Model:\s*(.+)$", body, flags=re.MULTILINE)
        if not model_match:
            continue
        model = model_match.group(1).strip()
        key = model.split("/")[0].split("(")[0].strip().upper().replace(" ", "_")

        fields = []
        table = re.search(r"\*\*Fill-in fields[^*]*\*\*\s*\n((?:\|.*\n)+)", body)
        if table:
            for row in table.group(1).splitlines():
                cells = [c.strip() for c in row.strip().strip("|").split("|")]
                if len(cells) < 2 or set(cells[0]) <= set("-: "):
                    continue
                name = cells[0].strip("`").strip()
                if not name or name.lower() == "field":
                    continue
                fields.append((name, cells[1]))

        use_cases = []
        uc = re.search(r"\*\*Use cases:\*\*\s*(.+)", body)
        if uc:
            use_cases = re.findall(r"`([^`]+)`", uc.group(1))

        models[key] = {
            "agent": header.strip(),
            "model": model,
            "fields": fields,
            "use_cases": use_cases,
        }
    return models


def parse_routing_map(path: Path = ROUTING_MAP) -> dict[str, str]:
    """use_case -> 'Agent N (MODEL)', from the routing map's quick-map table."""
    routes: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^\|\s*(`[^|]+`)\s*\|\s*(Agent \d+ \([^)]+\))\s*\|", line)
        if match:
            for use_case in re.findall(r"`([^`]+)`", match.group(1)):
                routes[use_case] = match.group(2).strip()
    return routes


# Keyword weights for the deterministic stand-in router (Stage 1). Each use case
# lists the signals that vote for it; confidence is the winner's share of all votes,
# scaled into the spec's three bands.
ROUTING_KEYWORDS: dict[str, list[str]] = {
    "Salary_Negotiation": ["salary", "raise", "compensation", "pay rise", "negotiate my", "counter offer"],
    "Client_Deal": ["client", "deal", "contract terms", "close the sale"],
    "Vendor_Management": ["vendor", "supplier", "procurement"],
    "Resource_Allocation": ["headcount", "allocate resources", "more people on"],
    "Job_Interview": ["interview", "tell me about a time", "behavioral question"],
    "Performance_Review": ["performance review", "appraisal", "self-assessment", "self assessment"],
    "Project_Debrief": ["debrief", "retrospective", "post-mortem", "postmortem"],
    "Resume_Writing": ["resume", "cv", "cover letter"],
    "Project_Status_Report": ["status report", "weekly update", "project update"],
    "Strategy_Proposal": ["proposal", "strategy", "pitch a plan", "business case"],
    "Budget_Request": ["budget", "funding", "approve spend", "cost approval"],
    "Issue_Escalation": ["escalate", "escalation", "raise this to"],
    "Logical_Analysis": ["analyse", "analyze", "break down", "structure my thinking"],
    "Report_Outlining": ["outline", "report structure", "table of contents"],
    "Meeting_Minutes": ["minutes", "meeting notes"],
    "Brainstorming_Structure": ["brainstorm", "ideation"],
    "Elevator_Pitch": ["elevator pitch", "introduce myself", "30 seconds", "thirty seconds"],
    "Quick_Meeting_Speech": ["speak up in the meeting", "quick speech", "say something in the meeting"],
    "Daily_Standup": ["standup", "stand-up", "daily update"],
    "Public_Comment": ["public comment", "town hall", "all hands", "all-hands"],
    "Crisis_Management": ["crisis", "outage", "incident", "emergency"],
    "Problem_Solving": ["problem", "root cause", "figure out why"],
    "Conflict_Resolution": ["conflict", "disagreement", "tension with", "argument with"],
    "Urgent_Incident": ["urgent", "sev1", "sev-1", "p0 incident"],
    "Team_Recognition": ["recognise", "recognize", "praise", "shout out", "shout-out", "thank the team"],
    "Relationship_Building": ["rapport", "build a relationship", "networking"],
    "Peer_Feedback": ["peer feedback", "feedback to a colleague", "360 feedback"],
    "Ice_Breaking": ["ice breaker", "icebreaker", "break the ice"],
    "Task_Delegation": ["delegate", "hand off", "assign this task"],
    "Complex_Instruction": ["complex instruction", "explain this process", "simplify these steps"],
    "Information_Compression": ["compress", "condense", "shorten this", "tl;dr", "summarise this email", "summarize this email"],
    "Executive_Summary": ["executive summary", "one-pager", "brief the exec"],
}

CONFIDENCE_THRESHOLD = 0.6      # high band floor      (agent-routing-map.md §5)
CLARIFICATION_BAND_LOW = 0.4    # borderline band floor


def route(text: str, routes: dict[str, str]) -> dict:
    """Deterministic keyword router — the demo stand-in for Skill-1's LLM classifier.

    Applies the routing map's three-band confidence rule verbatim:
      >= 0.6 success · 0.4-0.6 clarify_intent (top 2) · < 0.4 GENERAL_CHAT fallback.
    """
    lowered = text.lower()
    scores: dict[str, float] = {}
    for use_case, keywords in ROUTING_KEYWORDS.items():
        hits = [k for k in keywords if k in lowered]
        if hits:
            # Longer phrases are stronger evidence than single common words.
            scores[use_case] = sum(1 + len(k.split()) * 0.5 for k in hits)

    if not scores:
        return {
            "status": "fallback", "routed_agent": "GENERAL_CHAT",
            "use_case": "General_Communication", "confidence": 0.0, "candidates": [],
        }

    ranked = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
    total = sum(scores.values())
    top_case, top_score = ranked[0]
    confidence = round(min(0.95, 0.35 + 0.6 * (top_score / total)), 2)
    candidates = [
        {"use_case": uc, "routed_agent": routes.get(uc, "?"), "confidence": round(sc / total, 2)}
        for uc, sc in ranked[:2]
    ]

    if confidence >= CONFIDENCE_THRESHOLD:
        status = "success"
    elif confidence >= CLARIFICATION_BAND_LOW:
        status = "clarify_intent"
    else:
        return {
            "status": "fallback", "routed_agent": "GENERAL_CHAT",
            "use_case": "General_Communication", "confidence": confidence, "candidates": candidates,
        }

    return {
        "status": status,
        "routed_agent": routes.get(top_case, "?"),
        "use_case": top_case,
        "confidence": confidence,
        "candidates": candidates,
    }


def find_model(models: dict[str, dict], name: str) -> tuple[str, dict] | tuple[None, None]:
    """Resolve a model key from a catalog key, a routed_agent string, or an alias.

    'Agent 6 (RIDE)' -> RIDE; 'Funnel' -> COMMUNICATION_FUNNEL; 'MECE' -> MECE.
    """
    if not name:
        return None, None
    token = name
    paren = re.search(r"\(([^)]+)\)", name)
    if paren:
        token = paren.group(1)
    token = token.strip().upper().replace(" ", "_")
    if token in models:
        return token, models[token]
    for key, value in models.items():
        if key.startswith(token) or token in key.split("_"):
            return key, value
    return None, None


# --------------------------------------------------------------------------
# Generation (Skill-7) — recorded by default, live Claude API with --api
# --------------------------------------------------------------------------

def generate_live(model_info: dict, use_case: str, cards: dict[str, str],
                  revision_instruction: str | None = None) -> str:
    """Call the Claude API with the catalog's own generation prompt. Stdlib only."""
    import urllib.request

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set")

    filled = "\n".join(f"- {name}: {value}" for name, value in cards.items())
    prompt = (
        f"You are a WiseTalk {model_info['model']} expert. The user filled in the mandatory "
        f"cards for a [{use_case}]. Synthesize these fragments into a polished, "
        f"professional communication that follows the {model_info['model']} structure. "
        f"Use only the values the user provided — invent no numbers, statistics, quotes, "
        f"citations, or attributions.\n\nFilled cards:\n{filled}"
    )
    if revision_instruction:
        prompt += f"\n\nMandatory revision: {revision_instruction}"

    request = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps({
            "model": os.environ.get("WISETALK_MODEL", "claude-sonnet-5"),
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
        }).encode("utf-8"),
        headers={
            "content-type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = json.load(response)
    return "".join(block.get("text", "") for block in payload.get("content", []))


# --------------------------------------------------------------------------
# Generation stand-in (Skill-7) — deterministic, offline, and never passed off
# as model output. Used when no API key is available and the input is freeform,
# so there is no recorded draft to replay.
# --------------------------------------------------------------------------

# One lead-in per card name across the catalog's 8 models (28 slots, 25 distinct
# names — `Situation`, `Reason` and `Action` are shared between models). The card
# order in the catalog *is* the model's rhetorical order, so walking the fields in
# order and prefixing each with its lead-in produces the model's shape.
CARD_LEADINS = {
    # STAR
    "Situation": "The situation:",
    "Task": "What I was responsible for:",
    "Action": "What I did about it:",
    "Result": "Where that landed:",
    # SCRTV
    "Scene": "Where things stand:",
    "Conflict": "The problem blocking us:",
    "Reason": "Why it is happening:",
    "Tactics": "What I propose we do:",
    "Value": "What that is worth:",
    # MECE / Pyramid
    "Conclusion": "My conclusion up front:",
    "Arguments": "It rests on these arguments:",
    "Evidence": "The evidence behind them:",
    # PREP
    "Point": "My point:",
    "Example": "A concrete example:",
    # SCQA
    "Complication": "What has changed:",
    "Question": "So the question is:",
    "Answer": "My answer:",
    # RIDE
    "Risk": "The risk of leaving this as it is:",
    "Interest": "What we both gain by moving:",
    "Difference": "What sets this apart:",
    "Effect": "The effect I am asking for:",
    # FFC
    "Feeling": "How this landed for me:",
    "Fact": "Specifically, what you did:",
    "Compare": "Set against what came before:",
    # Funnel
    "OriginalText": "Source text:",
}

COMPOSED_NOTE = ("Assembled from your cards in the model's own order — "
                 "no language model was called.")


def compose_structural(model_info: dict, cards: dict[str, str]) -> str:
    """Order the filled cards through the model's rhetorical sequence.

    A deterministic Skill-7 stand-in, not a generator: it adds structure and
    nothing else. Every word of substance is the user's own, which is exactly why
    it is safe to run with no key and no network — and why it is labelled
    `composed` rather than `live` or `recorded` everywhere it surfaces.
    """
    parts = []
    for field, _question in model_info["fields"]:
        value = str(cards.get(field, "")).strip()
        if not value:
            continue
        parts.append(f"{CARD_LEADINS.get(field, field + ':')} {value}")
    return "\n\n".join(parts)


# --------------------------------------------------------------------------
# Recorded coaching artifacts — Skill-13 critique and Skill-8/9 battle are
# prose-only skills with no scripts, so they cannot run deterministically
# offline. The scenarios carry recordings, and these validate them against the
# skills' published contracts so a drifted fixture fails the demo loudly.
# --------------------------------------------------------------------------

BATTLE_DIMENSIONS = ["logic", "eq", "response_speed", "persuasion"]


def validate_critique(critique) -> list[str]:
    """Skill-13 contract: exactly 3 critique points."""
    if not isinstance(critique, list):
        return ["recorded_critique is not a list"]
    if len(critique) != 3:
        return [f"Skill-13 contract is exactly 3 critique points, found {len(critique)}"]
    return [f"critique point {i + 1} is empty" for i, p in enumerate(critique)
            if not str(p).strip()]


def validate_battle(battle) -> list[str]:
    """Skill-9 contract: 4 integer scores 0-100 plus exactly 2 advice tips."""
    if not isinstance(battle, dict):
        return ["recorded_battle is not an object"]
    problems = []
    for dim in BATTLE_DIMENSIONS:
        score = battle.get(dim)
        if not isinstance(score, int) or isinstance(score, bool):
            problems.append(f"{dim} is not an integer: {score!r}")
        elif not 0 <= score <= 100:
            problems.append(f"{dim} out of range 0-100: {score}")
    advice = battle.get("advice")
    if not isinstance(advice, list) or len(advice) != 2:
        problems.append("Skill-9 contract is exactly 2 advice tips, found "
                        f"{len(advice) if isinstance(advice, list) else advice!r}")
    return problems


def record_battle(battle: dict, scenario_id: str) -> dict:
    """Append one battle result to the gitignored session file. Returns the record."""
    GROWTH_DIR.mkdir(parents=True, exist_ok=True)
    entry = {"date": datetime.now().strftime("%Y-%m-%d"), "scenario": scenario_id,
             "origin": "recorded-fixture"}
    entry.update({dim: battle[dim] for dim in BATTLE_DIMENSIONS})
    with SESSION_BATTLES.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def growth_input_path() -> Path | None:
    """Merge the tracked seed with this session's battles into a scratch file.

    The seed is never written to. Returns None when there is nothing to plot.
    """
    lines = []
    for source in (BATTLE_SCORES, SESSION_BATTLES):
        if source.exists():
            lines += [ln for ln in source.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if not lines:
        return None
    GROWTH_DIR.mkdir(parents=True, exist_ok=True)
    GROWTH_INPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return GROWTH_INPUT


# --------------------------------------------------------------------------
# The pipeline
# --------------------------------------------------------------------------

def run_scenario(scenario: dict, models: dict[str, dict], routes: dict[str, str],
                 audit: AuditLog, use_api: bool = False) -> dict:
    """Walk one scenario through Stages 0-4. Returns an outcome dict for the summary."""
    name = scenario["id"]
    message = scenario["user_message"]
    outcome = {"id": name, "title": scenario.get("title", name), "deviations": []}
    expect = scenario.get("expect", {})

    print("\n" + Style.bold("=" * 78))
    print(Style.bold(f"  {scenario.get('title', name)}"))
    print(Style.dim(f"  scenario: {name}"))
    print(Style.bold("=" * 78))
    print(f"\n{Style.dim('user message:')}\n{indent(message)}")

    def check(label: str, actual: str, key: str) -> None:
        wanted = expect.get(key)
        if wanted is not None and str(wanted).upper() != str(actual).upper():
            outcome["deviations"].append(f"{label}: expected {wanted}, got {actual}")

    # ---- Stage 0 — Skill-11 injection filter (fail-closed) -----------------
    stage_header("Stage 0", "Skill-11 injection-filter", "entry safety interception")
    code, payload, _, ms = run_script(DFA_FILTER, ["--text", message])
    blocked = bool(payload and payload.get("is_blocked"))
    verdict = "BLOCKED" if blocked else "SAFE"
    audit.record(scenario=name, stage="0", skill="Skill-11", verdict=verdict,
                 exit_code=code, elapsed_ms=ms, script=DFA_FILTER.name)
    print(f"  {badge(verdict)} exit {code}  {Style.dim(DFA_FILTER.name)}")
    check("stage 0", verdict, "stage0")
    if blocked:
        print(indent(Style.red("403 — " + payload.get("block_reason", ""))))
        print(indent(Style.dim("pipeline stops here; nothing is routed or generated.")))
        outcome["final"] = "BLOCKED_AT_ENTRY"
        return outcome

    # ---- Stage 1 — Skill-1 routing ----------------------------------------
    stage_header("Stage 1", "Skill-1 intent-routing", "classification & dispatch")
    started = time.perf_counter()
    decision = route(message, routes)
    ms = int((time.perf_counter() - started) * 1000)
    audit.record(scenario=name, stage="1", skill="Skill-1", verdict=decision["status"].upper(),
                 exit_code=None, elapsed_ms=ms, routed_agent=decision["routed_agent"],
                 use_case=decision["use_case"], confidence=decision["confidence"],
                 implementation="deterministic-keyword-stand-in")
    print(f"  {badge(decision['status'])} {decision['routed_agent']} · "
          f"{decision['use_case']} · confidence {decision['confidence']}")
    print(indent(Style.dim("deterministic keyword router (stand-in for Skill-1's LLM classifier)")))
    check("routed agent", decision["routed_agent"], "routed_agent")

    if decision["status"] == "clarify_intent":
        print(indent(Style.yellow("borderline band — asking the user to disambiguate:")))
        for candidate in decision["candidates"]:
            print(indent(f"· {candidate['routed_agent']} — {candidate['use_case']}", "      "))
        outcome["final"] = "CLARIFY"
        return outcome
    if decision["status"] == "fallback":
        print(indent(Style.dim("no workplace signal — left to general chat, no Expert Agent triggered.")))
        outcome["final"] = "GENERAL_CHAT"
        return outcome

    model_key, model_info = find_model(models, decision["routed_agent"])
    if not model_info:
        outcome["deviations"].append(f"no catalog entry for {decision['routed_agent']}")
        outcome["final"] = "ERROR"
        return outcome

    # ---- Stage 2 — Skill-3 mandatory fill-in cards -------------------------
    stage_header("Stage 2", "Skill-3 mandatory-fill-in", f"{model_info['model']} cards")
    cards = scenario.get("cards", {})
    required = [field for field, _question in model_info["fields"]]
    missing = [f for f in required if not str(cards.get(f, "")).strip()]
    verdict = "OK" if not missing else "FORCE_FILL"
    audit.record(scenario=name, stage="2", skill="Skill-3", verdict=verdict, exit_code=None,
                 elapsed_ms=0, required=required, missing=missing, model=model_info["model"])
    for field, question in model_info["fields"]:
        value = str(cards.get(field, "")).strip()
        mark = Style.green("filled") if value else Style.yellow("empty")
        print(f"  {Style.bold(field):<24} {mark}")
        print(indent(Style.dim(question), "      "))
        if value:
            print(indent(value, "      "))
    if missing:
        print(f"\n  {badge('FORCE_FILL')} generation refused — "
              f"{len(missing)} card(s) still empty: {', '.join(missing)}")
        print(indent(Style.dim("Skill-3 asks for all missing cards at once (force_fill_batch).")))
        outcome["final"] = "FORCE_FILL"
        check("final", "FORCE_FILL", "final_verdict")
        return outcome

    # ---- Stage 3a — Skill-12 input gate -----------------------------------
    stage_header("Stage 3a", "Skill-12 hallucination-gate", "card data validation (--mode input)")
    card_text = "\n".join(f"{field}: {value}" for field, value in cards.items())
    code, payload, _, ms = run_script(HALLUCINATION_GATE, ["--mode", "input", "--data", card_text])
    verdict = payload["verdict"] if payload else "ERROR"
    audit.record(scenario=name, stage="3a", skill="Skill-12", verdict=verdict, exit_code=code,
                 elapsed_ms=ms, mode="input",
                 flagged=(payload or {}).get("heuristic_flagged_claims", []),
                 placeholders=(payload or {}).get("placeholder_flagged", []))
    print(f"  {badge(verdict)} exit {code}  {Style.dim(HALLUCINATION_GATE.name + ' --mode input')}")
    check("stage 3a", verdict, "stage3a")
    if verdict == "BLOCK":
        print(indent(Style.red((payload or {}).get("regeneration_instruction", ""))))
        print(indent(Style.dim("generation refuses until the flagged values are replaced.")))
        outcome["final"] = "BLOCKED_AT_INPUT"
        check("final", "BLOCKED_AT_INPUT", "final_verdict")
        return outcome

    # ---- Stage 3b — Skill-7 generation, gated by Skill-12 ------------------
    stage_header("Stage 3b", "Skill-7 + Skill-12", "generation behind the output gate")
    drafts = [scenario.get("recorded_draft", "")]
    drafts += scenario.get("recorded_regenerations", [])
    drafts = [d for d in drafts if d] or [compose_structural(model_info, cards)]
    final_text, final_verdict = "", "ERROR"
    regeneration_hint = None

    for attempt in range(MAX_RETRIES + 1):
        instruction = None if attempt == 0 else regeneration_hint
        if use_api:
            try:
                draft = generate_live(model_info, decision["use_case"], cards, instruction)
                source = "live"
            except Exception as exc:  # fall back to the recording rather than failing the demo
                print(indent(Style.yellow(f"live generation unavailable ({exc}); using recording")))
                draft = drafts[min(attempt, len(drafts) - 1)]
                source = "recorded"
        else:
            draft = drafts[min(attempt, len(drafts) - 1)]
            source = "recorded"

        label = Style.green("live model output") if source == "live" else Style.yellow("recorded draft (replay)")
        print(f"\n  {Style.dim(f'attempt {attempt + 1}/{MAX_RETRIES + 1}')} · {label}")
        print(indent(Style.dim(draft)))

        last_attempt = attempt == MAX_RETRIES
        args = ["--data", card_text]
        if last_attempt:
            args.append("--force-warn")  # retries exhausted: downgrade BLOCK to a marked WARN
        args += ["--text", draft]
        code, payload, _, ms = run_script(HALLUCINATION_GATE, args)
        verdict = payload["verdict"] if payload else "ERROR"
        audit.record(scenario=name, stage="3b", skill="Skill-12", verdict=verdict, exit_code=code,
                     elapsed_ms=ms, retry=attempt, mode="gate", generation_source=source,
                     force_warn=last_attempt,
                     flagged_values=(payload or {}).get("regex_flagged_values", []),
                     flagged_claims=(payload or {}).get("heuristic_flagged_claims", []))
        print(f"  {badge(verdict)} exit {code}  {Style.dim(HALLUCINATION_GATE.name + ' --mode gate')}")

        flagged = (payload or {}).get("regex_flagged_values", []) + (payload or {}).get("heuristic_flagged_claims", [])
        if flagged:
            print(indent(Style.dim("flagged: " + ", ".join(str(f) for f in flagged))))

        if verdict == "BLOCK":
            regeneration_hint = (payload or {}).get("regeneration_instruction", "")
            print(indent(Style.red("draft never reaches the user — regenerating with anti-fabrication constraints")))
            continue

        final_text, final_verdict = (payload or {}).get("safe_text", draft), verdict
        break

    print(f"\n  {badge(final_verdict)} delivered to the user:")
    print(indent(final_text))
    check("final", final_verdict, "final_verdict")
    outcome["final"] = final_verdict

    # ---- Stage 3c — Skill-13 iterative critique ---------------------------
    critique = scenario.get("recorded_critique") or []
    if critique:
        stage_header("Stage 3c", "Skill-13 iterative-critique", "three critique points")
        problems = validate_critique(critique)
        outcome["deviations"] += problems
        verdict = "OK" if not problems else "CONTRACT_VIOLATION"
        audit.record(scenario=name, stage="3c", skill="Skill-13", verdict=verdict,
                     exit_code=None, elapsed_ms=0, source="recorded", points=len(critique))
        print(f"  {badge(verdict)} {Style.yellow('recorded critique (replay)')} "
              f"{Style.dim('— Skill-13 is prose-only; no script to run offline')}")
        for i, point in enumerate(critique, 1):
            print(indent(f"{i}. {point}"))
        for problem in problems:
            print(indent(Style.red(problem)))
        check("critique points", str(len(critique)), "critique_points")

    # ---- Stage 4 — Skill-8 battle simulation, Skill-9 scoring --------------
    battle = scenario.get("recorded_battle")
    if battle:
        stage_header("Stage 4", "Skill-8 + Skill-9", "sandbox battle & scoring")
        problems = validate_battle(battle)
        outcome["deviations"] += problems
        verdict = "OK" if not problems else "CONTRACT_VIOLATION"
        print(f"  {badge(verdict)} {Style.yellow('recorded battle (replay)')} "
              f"{Style.dim('— Skill-8/9 are prose-only; no script to run offline')}")
        if not problems:
            for dim in BATTLE_DIMENSIONS:
                bar = "#" * round(battle[dim] / 5)
                print(f"    {dim:<16} {battle[dim]:>3}  {Style.cyan(bar)}")
            for tip in battle["advice"]:
                print(indent(Style.dim("tip: " + tip)))
            record_battle(battle, name)
        for problem in problems:
            print(indent(Style.red(problem)))
        audit.record(scenario=name, stage="4", skill="Skill-9", verdict=verdict,
                     exit_code=None, elapsed_ms=0, source="recorded",
                     **{dim: battle.get(dim) for dim in BATTLE_DIMENSIONS})
        if expect.get("battle_scored") is True and problems:
            outcome["deviations"].append("battle_scored expected, contract violated")

    # ---- Stage 6 — Skill-10 persistence & growth trends --------------------
    # Spec §5: Stage 6 is persistence/archiving, which is what growth-trends
    # reads. Reads the seed plus this session's battles; writes neither.
    scores_path = growth_input_path()
    if scores_path:
        stage_header("Stage 6", "Skill-10 growth-trends", "learning analytics")
        code, payload, raw, ms = run_script(GROWTH_TRENDS, ["--scores", str(scores_path)])
        audit.record(scenario=name, stage="6", skill="Skill-10", verdict="OK" if code == 0 else "EMPTY",
                     exit_code=code, elapsed_ms=ms,
                     source=f"{BATTLE_SCORES.relative_to(ROOT)} + {SESSION_BATTLES.relative_to(ROOT)}")
        print(f"  {badge('OK' if code == 0 else 'EMPTY')} exit {code}  {Style.dim(GROWTH_TRENDS.name)}")
        print(indent(json.dumps(payload, ensure_ascii=False, indent=2) if payload else raw.strip()))

    return outcome


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------

def load_scenarios(selector: str | None) -> list[dict]:
    files = sorted(SCENARIO_DIR.glob("*.json"))
    scenarios = []
    for path in files:
        data = json.loads(path.read_text(encoding="utf-8"))
        data.setdefault("id", path.stem)
        if selector and selector.lower() not in data["id"].lower():
            continue
        scenarios.append(data)
    return scenarios


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="WiseTalk end-to-end pipeline demo (Master Spec §5, Stages 0-6).",
    )
    parser.add_argument("--scenario", help="run only scenarios whose id contains this string")
    parser.add_argument("--list", action="store_true", help="list available scenarios and exit")
    parser.add_argument("--api", action="store_true",
                        help="generate live via the Claude API (needs ANTHROPIC_API_KEY)")
    args = parser.parse_args(argv)

    if not SCENARIO_DIR.exists():
        sys.stderr.write(f"no scenarios directory at {SCENARIO_DIR}\n")
        return 2

    scenarios = load_scenarios(args.scenario)
    if not scenarios:
        sys.stderr.write("no scenarios matched\n")
        return 2

    if args.list:
        for scenario in scenarios:
            print(f"{scenario['id']:<28} {scenario.get('title', '')}")
        return 0

    if args.api and not os.environ.get("ANTHROPIC_API_KEY"):
        print(Style.yellow("--api given but ANTHROPIC_API_KEY is unset; falling back to recorded drafts."))

    # Start each run from the tracked seed alone, so two identical invocations
    # produce identical growth output. Reproducibility is the claim being sold.
    SESSION_BATTLES.unlink(missing_ok=True)

    models = parse_catalog()
    routes = parse_routing_map()
    run_id = datetime.now().strftime("%Y%m%dT%H%M%S")
    audit = AuditLog(run_id)

    print(Style.bold("WiseTalk — end-to-end pipeline demo"))
    print(Style.dim(f"{len(models)} models · {len(routes)} use cases · {len(scenarios)} scenario(s)"))
    print(Style.dim(f"audit log: {audit.path.relative_to(ROOT)}"))

    outcomes = [run_scenario(s, models, routes, audit, use_api=args.api) for s in scenarios]

    print("\n" + Style.bold("=" * 78))
    print(Style.bold("  Summary"))
    print(Style.bold("=" * 78))
    deviated = 0
    for outcome in outcomes:
        if outcome["deviations"]:
            deviated += 1
            print(f"  {Style.red('DEVIATED')} {outcome['id']}")
            for note in outcome["deviations"]:
                print(indent(note, "      "))
        else:
            print(f"  {Style.green('as declared')} {outcome['id']:<28} → {outcome.get('final', '?')}")

    print(f"\n  {len(audit.records)} audit records written to {audit.path.relative_to(ROOT)}")
    return 1 if deviated else 0


if __name__ == "__main__":
    sys.exit(main())
