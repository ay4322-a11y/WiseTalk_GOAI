#!/usr/bin/env python3
"""WiseTalk Skill-12: AI Hallucination Self-Check & Disclaimer Appender (code-first, fail-soft).

Deterministic post-validator for generated communication text:
1. Extract invention candidates (percentages, currency amounts, dates, years,
   large numbers) from the generated final text.
2. Any candidate NOT present in the user's original filled data (passed as
   --data) gets wrapped token-level with the [AI Inferred: Please verify] marker.
3. Append the mandatory disclaimer if it is not already the text's suffix
   (idempotent).
4. Fail-soft: an internal error returns the original text unmodified
   (status "fallback") — this skill must never be the reason delivery stops.

Contract: single-line JSON + exit code.
  exit 0  status "ok"      — safe_text processed (wrapped + disclaimer)
  exit 1  status "fallback" — safe_text = original text unmodified (wrap skipped; disclaimer still appended)
  exit 2  usage error       — missing input; the agent delivers the text with a gap note

Invocation: --data MUST be passed BEFORE --text (--text consumes everything after it).
"""
import argparse
import json
import re
import sys

# UTF-8 everywhere: argv through some shells (e.g. MSYS/Git Bash on Windows)
# is converted to the ANSI codepage and mangles non-ASCII — stdin/stdout pipes
# stay byte-clean, so the script's own I/O must be explicitly UTF-8.
for stream in (sys.stdin, sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass  # Python < 3.7 or a non-reconfigurable stream

DISCLAIMER = "\n\n---\n*Disclaimer: This AI-generated communication is for reference only and does not replace independent human judgment. Use responsibly.*"
MARKER = "[AI Inferred: Please verify]"

# Invention candidates (deterministic, language-independent numeric patterns).
CANDIDATE_RE = re.compile(
    r"\d+(?:\.\d+)?\s?%"                              # percentages: 15%, 15 %, 3.5%
    r"|[$€£]\s?\d[\d,]*(?:\.\d{1,2})?"                 # currency: $5,000, €12.50
    r"|\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"              # dates: 12/25/2026, 25-12-26
    r"|\b(?:19|20)\d{2}\b"                             # years: 2026, 1999
    r"|\b\d[\d,]{2,}\b"                                # large numbers: 1,200; 5000
)


def normalize(value):
    """Canonical form for comparison: digits and dots only (strip $ , % / - spaces)."""
    return re.sub(r"[^0-9.]", "", value)


def user_values(data_text):
    """The set of canonical values the user actually provided, scanned with the same patterns."""
    if not data_text:
        return set()
    return {normalize(v) for v in CANDIDATE_RE.findall(data_text)}


def wrap_inventions(text, data_text):
    """Return (wrapped_text, flagged_count, flagged_values). Raises on unexpected errors (fail-soft)."""
    provided = user_values(data_text)
    matches = [(m.start(), m.end(), m.group()) for m in CANDIDATE_RE.finditer(text)]
    flagged = []
    for start, end, raw in reversed(matches):
        if normalize(raw) not in provided:
            flagged.append(raw)
            text = text[:start] + MARKER + " " + text[start:end] + text[end:]
    flagged.reverse()  # restore document order for reporting
    return text, len(flagged), flagged


def append_disclaimer(text):
    """Append the mandatory disclaimer exactly once (idempotent)."""
    return text + DISCLAIMER if not text.endswith(DISCLAIMER) else text


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="WiseTalk Skill-12: hallucination self-check + disclaimer appender",
        add_help=False,
    )
    # Order matters: --data/--data-file must come BEFORE --text (REMAINDER consumes the rest of argv).
    parser.add_argument("--data", help="the user's original filled values (quoted)")
    parser.add_argument("--data-file", help="path to a UTF-8 file with the filled values (encoding-safe; preferred for non-ASCII)")
    parser.add_argument("--text", nargs=argparse.REMAINDER, help="the generated final text (unquoted)")
    parser.add_argument("--help", action="help", help="show this help")
    args = parser.parse_args(argv)

    text = " ".join(args.text).strip() if args.text else None
    if text is None:
        text = sys.stdin.read().strip() if not sys.stdin.isatty() else None
    if not text:
        sys.stderr.write("usage: hallucination-detect.py --text <final text> [--data <filled values>] [--data-file <path>] | stdin fallback\n")
        return 2

    try:
        data = args.data
        if data is None and args.data_file:
            with open(args.data_file, "r", encoding="utf-8") as fh:
                data = fh.read()
        safe_text, flagged_count, flagged_values = wrap_inventions(text, data)
        status = "ok"
        reason = None
    except Exception as exc:  # fail-soft: never block delivery
        safe_text, flagged_count, flagged_values = text, 0, []
        status = "fallback"
        reason = str(exc)

    safe_text = append_disclaimer(safe_text)
    # Verdict parity with the hallucination-gate.py contract: 0 -> PASS,
    # 1-2 -> WARN, 3+ -> BLOCK. The legacy fail-soft exit codes are unchanged
    # (0=ok, 1=fallback) — the verdict field is additive, for callers that
    # want the gate-style decision without the new gate script.
    verdict = "PASS" if flagged_count == 0 else ("WARN" if flagged_count < 3 else "BLOCK")
    result = {
        "status": status,
        "verdict": verdict,
        "safe_text": safe_text,
        "inventions_flagged": flagged_count,
        "flagged_values": flagged_values,
        "disclaimer_appended": safe_text.endswith(DISCLAIMER),
        "reason": reason,
    }
    print(json.dumps(result, ensure_ascii=False))
    return 0 if status == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
