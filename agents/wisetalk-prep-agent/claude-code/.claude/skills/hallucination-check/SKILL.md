---
name: hallucination-check
description: Validate a generated communication text BEFORE any of it is shown to the user — a deterministic pre-output gate (Skill-12) that returns a PASS / WARN / BLOCK verdict: BLOCK triggers automatic regeneration with anti-fabrication constraints (max 2 retries), WARN wraps invented claims in the AI-Inferred marker and appends the mandatory disclaimer, PASS delivers clean text. Also validates fill-in card data before generation (--mode input). Use inside language-polishing after every synthesis, on the accepted draft for the final delivery wrap, and on filled cards before generating. Do NOT use for checking incoming user messages (that is the injection-filter pre-validator), for semantic fact-checking against external knowledge, or for content moderation.
license: MIT
compatibility: Python 3 (stdlib only)
allowed-tools: "Bash(python:*)"
metadata:
  author: WiseTalk (via skill-generator)
  version: 2.0.0
---

# AI Hallucination Validation Gate & Disclaimer Appender (WiseTalk Skill-12)

## Important

- **Gate behavior, not labeling:** the verdict decides whether text may be shown at all.
  - `PASS` — all layers clean → deliver immediately.
  - `WARN` — 1–2 minor flags → wrap the invented values in `[AI Inferred: Please verify]`, append the disclaimer, deliver with a gap note.
  - `BLOCK` — 3+ significant inventions → **do NOT deliver**; return the `regeneration_instruction` to the caller (Skill-7), which regenerates with the anti-fabrication constraint, then re-runs the gate (max 2 retries; on exhaustion, re-run with `--force-warn` and deliver marked).
- **Fail-soft on internal errors only** (D-004): a script crash falls back to `WARN` + gap note and never loses the text. Fail-**closed** on detected inventions: BLOCK must never be delivered. This is the deliberate opposite of the legacy fail-soft labeler.
- **The disclaimer is never optional**: it is appended in every deliverable verdict (PASS/WARN/fallback), exactly once (idempotent).
- **Three call points** (per the Master Spec): (1) `--mode input` on fill-in card data before Skill-7 generates; (2) `--mode gate` inside Skill-7 on every draft before it reaches the user; (3) the final delivery wrap on the accepted text.
- The verdict comes **only** from the scripts' deterministic output. Never invent flagged values, never fabricate a pass.

## Instructions

### Step 1: Run the gate on the generated text
Pass the generated text as `--text` (unquoted — all remaining arguments are joined), and the user's original filled values as `--data` or `--data-file`. **`--data` / `--data-file` must come BEFORE `--text`**:

    python scripts/hallucination-gate.py --mode gate --data "<user's filled values>" --text <generated text>

(If the filled cards are saved as a file — e.g. `memory/drafts/<use-case>-v<N>.md` — pass `--data-file <path>` instead: encoding-safe for non-ASCII. Alternative for messages containing shell metacharacters: pipe the text in via stdin: `echo "<generated text>" | python scripts/hallucination-gate.py --mode gate --data "<filled values>"`.)

`--data` content: every card value the user actually typed, verbatim — the script only needs to know what the user DID provide; omit blank fields.

Expected output — one JSON line with `verdict`, `regex_flagged(_values)`, `heuristic_flagged(_claims)`, `semantic_candidates`, `safe_text`, `regeneration_instruction`, `gap_note`, `disclaimer_appended`.

Exit codes: `0` = PASS, `1` = WARN, `2` = usage error, `3` = BLOCK, `4` = fallback.
Done when: the JSON line has been read and the exit code is known.

### Step 2: Act on the verdict
- `PASS` (exit 0) → deliver `safe_text` verbatim (it carries the disclaimer).
- `WARN` (exit 1) → deliver `safe_text` (AI-Inferred markers + disclaimer) with a gap note naming the flagged values.
- `BLOCK` (exit 3) → **do not deliver.** Take `regeneration_instruction` and feed it to Skill-7 as the `user_revision_request` for the next synthesis; increment the retry counter (max 2). Re-run Step 1 on the regenerated text. If BLOCK again after retries are exhausted, re-run with `--force-warn` (exit 1) and deliver the marked text with a gap note that retries were exhausted.
- exit 2 → re-run with `--data` first and the message double-quoted (or via stdin).
- exit 4 (fallback) → deliver `safe_text` (text unmodified + disclaimer) with a gap note that the gate could not run.
Done when: the final text is delivered — always — with the disclaimer present exactly once, and no BLOCK was ever delivered.

### Step 3: Validate the input before generating (`--mode input`)
When Skill-7 is about to generate from fill-in cards, run the input gate first:

    python scripts/hallucination-gate.py --mode input --data "<the filled card values>"

(or `--data-file <path>` / `--text <cards>` — the cards themselves are the text under test). The input gate checks for `[AI Placeholder]` markers (not real user values) and fabrication-phrase patterns inside the cards — authority citations, research claims, projections, stat phrasing (plain numbers are user values by definition in card data).
- `PASS` → generate normally.
- `WARN` → proceed, but ask the user to confirm the flagged items (placeholders must be replaced with real values).
- `BLOCK` → do NOT generate; return the `regeneration_instruction` (it tells the user which claims need real values).

### Step 4: Final delivery wrap
On the user-accepted final text, re-run `--mode gate` once more so the delivered text carries the disclaimer and any last-moment marker sweep (idempotent — no double disclaimer). This is the Stage 5 compliance wrap; it is no longer the first line of defense.

### Step 5: Log the outcome
Leave one trace line per invocation: call point (input/gate/delivery), verdict, flagged counts, retry number (if any). No user data is stored beyond the existing memory files.
Done when: the trace line is written.

## The regeneration loop (BLOCK)

1. Caller (Skill-7 or the agent body) receives `BLOCK` + `regeneration_instruction`.
2. Skill-7 synthesizes again with the instruction as the `user_revision_request`.
3. Re-run the gate on the new text.
4. BLOCK again → one more retry (2 total attempts).
5. Still BLOCK → re-run with `--force-warn`, deliver the marked text with a gap note. Never deliver a BLOCK.

## Examples

### Example 1: Invented values block generation (signature case)
User left the Evidence card blank; the draft says "market growth of 15% next year" plus "a 30% reduction and 5000 new clients".
Actions:
1. `python scripts/hallucination-gate.py --mode gate --data "Conclusion: market growth is promising; Tactics: launch in Q1" --text We project market growth of 15% next year, a 30% reduction, and 5000 new clients, which the CFO will review.`
2. Verdict: `BLOCK`, `regex_flagged_values: ["15%", "30%", "5000"]`, `regeneration_instruction` populated (exit 3).
3. Feed the instruction to Skill-7; regenerate; re-run the gate.
Result: the fabricated figures never reach the user — generation retried until clean or until the 2-retry cap forces a marked WARN delivery.

### Example 2: User-provided values pass through
User's Value card contained "15% market growth" and "since 2023".
Actions: `python scripts/hallucination-gate.py --mode gate --data "Value: 15% market growth since 2023" --text We project 15% market growth since 2023, which the CFO will review.`
Result: `PASS` (exit 0) — values the user typed are never flagged, even when the model reuses them in the polished text.

### Example 3: Fabricated citation caught by the heuristic layer
Draft says "According to Harvard Business Review, employee engagement improves retention."
Actions: `python scripts/hallucination-gate.py --mode gate --data "Feeling: impressed; Fact: turned the meeting around" --text ...`
Result: `WARN`, `heuristic_flagged_claims: ["According to Harvard Business Review"]` — non-numeric fabrications are caught without an LM call.

### Example 4: Placeholder cards caught before generation
Filled cards contain `Risk: [AI Placeholder]`.
Actions: `python scripts/hallucination-gate.py --mode input --data "Risk: [AI Placeholder]; Interest: 10% raise"`
Result: `WARN` with `placeholder_flagged: ["[AI Placeholder]"]` — the agent asks the user for the real Risk value before generating.

### Example 5: Fail-soft on a broken run
The `--data-file` path is missing.
Actions: run the gate; verdict `fallback`/exit 4 → `safe_text` = text unmodified + disclaimer, gap note about the failed run.
Result: the draft still delivers, with the disclaimer — but a BLOCK would never have been delivered as a WARN.

## Troubleshooting

### Error: exit 2 "unrecognized arguments"
Cause: `--data` was passed AFTER `--text`, so the text consumed it (REMAINDER).
Solution: always pass `--data` / `--data-file` BEFORE `--text`; or re-run with the text piped via stdin.

### Error: message with apostrophes or `$` behaves oddly
Cause: the shell parses the unquoted text. Apostrophes break the command (shell parse error); `$` gets expanded **silently** — e.g. `$50,000` becomes `0,000`, and the script then returns a verdict on corrupted input (usually still fail-safe — the corrupted value gets flagged — but wrong). There is no error signal for the `$` case.
Solution: re-run with the message double-quoted (escape any `$` inside), or pipe it via stdin — never pass an unquoted message containing apostrophes or `$`.

### Error: non-ASCII characters look wrong in the output (e.g. a mangled €)
Cause: some shells (Git Bash/MSYS on Windows) convert argv to the ANSI codepage, corrupting non-ASCII before the script sees it.
Solution: pipe the text via stdin and pass the filled values via `--data-file` (UTF-8) — both channels are encoding-clean.

### Error: too many markers (e.g. every year gets flagged)
Cause: the draft contains dates/years the user never typed — by design those count as invented (safe direction: better to ask verification than to ship an unverified figure).
Solution: tune `CANDIDATE_RE` in `scripts/hallucination-gate.py` (e.g. drop the year alternative) and re-run the TC corpus; or ask the user for the value so it enters `--data`.

### Error: verdict feels wrong
Cause: the check is string-level, not semantic — it cannot know whether a fabricated company name or claim is real (out of scope, PRD negative scope 6).
Solution: report the limitation — non-numeric inventions that pass the heuristic layer stay with the agent's human self-check; `--mode full` emits `semantic_candidates` for an optional LM deep-check that the agent runs itself.

## Fallback
If Python is unavailable: deliver the final text with the mandatory disclaimer appended manually and a gap note — never fail the delivery (fail-soft). The invention gate is the only thing that may be lost; the disclaimer is never optional.

## Customization points

- **Patterns** — `CANDIDATE_RE` (numeric) and `HEURISTIC_RE` (citations, research claims, attributions, quotes, stat phrasing) in `scripts/hallucination-gate.py` are the invention corpus; add or remove alternatives per deployment and re-run the TC corpus.
- **Thresholds** — `BLOCK_THRESHOLD` (default 3 flags → BLOCK) and `MAX_RETRIES` (default 2) in `scripts/hallucination-gate.py`; keep `MAX_RETRIES` in sync with the agent bodies' retry caps.
- **Marker text** — `MARKER` — keep it aligned with the project's placeholder convention (`[AI Inferred: Please verify]` is baked into all 8 agent bodies).
- **Disclaimer** — `DISCLAIMER` — the Master Spec fixes this string; change it only together with the agents' delivery contract.
- **`--data` assembly** — each agent builds it from its own filled cards; the field layout is irrelevant (only the values matter). `--data-file` reads any saved cards file.
- **Legacy script** — `scripts/hallucination-detect.py` (v1 fail-soft labeler) remains for backward compatibility; its output now carries the same `verdict` field. New work should call `hallucination-gate.py`.
- **Agent delivery step** — the accept step now runs the gate for the final delivery wrap and delivers `safe_text`; the old "append the disclaimer manually" instruction was removed with the v2 upgrade.
