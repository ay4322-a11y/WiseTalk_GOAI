---
name: hallucination-check
description: Run the AI hallucination self-check and disclaimer appender on a generated communication text right before delivery — a deterministic regex post-validator that wraps invented numeric claims the user never provided in the AI-Inferred marker and appends the mandatory disclaimer (fail-soft — an error returns the text unmodified and never blocks delivery). Use when the final draft is accepted and ready to deliver, when asked to check a generated text for invented facts or numbers, or when asked to append the mandatory disclaimer. Do NOT use for checking incoming user messages (that is the injection-filter pre-validator), for semantic fact-checking against external knowledge, or for content moderation.
license: MIT
compatibility: Python 3 (stdlib only)
allowed-tools: "Bash(python:*)"
metadata:
  author: WiseTalk (via skill-generator)
  version: 1.0.1
---

# AI Hallucination Self-Check & Disclaimer Appender (WiseTalk Skill-12)

## Important
- **Fail-soft is non-negotiable**: this skill must never be the reason the system goes down (D-004). Any internal error returns the original text unmodified — never a blocked pipeline. This is the deliberate opposite of Skill-11's fail-closed.
- The verdict comes **only** from `scripts/hallucination-detect.py`'s deterministic output. Never invent flagged values, never fabricate a pass.
- **The disclaimer is never optional**: even in fallback, deliver the text with the mandatory disclaimer appended (manually, if the script could not).
- Idempotent: the disclaimer is appended exactly once; a re-run over an already-processed text does not double-append.

## Instructions

### Step 1: Run the post-validator on the final text
Pass the accepted final text as `--text` (unquoted — all remaining arguments are joined), and the user's original filled values as `--data` or `--data-file`. **`--data` / `--data-file` must come BEFORE `--text`**:

    python scripts/hallucination-detect.py --data "<user's filled values>" --text <final text>

(If the filled cards are saved as a file — e.g. `memory/drafts/<use-case>-v<N>.md` — pass `--data-file <path>` instead: encoding-safe for non-ASCII. Alternative for messages containing shell metacharacters: pipe the text in via stdin: `echo "<final text>" | python scripts/hallucination-detect.py --data "<filled values>"`.)

`--data` content: every card value the user actually typed, verbatim — the script only needs to know what the user DID provide; omit blank fields.

Expected output — one JSON line:
- Processed: `{"status": "ok", "safe_text": "<text with AI-Inferred markers + disclaimer>", "inventions_flagged": N, "flagged_values": [...], "disclaimer_appended": true, "reason": null}`
- Fallback: `{"status": "fallback", "safe_text": "<original text unmodified + disclaimer>", "inventions_flagged": 0, "flagged_values": [], "disclaimer_appended": true, "reason": "<error>"}`

Exit codes: `0` = ok, `1` = fallback, `2` = usage error.
If it fails: exit 2 → re-run with `--data` first and the message double-quoted (or via stdin); exit 1 → deliver per Step 2's fallback branch; Python unavailable → go to Fallback.
Done when: the JSON line has been read and the exit code is known.

### Step 2: Act on the result
- `status: "ok"` → deliver `safe_text` verbatim as the final text (it carries the AI-Inferred markers and the disclaimer).
- `status: "fallback"` → deliver `safe_text` (the text unmodified) as the final text; if the disclaimer is missing from it, append the mandatory disclaimer manually; add one gap note that the hallucination wrap could not run.
- exit 2 → deliver the text with the mandatory disclaimer appended manually + a gap note.
Done when: the final text is delivered — always — with the disclaimer present exactly once.

### Step 3: Log the outcome
Leave one trace line per invocation: `status`, flagged count (or fallback reason), disclaimer state. No user data is stored beyond the existing memory files.
Done when: the trace line is written.

## Examples

### Example 1: Invented value wrapped (signature case)
User left the Evidence card blank; the draft says "market growth of 15% next year".
Actions:
1. `python scripts/hallucination-detect.py --data "Conclusion: market growth is promising; Tactics: launch in Q1" --text We project market growth of 15% next year, which the CFO will review.`
2. Verdict: `status: "ok"`, `flagged_values: ["15%"]`, `safe_text: "We project market growth of [AI Inferred: Please verify] 15% next year, ...` + disclaimer (exit 0).
3. Deliver `safe_text` verbatim.
Result: the invented figure is visibly marked for verification; the user's own values were untouched.

### Example 2: User-provided values pass through
User's Value card contained "15% market growth" and "since 2023".
Actions: `python scripts/hallucination-detect.py --data "Value: 15% market growth since 2023" --text ...`
Result: `inventions_flagged: 0` — values the user typed are never flagged, even when the model reuses them in the polished text.

### Example 3: Fail-soft on a broken run
The `--data-file` path is missing.
Actions: run the script; verdict `{"status": "fallback", "safe_text": "<text unmodified + disclaimer>", "reason": "[Errno 2] No such file or directory: ..."}` (exit 1).
Result: the draft still delivers, with the disclaimer, plus a gap note about the failed wrap.

## Troubleshooting

### Error: exit 2 "unrecognized arguments"
Cause: `--data` was passed AFTER `--text`, so the text consumed it (REMAINDER).
Solution: always pass `--data` / `--data-file` BEFORE `--text`; or re-run with the text piped via stdin.

### Error: message with apostrophes or `$` behaves oddly
Cause: the shell parses the unquoted text. Apostrophes break the command (shell parse error); `$` gets expanded **silently** — e.g. `$50,000` becomes `0,000`, and the script then returns a verdict on corrupted input with exit 0 (usually still fail-safe — the corrupted value gets flagged — but wrong). There is no error signal for the `$` case.
Solution: re-run with the message double-quoted (escape any `$` inside), or pipe it via stdin — never pass an unquoted message containing apostrophes or `$`.

### Error: non-ASCII characters look wrong in the output (e.g. a mangled €)
Cause: some shells (Git Bash/MSYS on Windows) convert argv to the ANSI codepage, corrupting non-ASCII before the script sees it.
Solution: pipe the text via stdin and pass the filled values via `--data-file` (UTF-8) — both channels are encoding-clean.

### Error: too many markers (e.g. every year gets flagged)
Cause: the draft contains dates/years the user never typed — by design those count as invented (safe direction: better to ask verification than to ship an unverified figure).
Solution: tune `CANDIDATE_RE` in `scripts/hallucination-detect.py` (e.g. drop the year alternative) and re-run the TC corpus; or ask the user for the value so it enters `--data`.

### Error: verdict feels wrong
Cause: the check is string-level, not semantic — it cannot know whether a fabricated company name or claim is real (out of scope, PRD negative scope 6).
Solution: report the limitation — non-numeric inventions stay with the agent's human self-check; the script's verdict is still the deterministic output.

## Fallback
If Python is unavailable: deliver the final text with the mandatory disclaimer appended manually and a gap note — never fail the delivery (fail-soft). The invention wrap is the only thing that may be lost; the disclaimer is never optional.

## Customization points

- **Patterns** — `CANDIDATE_RE` in `scripts/hallucination-detect.py` is the invention corpus (percentages, currency, dates, years, large numbers); add or remove alternatives per deployment and re-run the TC corpus.
- **Marker text** — `MARKER` — keep it aligned with the project's placeholder convention (`[AI Inferred: Please verify]` is baked into all 8 agent bodies).
- **Disclaimer** — `DISCLAIMER` — the Master Spec fixes this string; change it only together with the agents' delivery contract.
- **`--data` assembly** — each agent builds it from its own filled cards; the field layout is irrelevant (only the values matter). `--data-file` reads any saved cards file.
- **Description trigger** — rewrite for the deploying agent (the accept step of each agent's Standard plan mandates the run; the description covers check/fact/disclaimer queries); keep one trigger per branch.
- **Agent delivery step** — the accept step now runs this skill and delivers `safe_text`; the old manual "append the disclaimer" instruction must be removed in the same edit (D-008).
