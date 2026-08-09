---
name: growth-trends
description: Aggregate battle-score history into weekly or monthly growth trends and name the weakest dimension (WiseTalk Skill-10; user-invoked — type `growth-trends`).
disable-model-invocation: true
license: MIT
compatibility: code-first (deterministic script, no LLM)
metadata:
  author: WiseTalk (via skill-generator)
  version: 1.0.1
---

# Long-Term Trend Analysis & Visualization (WiseTalk Skill-10)

## Important
- **The script is the source of truth**: deliver its JSON output verbatim — never re-interpret, re-average, or paraphrase the numbers. This skill is "Pure Code, no LLM" (PDF): the weak point and every average are computed, never imagined.
- **Empty history is a valid deliverable, not an error**: a missing, empty, or all-malformed records file returns `{"message": "No history available yet"}` with exit code 0 — that is the dashboard's empty state, not a failure.
- **Never invent records**: if the records file does not exist, say so in the empty-history response. This skill aggregates only what Skill-9 `battle-scoring` actually persisted; it never creates, edits, or guesses scores.
- **Verbatim JSON contract**: one single-line JSON on stdout. Any other output (usage errors, tracebacks) means the run failed — report it, do not deliver partial data.

## Instructions

### Step 1: Locate the score records file
The router's `memory/battle-scores.jsonl` (the Skill-9 persistence contract: one record per line, `{"date": "YYYY-MM-DD", "logic": 0-100, "eq": 0-100, "response_speed": 0-100, "persuasion": 0-100}`).
If the file does not exist, do not create it — go to Step 3 (empty history).
Done when: you know the file's absolute path, or you have confirmed it is absent.

### Step 2: Run the aggregator
```
python scripts/aggregate-scores.py --scores "<records file path>" --range weekly
```
- `--range weekly` (default) → ISO-week buckets labeled by Monday (`YYYY-MM-DD`); `--range monthly` → calendar-month buckets labeled `YYYY-MM-01`.
- Records are bucketed by date, oldest first; each dimension is averaged per bucket (integer mean, round half up); malformed records are skipped, never fatal.
- Expected output — success:
```json
{"trend_data": {"dates": ["2026-05-11", "..."], "logic": [82, "..."], "eq": [55, "..."], "response_speed": [76, "..."], "persuasion": [71, "..."]}, "weak_point": "Emotional Empathy declining"}
```
- Expected output — no usable history (missing/empty/all-malformed file): `{"message": "No history available yet"}`
- Exit codes: `0` = ok (including empty history); `2` = usage error (bad args) — report the usage message and re-run with correct arguments.
Done when: you have the script's exit code and JSON, delivered exactly as printed.

### Step 3: Deliver the result
Present the script's JSON verbatim, plus one plain-language line naming the weak point (e.g. "Your weakest dimension across this range is Emotional Empathy — and it is declining from bucket to bucket.") and, when it is declining, point the user at Skill-8/9 practice on that dimension. If the response was the empty-history message, tell the user that trends appear once battle sessions have been scored (Skill-9) and saved.
Done when: the verbatim JSON plus the one-line reading is delivered, and the run is logged (file path, range, weak point or "no history").

## Examples

### Example 1 — Signature case: 12 sessions over ~90 days, weekly
`--scores memory/battle-scores.jsonl --range weekly` →
```json
{"trend_data": {"dates": ["2026-05-11", "2026-05-18", "2026-05-25", "2026-06-01", "2026-06-08", "2026-06-15", "2026-06-22", "2026-06-29", "2026-07-06", "2026-07-13", "2026-07-20", "2026-07-27"], "logic": [82, 85, 80, 84, 87, 83, 86, 81, 88, 84, 82, 86], "eq": [55, 58, 60, 62, 60, 58, 55, 52, 50, 48, 45, 42], "response_speed": [76, 78, 75, 79, 80, 77, 81, 74, 82, 79, 76, 80], "persuasion": [71, 73, 70, 74, 75, 72, 76, 70, 77, 73, 71, 75]}, "weak_point": "Emotional Empathy declining"}
```
Reading: "Your weakest dimension is Emotional Empathy, and the trend is downward — its weekly average fell from 55 to 42."

### Example 2 — Monthly view
`--range monthly` on the same file →
```json
{"trend_data": {"dates": ["2026-05-01", "2026-06-01", "2026-07-01"], "logic": [82, 84, 85], "eq": [58, 57, 46], "response_speed": [76, 78, 79], "persuasion": [71, 73, 74]}, "weak_point": "Emotional Empathy declining"}
```

### Example 3 — New user, no history yet
`--scores memory/battle-scores.jsonl` (file absent) →
```json
{"message": "No history available yet"}
```
Reading: "You have no scored battle sessions yet — run the Battle Arena (Skill-8) and get scored (Skill-9) to start your trend history."

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `{"message": "No history available yet"}` | File missing, empty, or every record malformed | Correct state, not an error — deliver it. If records should exist, check the path (Skill-9 writes `memory/battle-scores.jsonl`). |
| Exit 2 with `usage:` text | Missing `--scores`, invalid `--range`, or unknown flag | Re-run with the documented arguments. |
| A malformed-looking record is silently missing from the averages | Malformed records are skipped by design (never crash, never guess) | Confirm the record is valid: parseable ISO `YYYY-MM-DD` date and integer 0–100 values for all four dimensions. |
| Averages look off by 0.5 | Integer mean rounds half up (`int(avg + 0.5)`) | Expected — this is the documented rounding, matching hand computation. |
| Weak point has no "declining" suffix | Only one bucket exists, or the last bucket is not below the first | Expected — the suffix requires ≥2 buckets with a downward trend (PDF rule). |

## Fallback
If Python is unavailable, the trend feature is unavailable: tell the user (do not estimate trends by hand — that would be fabrication), deliver the "No history available yet" message if the file exists, and log a gap note. Usage errors (exit 2) → show the usage line and ask for the correct arguments. This skill is a read-only dashboard query — the system never fails because of it; the dashboard simply shows the empty state.

## Customization points
- **Records path** — change `memory/battle-scores.jsonl` in Step 1 when the real storage layer (the Master Spec's SQLite) lands; the script itself only takes `--scores <path>`, so any JSONL file of Skill-9-shaped records works.
- **Rounding rule** — `mean_half_up` (round half up) in `scripts/aggregate-scores.py`; change to floor/nearest if the dashboard needs it (update Examples too).
- **Dimension order for ties** — `DIMENSIONS = ["logic", "eq", "response_speed", "persuasion"]`; the first dimension wins a tie for the lowest average. Reorder to change tie-break priority.
- **Labels** — `DIMENSION_LABELS` in the script; edit if the UI names differ.
- **Range choices** — add a `weekly`/`monthly`-style choice to the `--range` argument to support, e.g., quarterly bucketing.
