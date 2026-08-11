#!/usr/bin/env python3
"""WiseTalk browser demo — zero-dependency, stdlib http.server only.

    python demo_server.py            # http://localhost:8000
    python demo_server.py --port 9000

Renders the Master Spec's Stage 2 "mandatory fill-in cards" UI — the non-chatbox
interface the spec calls for — and runs a submitted set of cards through the real
pipeline, showing every gate verdict as it happens.

Shares its pipeline primitives with demo.py (same scripts, same routing map, same
catalog, same audit log). Generation replays a recorded draft unless
ANTHROPIC_API_KEY is set, and the page labels which one it used.

No pip install, no framework, no build step, no CDN — the page is served from this
file and nothing is fetched from the network.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

import demo
from demo import (
    BATTLE_SCORES, GROWTH_TRENDS, HALLUCINATION_GATE, DFA_FILTER, MAX_RETRIES,
    AuditLog, find_model, parse_catalog, parse_routing_map, route, run_script,
)

MODELS = parse_catalog()
ROUTES = parse_routing_map()
SCENARIOS = {s["id"]: s for s in demo.load_scenarios(None)}


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
    drafts = [scenario.get("recorded_draft", "")] + scenario.get("recorded_regenerations", [])
    drafts = [d for d in drafts if d] or [
        "\n\n".join(f"{field}: {cards[field]}" for field, _ in model_info["fields"] if cards.get(field))
    ]
    hint, delivered, final_verdict = None, None, "ERROR"

    for attempt in range(MAX_RETRIES + 1):
        source = "recorded"
        try:
            draft = demo.generate_live(model_info, decision["use_case"], cards,
                                       None if attempt == 0 else hint)
            source = "live"
        except Exception:
            draft = drafts[min(attempt, len(drafts) - 1)]

        last = attempt == MAX_RETRIES
        args = ["--data", card_text] + (["--force-warn"] if last else []) + ["--text", draft]
        code, payload, _, ms = run_script(HALLUCINATION_GATE, args)
        verdict = payload["verdict"] if payload else "ERROR"
        flagged = ((payload or {}).get("regex_flagged_values", [])
                   + (payload or {}).get("heuristic_flagged_claims", []))
        audit.record(scenario=scenario_id, stage="3b", skill="Skill-12", verdict=verdict,
                     exit_code=code, elapsed_ms=ms, retry=attempt, mode="gate",
                     generation_source=source, flagged=flagged)
        add(f"Stage 3b · attempt {attempt + 1}", "Skill-7 + Skill-12 gate", verdict,
            "clean — cleared for delivery" if verdict == "PASS"
            else ("blocked before you saw it: " + ", ".join(str(f) for f in flagged) if verdict == "BLOCK"
                  else "delivered with inference markers: " + ", ".join(str(f) for f in flagged)),
            exit_code=code, elapsed_ms=ms, draft=draft, source=source, flagged=flagged)

        if verdict == "BLOCK":
            hint = (payload or {}).get("regeneration_instruction", "")
            continue
        delivered, final_verdict = (payload or {}).get("safe_text", draft), verdict
        break

    return {"stages": stages, "delivered": delivered, "verdict": final_verdict, "halted": None}


def growth_data() -> dict:
    if not BATTLE_SCORES.exists():
        return {"message": "No history available yet"}
    _code, payload, raw, _ms = run_script(GROWTH_TRENDS, ["--scores", str(BATTLE_SCORES)])
    return payload or {"message": raw.strip()}


# --------------------------------------------------------------------------
# HTTP
# --------------------------------------------------------------------------

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
            })
        elif path == "/api/growth":
            self._json(growth_data())
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
  :root {
    --bg:#f7f7f5; --panel:#fff; --ink:#1a1a1a; --muted:#6b6b6b; --line:#e2e2de;
    --accent:#1f5fbf; --pass:#1a7f4b; --warn:#a86a00; --block:#b3261e;
  }
  @media (prefers-color-scheme: dark) {
    :root { --bg:#14140f; --panel:#1e1e1a; --ink:#f0efe9; --muted:#a3a29a; --line:#33332c;
            --accent:#78a9ff; --pass:#5cc98c; --warn:#e0a34a; --block:#f08a80; }
  }
  * { box-sizing:border-box; }
  body { margin:0; background:var(--bg); color:var(--ink);
         font:15px/1.55 ui-sans-serif,-apple-system,"Segoe UI",system-ui,sans-serif; }
  header { padding:24px 20px 12px; max-width:1080px; margin:0 auto; }
  h1 { font-size:22px; margin:0 0 4px; letter-spacing:-.01em; }
  .sub { color:var(--muted); font-size:14px; }
  main { max-width:1080px; margin:0 auto; padding:12px 20px 60px;
         display:grid; grid-template-columns:minmax(320px,1fr) minmax(320px,1.1fr); gap:20px; }
  @media (max-width:860px) { main { grid-template-columns:1fr; } }
  .panel { background:var(--panel); border:1px solid var(--line); border-radius:10px; padding:16px; }
  h2 { font-size:13px; text-transform:uppercase; letter-spacing:.07em; color:var(--muted);
       margin:0 0 12px; font-weight:600; }
  label { display:block; font-size:13px; font-weight:600; margin:14px 0 2px; }
  .q { font-size:12.5px; color:var(--muted); margin-bottom:5px; }
  textarea, input, select { width:100%; background:var(--bg); color:var(--ink);
    border:1px solid var(--line); border-radius:6px; padding:8px 9px; font:inherit; font-size:14px; }
  textarea { min-height:60px; resize:vertical; }
  .row { display:flex; gap:8px; align-items:center; margin-bottom:10px; flex-wrap:wrap; }
  button { background:var(--accent); color:#fff; border:0; border-radius:6px;
           padding:9px 16px; font:inherit; font-weight:600; cursor:pointer; }
  button.ghost { background:transparent; color:var(--accent); border:1px solid var(--line); }
  button:disabled { opacity:.5; cursor:default; }
  .stage { border-left:3px solid var(--line); padding:9px 0 9px 12px; margin-bottom:4px; }
  .stage .top { display:flex; gap:8px; align-items:baseline; flex-wrap:wrap; }
  .name { font-weight:600; font-size:13.5px; }
  .skill { color:var(--muted); font-size:12.5px; font-family:ui-monospace,Menlo,Consolas,monospace; }
  .badge { font-size:11px; font-weight:700; letter-spacing:.04em; padding:1px 7px;
           border-radius:20px; border:1px solid currentColor; }
  .PASS,.SAFE,.OK,.SUCCESS { color:var(--pass); }
  .WARN,.CLARIFY_INTENT,.FORCE_FILL,.FALLBACK { color:var(--warn); }
  .BLOCK,.BLOCKED,.ERROR { color:var(--block); }
  .detail { font-size:13px; color:var(--muted); margin-top:3px; }
  .draft { white-space:pre-wrap; background:var(--bg); border:1px solid var(--line);
           border-radius:6px; padding:10px; margin-top:7px; font-size:13px; }
  .struck { text-decoration:line-through; opacity:.55; }
  .meta { font-size:11.5px; color:var(--muted); font-family:ui-monospace,Menlo,Consolas,monospace; }
  .halted { border:1px dashed var(--line); border-radius:6px; padding:10px;
            margin-top:10px; font-size:13.5px; color:var(--warn); }
  .delivered { border:1px solid var(--pass); border-radius:8px; padding:12px; margin-top:12px; }
  .delivered h3 { margin:0 0 7px; font-size:13px; color:var(--pass);
                  text-transform:uppercase; letter-spacing:.06em; }
  .empty { color:var(--muted); font-size:13.5px; }
  svg { width:100%; height:auto; }
  .tag { font-size:11px; padding:1px 6px; border-radius:4px; border:1px solid var(--line);
         color:var(--muted); }
</style>
</head>
<body>
<header>
  <h1>WiseTalk — mandatory fill-in cards, and the gates behind them</h1>
  <div class="sub">Stage&nbsp;2 of the Master Spec: the interface is cards, not a chatbox.
    Fill them, submit, and watch every gate verdict. Nothing here is fetched from the network.</div>
</header>
<main>
  <section class="panel">
    <h2>Your scenario</h2>
    <div class="row">
      <select id="scenario" style="flex:1 1 240px"><option value="">— load an example —</option></select>
      <select id="model" style="flex:1 1 160px"></select>
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
    <div class="panel" style="margin-top:20px">
      <h2>Skill-10 · growth curve</h2>
      <div id="growth" class="empty">loading…</div>
    </div>
  </section>
</main>
<script>
let DATA = {models: [], scenarios: []};
const $ = id => document.getElementById(id);
const esc = s => String(s == null ? "" : s).replace(/[&<>]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));

async function boot() {
  DATA = await (await fetch("/api/models")).json();
  $("model").innerHTML = DATA.models.map(m =>
    `<option value="${m.key}">${esc(m.model)} — ${esc(m.agent)}</option>`).join("");
  $("scenario").innerHTML += DATA.scenarios.map(s =>
    `<option value="${s.id}">${esc(s.title)}</option>`).join("");
  renderCards();
  drawGrowth();
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

function render(result) {
  if (result.error) { $("stages").innerHTML = `<div class="empty">${esc(result.error)}</div>`; return; }
  $("stages").innerHTML = result.stages.map(s => {
    const cls = String(s.verdict).toUpperCase();
    const timing = s.elapsed_ms != null
      ? `<span class="meta">exit ${s.exit_code == null ? "—" : s.exit_code} · ${s.elapsed_ms}ms</span>` : "";
    const source = s.source
      ? `<span class="tag">${s.source === "live" ? "live model output" : "recorded draft (replay)"}</span>` : "";
    const draft = s.draft
      ? `<div class="draft${cls === "BLOCK" ? " struck" : ""}">${esc(s.draft)}</div>` : "";
    const note = s.note ? `<div class="detail meta">${esc(s.note)}</div>` : "";
    const candidates = (s.candidates && cls === "CLARIFY_INTENT")
      ? `<div class="detail">${s.candidates.map(c =>
          `· ${esc(c.routed_agent)} — ${esc(c.use_case)}`).join("<br>")}</div>` : "";
    return `<div class="stage">
      <div class="top">
        <span class="name">${esc(s.stage)}</span>
        <span class="badge ${cls}">${esc(cls)}</span>
        <span class="skill">${esc(s.skill)}</span>${timing}${source}
      </div>
      <div class="detail">${esc(s.detail)}</div>${candidates}${note}${draft}
    </div>`;
  }).join("");

  $("out").innerHTML = result.halted
    ? `<div class="halted">${esc(result.halted)}</div>`
    : (result.delivered
        ? `<div class="delivered"><h3>Delivered to you — verdict ${esc(result.verdict)}</h3>
             <div class="draft">${esc(result.delivered)}</div></div>` : "");
}

async function drawGrowth() {
  const data = await (await fetch("/api/growth")).json();
  const trend = data.trend_data;
  if (!trend || !trend.dates || !trend.dates.length) {
    $("growth").textContent = data.message || "No history available yet";
    return;
  }
  const series = [["logic","Logic"],["eq","EQ"],["response_speed","Speed"],["persuasion","Persuasion"]];
  const W = 520, H = 190, P = 34, n = Math.max(trend.dates.length, 2);
  const x = i => P + (W - 2 * P) * (n === 1 ? 0.5 : i / (n - 1));
  const y = v => H - P - (H - 2 * P) * (v / 100);
  const colors = ["#1f5fbf", "#1a7f4b", "#a86a00", "#b3261e"];
  let svg = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="battle score trend">`;
  [0, 50, 100].forEach(v => {
    svg += `<line x1="${P}" y1="${y(v)}" x2="${W - P}" y2="${y(v)}" stroke="currentColor" opacity=".15"/>`;
    svg += `<text x="6" y="${y(v) + 4}" font-size="10" fill="currentColor" opacity=".55">${v}</text>`;
  });
  series.forEach(([key, label], si) => {
    const values = trend[key] || [];
    if (!values.length) return;
    const points = values.map((v, i) => `${x(i)},${y(v)}`).join(" ");
    svg += values.length > 1
      ? `<polyline points="${points}" fill="none" stroke="${colors[si]}" stroke-width="2"/>`
      : "";
    values.forEach((v, i) => { svg += `<circle cx="${x(i)}" cy="${y(v)}" r="3.5" fill="${colors[si]}"/>`; });
    svg += `<text x="${W - P + 4}" y="${y(values[values.length - 1]) + 4}" font-size="10" fill="${colors[si]}">${label}</text>`;
  });
  trend.dates.forEach((d, i) => {
    svg += `<text x="${x(i)}" y="${H - 12}" font-size="10" text-anchor="middle" fill="currentColor" opacity=".55">${d}</text>`;
  });
  svg += "</svg>";
  const weak = data.weak_point ? `<div class="detail">weakest dimension: <b>${esc(data.weak_point)}</b></div>` : "";
  $("growth").innerHTML = svg + weak;
  $("growth").className = "";
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
    args = parser.parse_args(argv)

    Handler.audit = AuditLog(datetime.now().strftime("%Y%m%dT%H%M%S-web"))
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    url = f"http://{args.host}:{args.port}/"
    print(f"WiseTalk browser demo on {url}")
    print(f"  {len(MODELS)} models · {len(ROUTES)} use cases · {len(SCENARIOS)} example scenarios")
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
