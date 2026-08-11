#!/usr/bin/env python3
"""WiseTalk browser demo — zero-dependency, stdlib http.server only.

    python demo_server.py            # http://localhost:8000
    python demo_server.py --port 9000

Renders the Master Spec's Stage 2 "mandatory fill-in cards" UI — the non-chatbox
interface the spec calls for — and runs a submitted set of cards through the real
pipeline, showing every gate verdict as it happens.

Shares its pipeline primitives with demo.py (same scripts, same routing map, same
catalog, same audit log).

Stage 3b has three possible sources and the page always labels which one ran:

    live      a real Claude API call   (only with --api and ANTHROPIC_API_KEY)
    recorded  a draft replayed from the scenario file
    composed  your cards ordered through the model's rhetorical sequence, by
              demo.compose_structural — deterministic, offline, no model call

`composed` is what freeform input gets with no key. It is a structuring step, not
a generator, and is never presented as model output.

No pip install, no framework, no build step, no CDN — the page is served from this
file and nothing is fetched from the network.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

import demo
from demo import (
    BATTLE_DIMENSIONS, COMPOSED_NOTE, GROWTH_TRENDS, HALLUCINATION_GATE, DFA_FILTER,
    MAX_RETRIES, ROOT, SESSION_BATTLES,
    AuditLog, compose_structural, find_model, growth_input_path, parse_catalog,
    parse_routing_map, record_battle, route, run_script, validate_battle,
    validate_critique,
)

MODELS = parse_catalog()
ROUTES = parse_routing_map()
SCENARIOS = {s["id"]: s for s in demo.load_scenarios(None)}

CORPUS_DIR = ROOT / "demo" / "corpus"
METRICS_SCRIPT = ROOT / "tools" / "metrics.py"

# Set from --api in main(). Off by default: without it every submission would
# attempt an outbound call that can only fail, and swallow the failure silently.
LIVE = False


# --------------------------------------------------------------------------
# Pipeline — same stages as demo.py, returning structured records for the UI
# --------------------------------------------------------------------------

def run_pipeline(message: str, cards: dict[str, str], model_key: str | None,
                 audit: AuditLog, scenario_id: str = "browser") -> dict:
    """Stages 0-3b for the browser. Returns {stages: [...], delivered: str|None}."""
    stages: list[dict] = []

    def add(stage, skill, verdict, detail, **extra):
        entry = {"stage": stage, "skill": skill, "verdict": verdict, "detail": detail}
        entry.update(extra)
        stages.append(entry)
        return entry

    # Stage 0 — injection filter
    code, payload, _, ms = run_script(DFA_FILTER, ["--text", message or " "])
    blocked = bool(payload and payload.get("is_blocked"))
    verdict = "BLOCKED" if blocked else "SAFE"
    audit.record(scenario=scenario_id, stage="0", skill="Skill-11", verdict=verdict,
                 exit_code=code, elapsed_ms=ms)
    add("Stage 0", "Skill-11 injection-filter", verdict,
        payload.get("block_reason", "no injection or prohibited vocabulary detected")
        if blocked else "no injection or prohibited vocabulary detected",
        exit_code=code, elapsed_ms=ms)
    if blocked:
        return {"stages": stages, "delivered": None, "halted": "403 — request refused at the entry gate"}

    # Stage 1 — routing
    started = time.perf_counter()
    decision = route(message, ROUTES)
    ms = int((time.perf_counter() - started) * 1000)
    audit.record(scenario=scenario_id, stage="1", skill="Skill-1", verdict=decision["status"].upper(),
                 exit_code=None, elapsed_ms=ms, routed_agent=decision["routed_agent"],
                 use_case=decision["use_case"], confidence=decision["confidence"])
    add("Stage 1", "Skill-1 intent-routing", decision["status"].upper(),
        f"{decision['routed_agent']} · {decision['use_case']} · confidence {decision['confidence']}",
        exit_code=None, elapsed_ms=ms, candidates=decision["candidates"],
        note="deterministic keyword router (stand-in for Skill-1's LLM classifier)")
    if decision["status"] == "clarify_intent":
        return {"stages": stages, "delivered": None,
                "halted": "borderline confidence — the router asks which one you meant rather than guessing"}
    if decision["status"] == "fallback":
        return {"stages": stages, "delivered": None,
                "halted": "no workplace signal — left to general chat, no Expert Agent triggered"}

    resolved_key, model_info = find_model(MODELS, model_key or decision["routed_agent"])
    if not model_info:
        return {"stages": stages, "delivered": None, "halted": "no catalog entry for the routed agent"}

    # Stage 2 — mandatory fill-in cards
    required = [field for field, _ in model_info["fields"]]
    missing = [f for f in required if not str(cards.get(f, "")).strip()]
    verdict = "OK" if not missing else "FORCE_FILL"
    audit.record(scenario=scenario_id, stage="2", skill="Skill-3", verdict=verdict,
                 exit_code=None, elapsed_ms=0, missing=missing)
    add("Stage 2", "Skill-3 mandatory-fill-in", verdict,
        f"all {len(required)} {model_info['model']} cards filled" if not missing
        else f"generation refused — {len(missing)} card(s) empty: {', '.join(missing)}",
        missing=missing)
    if missing:
        return {"stages": stages, "delivered": None,
                "halted": "the cards are the scaffolding — WiseTalk will not write around an empty one"}

    # Stage 3a — input gate
    card_text = "\n".join(f"{k}: {v}" for k, v in cards.items() if str(v).strip())
    code, payload, _, ms = run_script(HALLUCINATION_GATE, ["--mode", "input", "--data", card_text])
    verdict = payload["verdict"] if payload else "ERROR"
    audit.record(scenario=scenario_id, stage="3a", skill="Skill-12", verdict=verdict,
                 exit_code=code, elapsed_ms=ms, mode="input")
    flagged = (payload or {}).get("heuristic_flagged_claims", []) + (payload or {}).get("placeholder_flagged", [])
    add("Stage 3a", "Skill-12 gate (--mode input)", verdict,
        "card data is clean — every value is yours" if verdict == "PASS"
        else "flagged in the card data: " + ", ".join(str(f) for f in flagged),
        exit_code=code, elapsed_ms=ms, flagged=flagged)
    if verdict == "BLOCK":
        return {"stages": stages, "delivered": None,
                "halted": "generation refuses until the flagged values are replaced with real ones"}

    # Stage 3b — generation behind the output gate
    scenario = SCENARIOS.get(scenario_id, {})
    drafts = [d for d in [scenario.get("recorded_draft", "")]
              + scenario.get("recorded_regenerations", []) if d]
    hint, delivered, final_verdict = None, None, "ERROR"

    for attempt in range(MAX_RETRIES + 1):
        api_error = None
        draft, source = None, None
        if LIVE:
            try:
                draft = demo.generate_live(model_info, decision["use_case"], cards,
                                           None if attempt == 0 else hint)
                source = "live"
            except Exception as exc:
                # Surfaced in the stage record rather than swallowed — a silent
                # fallback here would let the page claim a replay that never was.
                api_error = str(exc)
        if draft is None:
            if drafts:
                draft, source = drafts[min(attempt, len(drafts) - 1)], "recorded"
            else:
                # Freeform input: nothing recorded to replay. Order the user's own
                # cards through the model rather than echoing them back.
                draft, source = compose_structural(model_info, cards), "composed"

        last = attempt == MAX_RETRIES
        args = ["--data", card_text] + (["--force-warn"] if last else []) + ["--text", draft]
        code, payload, _, ms = run_script(HALLUCINATION_GATE, args)
        verdict = payload["verdict"] if payload else "ERROR"
        flagged = ((payload or {}).get("regex_flagged_values", [])
                   + (payload or {}).get("heuristic_flagged_claims", []))
        audit.record(scenario=scenario_id, stage="3b", skill="Skill-12", verdict=verdict,
                     exit_code=code, elapsed_ms=ms, retry=attempt, mode="gate",
                     generation_source=source, flagged=flagged, api_error=api_error)
        add(f"Stage 3b · attempt {attempt + 1}", "Skill-7 + Skill-12 gate", verdict,
            "clean — cleared for delivery" if verdict == "PASS"
            else ("blocked before you saw it: " + ", ".join(str(f) for f in flagged) if verdict == "BLOCK"
                  else "delivered with inference markers: " + ", ".join(str(f) for f in flagged)),
            exit_code=code, elapsed_ms=ms, draft=draft, source=source, flagged=flagged,
            note=(COMPOSED_NOTE if source == "composed" else None)
                 or (f"live generation unavailable ({api_error}) — fell back" if api_error else None))

        if verdict == "BLOCK":
            hint = (payload or {}).get("regeneration_instruction", "")
            continue
        delivered, final_verdict = (payload or {}).get("safe_text", draft), verdict
        break

    # Stage 3c — Skill-13 critique (prose-only skill: replayed, never claimed live)
    critique = scenario.get("recorded_critique") or []
    if critique and not validate_critique(critique):
        audit.record(scenario=scenario_id, stage="3c", skill="Skill-13", verdict="OK",
                     exit_code=None, elapsed_ms=0, source="recorded", points=len(critique))
        add("Stage 3c", "Skill-13 iterative-critique", "OK",
            "exactly 3 critique points — the Skill-13 contract",
            critique=critique, source="recorded")

    # Stage 4 — Skill-8 battle, Skill-9 scoring (also prose-only, also replayed)
    battle = scenario.get("recorded_battle")
    if battle and not validate_battle(battle):
        record_battle(battle, scenario_id)
        audit.record(scenario=scenario_id, stage="4", skill="Skill-9", verdict="OK",
                     exit_code=None, elapsed_ms=0, source="recorded",
                     **{dim: battle[dim] for dim in BATTLE_DIMENSIONS})
        add("Stage 4", "Skill-8 + Skill-9 battle", "OK",
            "four dimensions scored, two tips — the Skill-9 contract",
            battle=battle, source="recorded")

    return {"stages": stages, "delivered": delivered, "verdict": final_verdict, "halted": None}


def growth_data() -> dict:
    """Skill-10 over the tracked seed plus this session's battles.

    The seed (agents/.../memory/battle-scores.jsonl) is tracked evidence from a
    real E2E run and is never written to — the union is materialised in runs/,
    which is gitignored, so a demo session leaves the repo clean.
    """
    scores_path = growth_input_path()
    if not scores_path:
        return {"message": "No history available yet"}
    _code, payload, raw, _ms = run_script(GROWTH_TRENDS, ["--scores", str(scores_path)])
    result = payload or {"message": raw.strip()}
    if isinstance(result, dict):
        session = 0
        if SESSION_BATTLES.exists():
            session = len([ln for ln in SESSION_BATTLES.read_text(encoding="utf-8").splitlines()
                           if ln.strip()])
        result["session_battles"] = session
    return result


def corpus_data() -> dict:
    """Run the real DFA filter over both corpora, live, in front of the reader.

    METRICS.md asserts 28/28 blocked and 0/24 false positives. This recomputes
    it on request instead of restating it.
    """
    out = {}
    for label, filename, expect_blocked in (
        ("attack", "injection-attacks.txt", True),
        ("benign", "benign-workplace.txt", False),
    ):
        path = CORPUS_DIR / filename
        if not path.exists():
            out[label] = {"error": f"missing {filename}"}
            continue
        lines = [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines()
                 if ln.strip() and not ln.startswith("#")]
        blocked = 0
        for line in lines:
            _code, payload, _raw, _ms = run_script(DFA_FILTER, ["--text", line])
            if payload and payload.get("is_blocked"):
                blocked += 1
        out[label] = {
            "file": f"demo/corpus/{filename}",
            "total": len(lines),
            "blocked": blocked,
            "correct": blocked if expect_blocked else len(lines) - blocked,
        }
    return out


def metrics_data() -> dict:
    """KPI strip, computed by tools/metrics.py rather than hardcoded here."""
    if not METRICS_SCRIPT.exists():
        return {"error": "tools/metrics.py not found"}
    _code, _payload, raw, _ms = run_script(METRICS_SCRIPT, [])
    wanted = {
        "communication models": "models",
        "routable use cases": "use_cases",
        "agent packages": "agents",
        "mandatory cards across models": "cards",
        "reusable library skills": "skills",
        "third-party dependencies": "dependencies",
    }
    out = {}
    for line in raw.splitlines():
        if "." not in line:
            continue
        label, _, value = line.partition("..")
        key = wanted.get(label.strip().rstrip("."))
        if key:
            digits = value.strip().lstrip(". ").split()
            if digits and digits[0].isdigit():
                out[key] = int(digits[0])
    return out


# --------------------------------------------------------------------------
# HTTP
# --------------------------------------------------------------------------

class QuietServer(ThreadingHTTPServer):
    """ThreadingHTTPServer that does not shout when a browser walks away.

    Reloading the page, or navigating while /api/metrics or /api/corpus is still
    running its subprocesses, aborts the socket mid-write. The stdlib default
    prints a full traceback for that, which looks like a crash — especially on a
    screen recording. A disconnected client is not an error worth reporting.
    """

    def handle_error(self, request, client_address):
        if isinstance(sys.exc_info()[1], (ConnectionAbortedError, ConnectionResetError,
                                          BrokenPipeError)):
            return
        super().handle_error(request, client_address)


class Handler(BaseHTTPRequestHandler):
    audit: AuditLog

    def log_message(self, fmt, *args):  # quieter console
        sys.stderr.write(f"  {self.address_string()} — {fmt % args}\n")

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, payload, status: int = 200) -> None:
        self._send(status, json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                   "application/json; charset=utf-8")

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/":
            self._send(200, PAGE.encode("utf-8"), "text/html; charset=utf-8")
        elif path == "/favicon.ico":
            # No icon to serve, and a 404 per page load is console noise on a
            # recording. 204 answers the browser without saying anything.
            self.send_response(204)
            self.send_header("Content-Length", "0")
            self.end_headers()
        elif path == "/api/models":
            self._json({
                "models": [
                    {"key": key, "agent": info["agent"], "model": info["model"],
                     "fields": [{"name": n, "question": q} for n, q in info["fields"]],
                     "use_cases": info["use_cases"]}
                    for key, info in MODELS.items()
                ],
                "scenarios": [
                    {"id": s["id"], "title": s.get("title", s["id"]),
                     "message": s["user_message"], "cards": s.get("cards", {})}
                    for s in SCENARIOS.values()
                ],
                "live": LIVE and bool(os.environ.get("ANTHROPIC_API_KEY")),
            })
        elif path == "/api/growth":
            self._json(growth_data())
        elif path == "/api/metrics":
            self._json(metrics_data())
        elif path == "/api/corpus":
            self._json(corpus_data())
        else:
            self._json({"error": "not found"}, 404)

    def do_POST(self):
        if urlparse(self.path).path != "/api/run":
            return self._json({"error": "not found"}, 404)
        length = int(self.headers.get("Content-Length", 0))
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            return self._json({"error": "invalid JSON"}, 400)
        try:
            result = run_pipeline(
                body.get("message", ""), body.get("cards", {}) or {},
                body.get("model"), self.audit, body.get("scenario_id", "browser"),
            )
        except Exception as exc:  # never leave the page hanging
            return self._json({"error": str(exc)}, 500)
        self._json(result)


PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>WiseTalk — pipeline demo</title>
<style>
  /* Palette from the ui-ux-pro-max "developer tool / pipeline inspector" design
     system (code dark + run green). Web fonts and animation libraries from that
     system are deliberately NOT used: this page ships zero dependencies and
     fetches nothing from the network, so type is the system stack and every
     transition is hand-written CSS. */
  :root {
    --bg:#f1f5f9; --panel:#ffffff; --card:#ffffff; --ink:#0f172a; --muted:#475569; --line:#cbd5e1;
    --primary:#1e293b; --accent:#15803d;
    --pass:#15803d; --on-pass:#ffffff;
    --warn:#a16207; --on-warn:#ffffff;
    --block:#b91c1c; --on-block:#ffffff;
    --shade:#e2e8f0;
    --sp-1:4px; --sp-2:8px; --sp-3:12px; --sp-4:16px; --sp-5:24px; --sp-6:32px;
    --radius-sm:6px; --radius-md:10px; --radius-lg:14px;
    --shadow-sm:0 1px 2px rgba(15,23,42,.06);
    --shadow-md:0 2px 10px rgba(15,23,42,.07), 0 1px 2px rgba(15,23,42,.05);
    --ease-out:cubic-bezier(.16,1,.3,1);
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg:#0f172a; --panel:#1e293b; --card:#1b2336; --ink:#f8fafc; --muted:#94a3b8; --line:#334155;
      --primary:#334155; --accent:#22c55e;
      --pass:#22c55e; --on-pass:#052e16;
      --warn:#eab308; --on-warn:#1c1917;
      --block:#ef4444; --on-block:#450a0a;
      --shade:#272f42;
      --shadow-sm:0 1px 2px rgba(0,0,0,.25);
      --shadow-md:0 4px 16px rgba(0,0,0,.35), 0 1px 3px rgba(0,0,0,.3);
    }
  }
  * { box-sizing:border-box; }
  body { margin:0; background:var(--bg); color:var(--ink);
         font:15px/1.55 ui-sans-serif,-apple-system,"Segoe UI",system-ui,sans-serif; }
  header { padding:var(--sp-6) var(--sp-5) var(--sp-1); max-width:1120px; margin:0 auto; }
  h1 { font-size:24px; line-height:1.25; margin:0 0 var(--sp-1); letter-spacing:-.02em; font-weight:700; }
  .sub { color:var(--muted); font-size:14px; line-height:1.5; max-width:70ch; }
  main { max-width:1120px; margin:0 auto; padding:var(--sp-3) var(--sp-5) 60px;
         display:grid; grid-template-columns:minmax(320px,1fr) minmax(320px,1.15fr); gap:var(--sp-5); }
  @media (max-width:900px) { main { grid-template-columns:1fr; } }
  .panel { background:var(--card); border:1px solid var(--line); border-radius:var(--radius-md);
           padding:var(--sp-4); box-shadow:var(--shadow-md); }
  h2 { font-size:13px; text-transform:uppercase; letter-spacing:.07em; color:var(--muted);
       margin:0 0 var(--sp-3); font-weight:600; }
  label { display:block; font-size:13px; font-weight:600; margin:14px 0 2px; }
  .q { font-size:12.5px; color:var(--muted); margin-bottom:5px; }
  textarea, input, select { width:100%; background:var(--bg); color:var(--ink);
    border:1px solid var(--line); border-radius:var(--radius-sm); padding:8px 9px; font:inherit; font-size:14px;
    transition:border-color .15s var(--ease-out), box-shadow .15s var(--ease-out); }
  textarea:focus-visible, input:focus-visible, select:focus-visible { border-color:var(--accent); }
  textarea { min-height:60px; resize:vertical; }
  .row { display:flex; gap:var(--sp-2); align-items:center; margin-bottom:10px; flex-wrap:wrap; }
  button { background:var(--accent); color:var(--on-pass); border:0; border-radius:var(--radius-sm);
           padding:9px 16px; font:inherit; font-weight:600; cursor:pointer;
           transition:filter .18s var(--ease-out), background-color .18s var(--ease-out), transform .1s var(--ease-out); }
  button:hover:not(:disabled) { filter:brightness(1.08); }
  button:active:not(:disabled) { transform:scale(.97); }
  button.ghost { background:transparent; color:var(--ink); border:1px solid var(--line); }
  button:disabled { opacity:.5; cursor:default; }
  select, summary { cursor:pointer; }
  :focus-visible { outline:2px solid var(--accent); outline-offset:2px; }

  /* KPI strip — every number computed by tools/metrics.py at request time.
     flex:1 makes the row span the same width as the panels below it instead
     of clumping content-sized cards on the left. */
  .kpis { display:flex; flex-wrap:wrap; gap:var(--sp-2); max-width:1120px; margin:0 auto;
          padding:var(--sp-2) var(--sp-5) 0; }
  .kpi { flex:1 1 140px; min-width:0; background:var(--card); border:1px solid var(--line);
         border-radius:var(--radius-sm); padding:7px 11px; box-shadow:var(--shadow-sm); }
  .kpi b { display:block; font-size:17px; letter-spacing:-.02em;
           font-family:ui-monospace,Menlo,Consolas,monospace; }
  .kpi span { font-size:10.5px; text-transform:uppercase; letter-spacing:.05em; color:var(--muted); }

  /* Per-card engineering detail (skill id / timing) toggle, styled as a quiet
     pill instead of the browser's default triangle+bold text. */
  details.stagemeta summary {
    cursor:pointer; list-style:none; color:var(--muted); font-weight:600;
    transition:color .15s var(--ease-out), border-color .15s var(--ease-out);
  }
  details.stagemeta summary::-webkit-details-marker { display:none; }
  details.stagemeta summary::marker { content:""; }
  details.stagemeta summary:hover { color:var(--ink); }
  details.stagemeta { display:inline-block; }
  details.stagemeta summary { font-size:11px; padding:1px 6px; border:1px solid var(--line);
                               border-radius:10px; }
  details.stagemeta summary:hover { border-color:var(--muted); }
  details.stagemeta[open] summary { border-color:var(--accent); color:var(--ink); }
  details.stagemeta .skill, details.stagemeta .meta { display:block; margin-top:3px; }

  /* Stage rail — the vertical connector makes BLOCK -> regenerate -> PASS read
     as one sequence rather than three unrelated rows. Cards start hidden and
     stagger in on render() so a run reads as a sequence, not a wall of text. */
  #stages { position:relative; }
  .stage { position:relative; border-left:2px solid var(--line); padding:9px 0 11px 16px;
           margin-left:5px; opacity:0; transform:translateY(6px);
           transition:opacity .35s ease, transform .35s ease; }
  .stage.in { opacity:1; transform:none; }
  .stage:last-child { border-left-color:transparent; }
  .stage::before { content:""; position:absolute; left:-6px; top:14px; width:10px; height:10px;
                   border-radius:50%; background:var(--line); border:2px solid var(--card); }
  .stage.v-pass::before { background:var(--pass); }
  .stage.v-warn::before { background:var(--warn); }
  .stage.v-block::before { background:var(--block); }
  .stage .top { display:flex; gap:8px; align-items:center; flex-wrap:wrap; }
  .name { font-weight:600; font-size:13.5px; }
  .skill { color:var(--muted); font-size:12.5px; font-family:ui-monospace,Menlo,Consolas,monospace; }
  .badge { font-size:10.5px; font-weight:700; letter-spacing:.05em; padding:2px 8px;
           border-radius:20px; background:var(--shade); color:var(--ink); }
  .badge.v-pass  { background:var(--pass);  color:var(--on-pass); }
  .badge.v-warn  { background:var(--warn);  color:var(--on-warn); }
  .badge.v-block { background:var(--block); color:var(--on-block); }
  .detail { font-size:13px; color:var(--muted); margin-top:4px; }
  .draft { white-space:pre-wrap; background:var(--bg); border:1px solid var(--line);
           border-radius:var(--radius-sm); padding:10px; margin-top:7px; font-size:13px; }
  .struck { text-decoration:line-through; opacity:.5; }
  .meta { font-size:11.5px; color:var(--muted); font-family:ui-monospace,Menlo,Consolas,monospace; }
  .halted { border:1px dashed var(--line); border-radius:var(--radius-sm); padding:10px;
            margin-top:10px; font-size:13.5px; color:var(--warn); }
  .delivered { border:1px solid var(--pass); border-radius:var(--radius-md); padding:12px; margin-top:12px;
               box-shadow:var(--shadow-sm); }
  .delivered h3 { margin:0 0 7px; font-size:13px; color:var(--pass);
                  text-transform:uppercase; letter-spacing:.06em; }
  .empty { color:var(--muted); font-size:13.5px; border:1px dashed var(--line);
           border-radius:var(--radius-sm); padding:12px; }
  svg { width:100%; height:auto; }
  .tag { font-size:10.5px; padding:2px 7px; border-radius:4px; border:1px solid var(--line);
         color:var(--muted); }
  .tag.live { border-color:var(--pass); color:var(--pass); }
  .tag.composed { border-color:var(--warn); color:var(--warn); }

  /* Stage timing — a bar per stage, scaled to the slowest in the run */
  .bar { height:3px; background:var(--accent); border-radius:2px; margin-top:6px; opacity:.55;
         transition:width .3s ease; }

  ol.critique { margin:7px 0 0; padding-left:20px; font-size:13px; color:var(--ink); }
  ol.critique li { margin-bottom:6px; }
  .tips { margin-top:8px; font-size:12.5px; color:var(--muted); }
  .tips div { margin-bottom:5px; padding-left:14px; text-indent:-14px; }
  .radar { display:flex; justify-content:center; gap:14px; align-items:center; flex-wrap:wrap; }
  .radar svg { max-width:230px; }
  .scores { font-size:12.5px; font-family:ui-monospace,Menlo,Consolas,monospace; }
  .scores div { display:flex; justify-content:space-between; gap:12px; }

  @media (prefers-reduced-motion: reduce) {
    * { transition:none !important; animation:none !important; }
  }
</style>
</head>
<body>
<header>
  <h1>WiseTalk: AI Communication Coach</h1>
  <div class="sub">Fill the cards, submit, and watch every gate verdict, the critique, and
    the battle score.</div>
</header>
<div class="kpis" id="kpis"></div>
<main>
  <section class="panel">
    <h2>Your scenario</h2>
    <div class="row">
      <select id="scenario" aria-label="Load an example scenario" style="flex:1 1 240px">
        <option value="">— load an example —</option></select>
      <select id="model" aria-label="Communication model" style="flex:1 1 160px"></select>
    </div>
    <label for="message">What do you need to communicate?</label>
    <div class="q">The router classifies this — it decides which of the 8 experts answers.</div>
    <textarea id="message" placeholder="e.g. I need to negotiate a salary increase with my manager next week."></textarea>
    <div id="cards"></div>
    <div class="row" style="margin-top:16px">
      <button id="run">Run the pipeline</button>
      <button id="clear" class="ghost">Clear</button>
    </div>
  </section>

  <section>
    <div class="panel">
      <h2>Pipeline</h2>
      <div id="stages"><div class="empty">Fill the cards and press Run.</div></div>
      <div id="out"></div>
    </div>
  </section>
</main>
<script>
let DATA = {models: [], scenarios: []};
const $ = id => document.getElementById(id);
const esc = s => String(s == null ? "" : s).replace(/[&<>]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));

// Verdict -> visual class. One map, used by both the badge and the rail dot, so a
// new verdict string can never render as a badge with no dot or vice versa.
const VERDICT_CLASS = {
  PASS:"v-pass", SAFE:"v-pass", OK:"v-pass", SUCCESS:"v-pass",
  WARN:"v-warn", CLARIFY_INTENT:"v-warn", FORCE_FILL:"v-warn", FALLBACK:"v-warn",
  BLOCK:"v-block", BLOCKED:"v-block", ERROR:"v-block", CONTRACT_VIOLATION:"v-block",
};
const vclass = v => VERDICT_CLASS[String(v).toUpperCase()] || "";

const SOURCE_LABEL = {
  live:     ["live", "live model output"],
  recorded: ["", "recorded draft (replay)"],
  composed: ["composed", "structural composition — no model call"],
};

async function boot() {
  DATA = await (await fetch("/api/models")).json();
  $("model").innerHTML = DATA.models.map(m =>
    `<option value="${m.key}">${esc(m.model)} — ${esc(m.agent)}</option>`).join("");
  $("scenario").innerHTML += DATA.scenarios.map(s =>
    `<option value="${s.id}">${esc(s.title)}</option>`).join("");
  renderCards();
  drawKpis();
}

async function drawKpis() {
  try {
    const m = await (await fetch("/api/metrics")).json();
    const items = [["models","models"],["use_cases","use cases"],["agents","agents"],
                   ["cards","cards"],["skills","skills"],["dependencies","deps"]];
    $("kpis").innerHTML = items.filter(([k]) => m[k] != null).map(([k, label]) =>
      `<div class="kpi"><b>${esc(m[k])}</b><span>${esc(label)}</span></div>`).join("");
  } catch (err) { /* the strip is decoration; never block the demo on it */ }
}

function currentModel() { return DATA.models.find(m => m.key === $("model").value); }

function renderCards(values) {
  const model = currentModel();
  if (!model) return;
  $("cards").innerHTML = `<h2 style="margin-top:20px">${esc(model.model)} cards — all mandatory</h2>` +
    model.fields.map(f => `
      <label for="c-${esc(f.name)}">${esc(f.name)}</label>
      <div class="q">${esc(f.question)}</div>
      <textarea id="c-${esc(f.name)}" data-card="${esc(f.name)}">${esc((values || {})[f.name] || "")}</textarea>
    `).join("");
}

function collectCards() {
  const cards = {};
  document.querySelectorAll("[data-card]").forEach(el => cards[el.dataset.card] = el.value);
  return cards;
}

$("model").onchange = () => renderCards();
$("clear").onclick = () => {
  $("message").value = ""; $("scenario").value = ""; renderCards();
  $("stages").innerHTML = '<div class="empty">Fill the cards and press Run.</div>'; $("out").innerHTML = "";
};

$("scenario").onchange = e => {
  const scenario = DATA.scenarios.find(s => s.id === e.target.value);
  if (!scenario) return;
  $("message").value = scenario.message;
  const fields = Object.keys(scenario.cards || {});
  const model = DATA.models.find(m => m.fields.length &&
    m.fields.every(f => fields.includes(f.name)) && fields.length === m.fields.length);
  if (model) $("model").value = model.key;
  renderCards(scenario.cards);
};

$("run").onclick = async () => {
  $("run").disabled = true;
  $("stages").innerHTML = '<div class="empty">running the real skill scripts…</div>';
  $("out").innerHTML = "";
  try {
    const result = await (await fetch("/api/run", {
      method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        message: $("message").value, cards: collectCards(),
        model: $("model").value, scenario_id: $("scenario").value || "browser",
      }),
    })).json();
    render(result);
  } catch (err) {
    $("stages").innerHTML = `<div class="empty">${esc(err)}</div>`;
  }
  $("run").disabled = false;
};

function radar(battle) {
  // Four axes, hand-drawn — no chart library, because a CDN would break the
  // zero-dependency claim this page makes.
  const dims = [["logic","Logic"],["eq","EQ"],["response_speed","Speed"],["persuasion","Persuasion"]];
  const S = 200, c = S / 2, R = 66;
  const at = (i, v) => {
    const a = (Math.PI * 2 * i) / dims.length - Math.PI / 2;
    return [c + Math.cos(a) * R * (v / 100), c + Math.sin(a) * R * (v / 100)];
  };
  // Labels sit at radius 128 — the leftmost axis (Persuasion) extends into
  // negative x, so the viewBox is widened beyond the 0-S drawing area to give
  // it room instead of clipping against the SVG viewport edge.
  let svg = `<svg viewBox="-24 0 ${S + 48} ${S}" role="img" aria-label="battle score radar">`;
  [25, 50, 75, 100].forEach(ring => {
    const pts = dims.map((_, i) => at(i, ring).join(",")).join(" ");
    svg += `<polygon points="${pts}" fill="none" stroke="currentColor" opacity=".16"/>`;
  });
  dims.forEach((_, i) => {
    const [x, y] = at(i, 100);
    svg += `<line x1="${c}" y1="${c}" x2="${x}" y2="${y}" stroke="currentColor" opacity=".16"/>`;
  });
  const pts = dims.map(([k], i) => at(i, battle[k]).join(",")).join(" ");
  svg += `<polygon points="${pts}" fill="var(--accent)" fill-opacity=".22"
           stroke="var(--accent)" stroke-width="2"/>`;
  dims.forEach(([k], i) => {
    const [x, y] = at(i, battle[k]);
    svg += `<circle cx="${x}" cy="${y}" r="3" fill="var(--accent)"/>`;
  });
  dims.forEach(([, label], i) => {
    const [x, y] = at(i, 128);
    svg += `<text x="${x}" y="${y + 3}" font-size="10" text-anchor="middle"
             fill="currentColor" opacity=".7">${label}</text>`;
  });
  svg += "</svg>";
  const scores = dims.map(([k, label]) =>
    `<div><span>${label}</span><b>${esc(battle[k])}</b></div>`).join("");
  const tips = (battle.advice || []).map(t => `<div>· ${esc(t)}</div>`).join("");
  return `<div class="radar">${svg}<div class="scores">${scores}</div></div>
          <div class="tips">${tips}</div>`;
}

function render(result) {
  if (result.error) { $("stages").innerHTML = `<div class="empty">${esc(result.error)}</div>`; return; }
  const slowest = Math.max(1, ...result.stages.map(s => s.elapsed_ms || 0));

  $("stages").innerHTML = result.stages.map(s => {
    const cls = String(s.verdict).toUpperCase();
    const vc = vclass(cls);
    const timing = s.elapsed_ms != null
      ? `<span class="meta">exit ${s.exit_code == null ? "—" : s.exit_code} · ${s.elapsed_ms}ms</span>` : "";
    const meta = `<details class="stagemeta"><summary>details</summary>
      <span class="skill">${esc(s.skill)}</span>${timing}</details>`;
    const [tagCls, tagText] = SOURCE_LABEL[s.source] || ["", ""];
    const source = tagText ? `<span class="tag ${tagCls}">${esc(tagText)}</span>` : "";
    const draft = s.draft
      ? `<div class="draft${cls === "BLOCK" ? " struck" : ""}">${esc(s.draft)}</div>` : "";
    const note = s.note ? `<div class="detail meta">${esc(s.note)}</div>` : "";
    const candidates = (s.candidates && cls === "CLARIFY_INTENT")
      ? `<div class="detail">${s.candidates.map(c =>
          `· ${esc(c.routed_agent)} — ${esc(c.use_case)}`).join("<br>")}</div>` : "";
    const critique = s.critique
      ? `<ol class="critique">${s.critique.map(p => `<li>${esc(p)}</li>`).join("")}</ol>` : "";
    const battle = s.battle ? radar(s.battle) : "";
    const bar = s.elapsed_ms
      ? `<div class="bar" style="width:${Math.max(2, (s.elapsed_ms / slowest) * 100)}%"></div>` : "";
    return `<div class="stage ${vc}">
      <div class="top">
        <span class="name">${esc(s.stage)}</span>
        <span class="badge ${vc}">${esc(cls)}</span>
        ${source}
        ${meta}
      </div>
      <div class="detail">${esc(s.detail)}</div>${candidates}${note}${draft}${critique}${battle}${bar}
    </div>`;
  }).join("");

  // Stagger each card in rather than letting the whole run appear at once.
  // Capped delay keeps a long pipeline from feeling sluggish; reduced-motion
  // users get the global transition:none override and see everything instantly.
  const cards = [...$("stages").children];
  cards.forEach((el, i) => { el.style.transitionDelay = `${Math.min(i, 6) * 90}ms`; });
  requestAnimationFrame(() => cards.forEach(el => el.classList.add("in")));

  $("out").innerHTML = result.halted
    ? `<div class="halted">${esc(result.halted)}</div>`
    : (result.delivered
        ? `<div class="delivered"><h3>Delivered to you — verdict ${esc(result.verdict)}</h3>
             <div class="draft">${esc(result.delivered)}</div></div>` : "");
}

boot();
</script>
</body>
</html>
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="WiseTalk zero-dependency browser demo.")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--no-browser", action="store_true", help="do not open a browser window")
    parser.add_argument("--api", action="store_true",
                        help="generate live via the Claude API (needs ANTHROPIC_API_KEY)")
    args = parser.parse_args(argv)

    global LIVE
    LIVE = args.api
    if args.api and not os.environ.get("ANTHROPIC_API_KEY"):
        print("  --api given but ANTHROPIC_API_KEY is unset; Stage 3b will fall back.")

    # Fresh session history each boot, so the growth curve is reproducible.
    SESSION_BATTLES.unlink(missing_ok=True)

    Handler.audit = AuditLog(datetime.now().strftime("%Y%m%dT%H%M%S-web"))
    server = QuietServer((args.host, args.port), Handler)
    url = f"http://{args.host}:{args.port}/"
    print(f"WiseTalk browser demo on {url}")
    print(f"  {len(MODELS)} models · {len(ROUTES)} use cases · {len(SCENARIOS)} example scenarios")
    print(f"  Stage 3b: {'live Claude API' if LIVE else 'recorded replay / structural composition'}")
    print(f"  audit log: {Handler.audit.path}")
    print("  Ctrl-C to stop")
    if not args.no_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
