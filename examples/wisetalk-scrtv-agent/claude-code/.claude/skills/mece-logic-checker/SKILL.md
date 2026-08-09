---
name: mece-logic-checker
description: Run a MECE check on a list of argument points — detect keyword overlap between points and missing 4M1E dimensions (Human, Machine, Material, Method, Environment). Use when the user lists 3 or more argument points and asks to verify they are mutually exclusive and collectively exhaustive, or when a MECE/SCRTV expert receives multiple arguments to structure. Do NOT use for a single argument, for generating or rewriting arguments, or for critiquing finished prose.
license: MIT
compatibility: Python 3 (stdlib only)
allowed-tools: "Bash(python:*)"
metadata:
  author: WiseTalk (via skill-generator)
  version: 1.0.0
---

# MECE Logic Checker (WiseTalk Skill-4)

## Important
- The verdict comes **only** from `scripts/mece-check.py`'s deterministic output. Never invent an overlap reason or a missing dimension — if the script fails, report the failure instead.
- Never claim a list is MECE (`is_valid: true`) without having run the script this run.
- The fixed dimension library is the 4M1E set: **Human, Machine, Material, Method, Environment** — it is the only omission standard (D-003).

## Instructions

### Step 1: Extract the argument points
Identify each distinct argument point in the user's message. If the user pasted prose, split it into one point per argument. Drop empty entries.
Done when every point is a single clean string and the list has no empties.
If fewer than 2 non-empty points remain, stop and report `{"message": "Cannot perform MECE analysis"}` — the script will also enforce this.

### Step 2: Run the checker
Pass the points as a JSON array:

    python scripts/mece-check.py --points '["Point A", "Point B", "Point C"]'

Expected output: a single JSON line — `{"is_valid": bool, "overlap_reason": str|null, "missing_dimension": str|null}`, or `{"message": "Cannot perform MECE analysis"}` for fewer than 2 points.
If it fails: script not found → check the path `scripts/mece-check.py` relative to this skill folder; JSON quoting error (exit 2) → pass the array as valid JSON with single-quoted wrapping and double-quoted strings; Python unavailable → go to Fallback.

### Step 3: Interpret the verdict
- `overlap_reason` non-null → name the overlapping pair and its reason, then ask the user to merge or split the points.
- `missing_dimension` non-null → list the uncovered 4M1E dimensions and ask the user whether each should be represented.
- `is_valid: true` → confirm the list is mutually exclusive and collectively exhaustive.
Done when the user has been told exactly what the verdict says and given the next action (fix points or proceed).

### Step 4: Return the structured result
Return the verdict JSON to the caller verbatim (the agent's pipeline consumes it), plus one sentence of coaching per Step 3.
Done when the returned object is the script's output — never a paraphrased verdict.

## Examples

### Example 1: Overlapping points (signature case)
User says: "Check these are MECE: reduce labor cost, cut overtime pay, improve efficiency"
Actions:
1. Points: `["Reduce labor cost", "Cut overtime pay", "Improve efficiency"]`
2. Run `python scripts/mece-check.py --points '["Reduce labor cost", "Cut overtime pay", "Improve efficiency"]'`
Result: `{"is_valid": false, "overlap_reason": "Point 1 'reduce labor cost' overlaps Point 2 'cut overtime pay': its content is contained in the other point.", "missing_dimension": "Machine, Material, Method, Environment dimension(s) missing."}` — coach the user to merge point 1 and 2 and consider the uncovered dimensions.

### Example 2: Clean list
User says: "Verify: hire two analysts, buy the new server, adopt a testing workflow"
Actions: run the script with the 3 points.
Result: `{"is_valid": false, "missing_dimension": "Material, Environment dimension(s) missing."}` — report the gaps; the analyst/server/workflow points cover Human, Machine, Method.

### Example 3: Too few points
User says: "Is this one argument OK?" (single point)
Actions: report `{"message": "Cannot perform MECE analysis"}` without running the script.

## Troubleshooting

### Error: exit 2 "Cannot parse input as JSON"
Cause: the array was wrapped in double quotes or had unescaped quotes.
Solution: wrap the whole array in single quotes and use double quotes inside — `--points '["A", "B", "C"]'`.

### Error: verdict feels wrong for non-English points
Cause: the keyword library is English-only (D-007); non-English points still get verbatim-substring overlap detection, but not synonym expansion or dimension coverage.
Solution: report the limitation to the user; the verdict is still the deterministic output.

## Fallback
If Python is unavailable or the script errors: say so explicitly, show the raw points to the user, and hand the MECE judgement back to the human — do NOT substitute an eyeballed verdict, and do NOT report `is_valid` without a script run.
