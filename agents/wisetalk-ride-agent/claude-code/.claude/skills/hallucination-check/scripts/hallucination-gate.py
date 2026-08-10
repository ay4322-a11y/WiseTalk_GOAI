#!/usr/bin/env python3
"""WiseTalk Skill-12: Hallucination Validation Gate (code-first).

Deterministic pre-output validator that decides whether a generated text may be
shown to the user at all. Unlike the legacy hallucination-detect.py (a fail-soft
post-delivery labeler), this script is a GATE:

  PASS   -> all layers clean, deliver immediately
  WARN   -> 1-2 minor flags, wrap values in [AI Inferred: Please verify],
            append disclaimer, deliver with a gap note
  BLOCK  -> 3+ significant inventions, DO NOT deliver; return a
            regeneration_instruction the caller feeds back into generation

Layers:
  1. regex    - numeric invention patterns (percentages, currency, dates,
                years, large numbers) compared against the user's filled data
  2. heuristic- citation/attribution/research patterns (zero LM cost) compared
                against the user's filled data
  3. semantic - only extracted as *candidates* in --mode full: the calling
                agent runs the LM pass over semantic_candidates itself

Modes:
  gate   - validate generated text before it is shown to the user
  input  - validate fill-in card data BEFORE generation (placeholder check +
           heuristic layer; numbers in card data are user values by definition)
  full   - gate + emit semantic_candidates for an optional LM deep-check

Contract: single-line JSON + exit code.
  exit 0  PASS     - clean, safe_text carries the disclaimer
  exit 1  WARN     - flagged + marked, deliverable with a gap note
  exit 2  usage error
  exit 3  BLOCK    - must regenerate; regeneration_instruction populated
  exit 4  fallback - internal error, safe_text unmodified + disclaimer
                     (fail-soft only on internal errors, never on inventions)

Invocation: --data/--data-file MUST come BEFORE --text (--text is REMAINDER).
"""
import argparse
import json
import re
import sys

for stream in (sys.stdin, sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

DISCLAIMER = "\n\n---\n*Disclaimer: This AI-generated communication is for reference only and does not replace independent human judgment. Use responsibly.*"
MARKER = "[AI Inferred: Please verify]"
PLACEHOLDER = "[AI Placeholder]"
BLOCK_THRESHOLD = 3  # 3+ total flags across layers -> BLOCK
MAX_RETRIES = 2      # matches the regeneration loop in the skill/agent bodies

# Layer 1: numeric invention candidates (mirrors hallucination-detect.py).
CANDIDATE_RE = re.compile(
    r"\d+(?:\.\d+)?\s?%"                              # percentages: 15%, 15 %, 3.5%
    r"|[$€£]\s?\d[\d,]*(?:\.\d{1,2})?"                 # currency: $5,000, €12.50
    r"|\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"              # dates: 12/25/2026, 25-12-26
    r"|\b(?:19|20)\d{2}\b"                             # years: 2026, 1999
    r"|\b\d[\d,]{2,}\b"                                # large numbers: 1,200; 5000
)

# Layer 2: heuristic non-numeric fabrication patterns (zero LM cost).
HEURISTIC_RE = re.compile(
    # Authority citations: "According to McKinsey", "Per Harvard", "As stated by Gartner",
    # "according to industry analysts" (lowercase sources, 3+ chars — excludes me/us/my/it)
    r"(?:According to|Per|As (?:stated|reported|noted|confirmed|suggested) by)\s+(?:[A-Z][A-Za-z]+|[a-z]{3,})(?:[ ,](?:[A-Z][A-Za-z]+|[a-z]{3,})){0,4}"
    # Research claims: "Studies show...", "Research indicates..."
    r"|(?:Studies|Research|Surveys|Data)\s+(?:show|shows|indicate|indicates|suggest|suggests|reveal|reveals|confirm|confirms|demonstrate|demonstrates)\b"
    # Person attributions: "Sarah Chen said...", "David Kim argued..."
    r"|[A-Z][a-z]+ [A-Z][a-z]+ (?:said|stated|reported|claimed|argued|noted|explained|announced|mentioned)"
    # Organization/institution claims: "... from/by/at X University / Corp / Inc"
    r"|(?:from|by|at)\s+[A-Z][A-Za-z]+(?:\s[A-Z][A-Za-z]+){0,3}\s+(?:University|Institute|Corporation|Inc\.?|LLC|Ltd\.?|Group|Firm|Foundation)"
    # Quoted speech (20+ chars) — needs the user to have provided it verbatim
    r"|\"[^\"]{20,}\""
    # Stat phrasing: "30% increase / growth / reduction ..."
    r"|\d{1,3}%\s*(?:of|increase|decrease|growth|reduction|improvement|rise|drop|decline)\b"
    # Unsourced projections: "will grow by 30%", "expected to rise 15%" (classic business-comm fabrication)
    r"|(?:will|expected to|projected to|forecast to|is expected to)\s+(?:grow|rise|increase|expand|decline|drop|fall|decrease)\s+(?:by\s+)?\d{1,3}%"
)

# Sentences carrying claims worth an optional LM deep-check (--mode full).
SEMANTIC_CANDIDATE_RE = re.compile(
    r"[^.!?]*(?:" + CANDIDATE_RE.pattern + r"|" + HEURISTIC_RE.pattern + r")[^.!?]*[.!?]"
)


def normalize(value):
    """Canonical form for comparison: digits and dots only."""
    return re.sub(r"[^0-9.]", "", value)


def user_provided_values(data_text):
    """Canonical numeric values the user actually typed."""
    if not data_text:
        return set()
    return {normalize(v) for v in CANDIDATE_RE.findall(data_text)}


def lower_phrases(text):
    """Case-folded phrase set for containment checks (heuristic layer)."""
    if not text:
        return set()
    return {p for p in re.split(r"[;,\n]+", text.lower()) if p.strip()}


def _collect_flags(text, data_text):
    """Collect (start, end, raw, is_numeric) spans from the regex and heuristic
    layers against the ORIGINAL text. Spans are merged when they overlap so the
    marker is applied exactly once. is_numeric records the pattern SOURCE
    (CANDIDATE_RE vs HEURISTIC_RE), not the digit content — stat phrasing and
    projections are heuristic claims even though they contain digits."""
    provided = user_provided_values(data_text)
    user_phrases = lower_phrases(data_text)
    spans = []  # (start, end, raw, is_numeric)

    for m in CANDIDATE_RE.finditer(text):
        if normalize(m.group()) not in provided:
            spans.append((m.start(), m.end(), m.group(), True))

    for m in HEURISTIC_RE.finditer(text):
        claim = m.group(0).strip()
        # A claim the user wrote verbatim (or nearly) is not invented.
        if any(claim.lower() in phrase or phrase in claim.lower() for phrase in user_phrases):
            continue
        spans.append((m.start(), m.end(), claim, False))

    spans.sort()
    merged = []
    for start, end, raw, is_numeric in spans:
        if merged and start < merged[-1][1]:  # overlap -> extend instead of duplicating
            prev_start, prev_end, prev_raw, prev_numeric = merged[-1]
            merged[-1] = (
                prev_start, max(prev_end, end),
                prev_raw if len(prev_raw) >= len(raw) else raw,
                prev_numeric and is_numeric,  # any heuristic contributor -> heuristic
            )
        else:
            merged.append((start, end, raw, is_numeric))
    return merged


def apply_markers(text, spans):
    """Wrap every merged span in the AI-Inferred marker. Returns (text, flagged_values)."""
    flagged = []
    for start, end, raw, _is_numeric in reversed(spans):
        flagged.append(raw)
        text = text[:start] + MARKER + " " + text[start:end] + text[end:]
    flagged.reverse()
    return text, flagged


def find_inventions(text, data_text):
    """Layer 1: numeric invention candidates (CANDIDATE_RE) absent from user data."""
    spans = [s for s in _collect_flags(text, data_text) if s[3]]
    return apply_markers(text, spans)


def find_heuristic_claims(text, data_text):
    """Layer 2: heuristic fabrication patterns (HEURISTIC_RE) absent from user data."""
    spans = [s for s in _collect_flags(text, data_text) if not s[3]]
    return apply_markers(text, spans)


def find_placeholders(text):
    """Input mode: [AI Placeholder] / [AI Inferred] markers are NOT user values."""
    return [m.group(0) for m in re.finditer(r"\[(?:AI Placeholder|AI Inferred[^\]]*)\]", text)]


def append_disclaimer(text):
    """Append the mandatory disclaimer exactly once (idempotent)."""
    return text + DISCLAIMER if not text.endswith(DISCLAIMER) else text


def regeneration_instruction(flagged_values, flagged_claims):
    """Anti-fabrication prompt fed back into generation on BLOCK."""
    parts = []
    if flagged_values:
        parts.append("invented data: " + ", ".join(flagged_values))
    if flagged_claims:
        parts.append("claims not present in the user's filled data: " + "; ".join(flagged_claims))
    if not parts:
        parts.append("content not traceable to the user's filled data")
    return ("Remove the following " + "; ".join(parts)
            + ". Every claim in the output must come from the user's filled data "
              "— no invented numbers, statistics, quotes, research citations, "
              "person attributions, or organization claims.")


def run_gate(text, data_text, force_warn=False):
    """Layers 1+2 against a generated text. Returns result dict (see module docstring)."""
    try:
        spans = _collect_flags(text, data_text)
        numeric = [s for s in spans if s[3]]
        heuristic = [s for s in spans if not s[3]]
        flagged_values = [s[2] for s in numeric]
        flagged_claims = [s[2] for s in heuristic]
        # single marker pass over the merged spans — one marker per flagged region
        marked_text, _ = apply_markers(text, spans)
        total = len(flagged_values) + len(flagged_claims)
    except Exception as exc:  # fail-soft on internal errors only
        return {
            "status": "fallback", "verdict": "WARN", "reason": str(exc),
            "regex_flagged": 0, "regex_flagged_values": [],
            "heuristic_flagged": 0, "heuristic_flagged_claims": [],
            "placeholder_flagged": [], "semantic_flagged": 0, "semantic_flagged_claims": [],
            "semantic_candidates": [],
            "safe_text": append_disclaimer(text), "disclaimer_appended": True,
            "regeneration_instruction": None,
            "gap_note": "Hallucination gate could not run ({0}); delivered WARN with disclaimer.".format(exc),
        }

    verdict = "PASS" if total == 0 else ("WARN" if total < BLOCK_THRESHOLD else "BLOCK")
    if verdict == "BLOCK" and force_warn:
        verdict = "WARN"
        gap_note = "BLOCK downgraded to WARN after {0} regeneration retries exhausted.".format(MAX_RETRIES)
    else:
        gap_note = None

    if verdict == "BLOCK":
        return {
            "status": "blocked", "verdict": verdict,
            "regex_flagged": len(flagged_values), "regex_flagged_values": flagged_values,
            "heuristic_flagged": len(flagged_claims), "heuristic_flagged_claims": flagged_claims,
            "placeholder_flagged": [], "semantic_flagged": 0, "semantic_flagged_claims": [],
            "semantic_candidates": [],
            "safe_text": text, "disclaimer_appended": False,
            "regeneration_instruction": regeneration_instruction(flagged_values, flagged_claims),
            "gap_note": None,
        }

    return {
        "status": "ok", "verdict": verdict,
        "regex_flagged": len(flagged_values), "regex_flagged_values": flagged_values,
        "heuristic_flagged": len(flagged_claims), "heuristic_flagged_claims": flagged_claims,
        "placeholder_flagged": [], "semantic_flagged": 0, "semantic_flagged_claims": [],
        "semantic_candidates": [],
        "safe_text": append_disclaimer(marked_text), "disclaimer_appended": True,
        "regeneration_instruction": None,
        "gap_note": gap_note,
    }


def run_input(text):
    """Input mode: validate fill-in card data BEFORE generation.
    Numbers in card data are user values by definition — only the placeholder
    check and the heuristic layer apply."""
    try:
        placeholders = find_placeholders(text)
        marked_text, flagged_claims = find_heuristic_claims(text, "")
        # In card data every number is user-provided; only non-numeric claim
        # patterns and placeholder markers indicate risk.
        total = len(flagged_claims) + len(placeholders)
    except Exception as exc:
        return {
            "status": "fallback", "verdict": "WARN", "reason": str(exc),
            "regex_flagged": 0, "regex_flagged_values": [],
            "heuristic_flagged": 0, "heuristic_flagged_claims": [],
            "placeholder_flagged": [], "semantic_flagged": 0, "semantic_flagged_claims": [],
            "semantic_candidates": [],
            "safe_text": text, "disclaimer_appended": False,
            "regeneration_instruction": None,
            "gap_note": "Input gate could not run ({0}); proceed but confirm with the user.".format(exc),
        }

    verdict = "PASS" if total == 0 else ("WARN" if total < BLOCK_THRESHOLD else "BLOCK")
    instruction = None
    if verdict != "PASS":
        parts = []
        if flagged_claims:
            parts.append("claims that look fabricated: " + "; ".join(flagged_claims))
        if placeholders:
            parts.append("placeholder markers that are not real user values: " + ", ".join(placeholders))
        instruction = ("The fill-in card data contains " + "; ".join(parts)
                       + ". Ask the user to provide real values before generation.")
    return {
        "status": "ok" if verdict == "PASS" else "flagged", "verdict": verdict,
        "regex_flagged": 0, "regex_flagged_values": [],
        "heuristic_flagged": len(flagged_claims), "heuristic_flagged_claims": flagged_claims,
        "placeholder_flagged": placeholders, "semantic_flagged": 0, "semantic_flagged_claims": [],
        "semantic_candidates": [],
        "safe_text": text, "disclaimer_appended": False,
        "regeneration_instruction": instruction,
        "gap_note": None,
    }


def extract_semantic_candidates(text):
    """--mode full: sentences carrying claims for the optional LM deep-check."""
    return [s.strip() for s in SEMANTIC_CANDIDATE_RE.findall(text) if s.strip()]


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="WiseTalk Skill-12: hallucination validation gate",
        add_help=False,
    )
    parser.add_argument("--mode", choices=["gate", "input", "full"], default="gate")
    parser.add_argument("--force-warn", action="store_true",
                        help="downgrade a BLOCK verdict to WARN (retries exhausted)")
    parser.add_argument("--data", help="the user's original filled values (quoted)")
    parser.add_argument("--data-file", help="path to a UTF-8 file with the filled values")
    parser.add_argument("--text", nargs=argparse.REMAINDER, help="the generated text (unquoted)")
    parser.add_argument("--help", action="help", help="show this help")
    args = parser.parse_args(argv)

    text = " ".join(args.text).strip() if args.text else None
    if text is None:
        text = sys.stdin.read().strip() if not sys.stdin.isatty() else None

    try:
        data = args.data
        if data is None and args.data_file:
            with open(args.data_file, "r", encoding="utf-8") as fh:
                data = fh.read()
    except Exception as exc:
        data = None

    # Input mode validates the card data itself: --data / --data-file / --text
    # all carry the cards; the caller passes whichever channel is convenient.
    if args.mode == "input":
        if text is None and data:
            text = data
        if text is None:
            sys.stderr.write("usage: hallucination-gate.py --mode input --data <card values> | --data-file <path> | --text <cards>\n")
            return 2
        result = run_input(text)
    else:
        if not text:
            sys.stderr.write("usage: hallucination-gate.py --mode gate|full [--data <filled values>] [--data-file <path>] [--force-warn] --text <text> | stdin fallback\n")
            return 2
        result = run_gate(text, data or "", force_warn=args.force_warn)
        if args.mode == "full":
            result["semantic_candidates"] = extract_semantic_candidates(text)

    print(json.dumps(result, ensure_ascii=False))
    return {"PASS": 0, "WARN": 1, "BLOCK": 3}.get(result["verdict"], 4)


if __name__ == "__main__":
    sys.exit(main())
