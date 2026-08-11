# The WiseTalk skill contract

Every skill in `skills-library/` follows the same contract. The contract is what makes the
library **reusable outside WiseTalk**: a skill is a self-contained unit with a declared
trigger, a declared input, a declared output, and a declared failure mode — adoptable by
any agent system that can read a markdown instruction file and run a Python script.

This document is the interface specification. Read it before adding a skill or lifting one
into another project.

---

## 1. Shape

```
skills-library/<skill-name>/
├── SKILL.md              # required — the instruction file, with YAML frontmatter
└── scripts/              # optional — deterministic logic the instruction file calls
    └── <script>.py
```

`SKILL.md` frontmatter carries exactly three keys:

```yaml
---
name: hallucination-check
description: >
  <what it does> Use when <trigger>. Do NOT use for <the nearest wrong thing>.
---
```

The `description` is load-bearing: it is how an agent decides whether to invoke the skill
at all. Write it as a routing rule — a positive trigger and an explicit boundary — not as a
summary. "Do NOT use for" lines exist to stop a skill being reached for when a sibling skill
is the right one.

## 2. Determinism boundary

Skills split into two kinds, and the split is deliberate:

| Kind | Logic lives in | Examples | Property |
|---|---|---|---|
| **Deterministic** | A Python script | `injection-filter`, `hallucination-check`, `mece-logic-checker`, `growth-trends` | Same input → same verdict, every time. No model call. Cannot be argued out of its answer. |
| **Judgment** | The instruction file | `language-polishing`, `iterative-critique`, `battle-simulator`, `battle-scoring`, `subtext-emotion` | Needs a model. The instruction file constrains the shape of the output (exactly 3 critique points, exactly 2 tips). |

**The rule: anything that gates delivery is deterministic.** A security control implemented
as a prompt is a suggestion. WiseTalk's two gates — Skill-11 at the entry and Skill-12
before output — are both scripts with exit codes, so their verdicts survive a model that
has been talked into cooperating.

## 3. Script contract

Every script in `scripts/` obeys the same four rules:

1. **Standard library only.** No third-party imports, ever. This is what makes the library
   liftable into another project with a copy, and auditable with no dependency tree.
2. **One JSON line on stdout.** The last line of stdout is the result object. Callers parse
   the last parseable line, so debug output above it is harmless.
3. **Exit code carries the verdict**, so a caller can branch without parsing:

   | Exit | Meaning |
   |---:|---|
   | 0 | clean / safe / PASS |
   | 1 | flagged / blocked-input / WARN |
   | 2 | usage error |
   | 3 | BLOCK — must not be delivered |
   | 4 | internal fallback |

4. **The failure direction is declared, and it differs by position.**
   - **Input-side skills fail closed.** `injection-filter` reports *blocked* on a crash, a
     missing wordlist, or bad arguments — an unverifiable message is treated as hostile.
   - **Output-side skills fail soft on internal errors and closed on detections.**
     `hallucination-check` degrades to WARN if the script itself breaks (the user's text is
     never lost), but a detected invention is never downgraded — a BLOCK triggers
     regeneration or, after the retry cap, a marked WARN.

   Getting this backwards is the classic failure: a filter that fails open, or a gate that
   silently drops the user's work.

## 4. Lifecycle

`skills-library/` is the **canonical source**. Each agent carries a byte-identical copy
under `agents/<agent>/claude-code/.claude/skills/<skill>/`, because a Claude Code sub-agent
loads skills from its own workspace.

```
python skills-library/sync.py --skill <name>   # propagate one skill
python skills-library/sync.py --all            # propagate every skill
python skills-library/sync.py --verify         # byte-compare, exit 1 on drift
```

`--verify` runs in CI. A drifted copy means an agent is silently running a stale skill, so
drift fails the build rather than being reconciled quietly. `sync-manifest.json` records
which agents receive which skills when the mapping is not name-for-name.

**Edit the library, never an agent copy.** An edit to a copy is erased by the next sync,
and until then it is a silent behavioural fork between agents.

## 5. Adding a skill

1. Create `skills-library/<name>/SKILL.md` with the three frontmatter keys and a
   description written as a routing rule.
2. If it gates anything, put the logic in `scripts/` as a stdlib-only script following §3.
3. Add the target agents to `sync-manifest.json` if the mapping is not name-for-name.
4. Run `python skills-library/sync.py --skill <name>`.
5. Add tests to `tests/test_skills.py` asserting **both** the exit code and the JSON
   verdict — the agents branch on both, so testing one leaves the other unprotected.
6. Run `python -m unittest discover tests` and `python skills-library/sync.py --verify`.

## 6. Reusing these skills elsewhere

The four deterministic skills carry no WiseTalk-specific state and are useful to any agent
system:

| Skill | What it gives you |
|---|---|
| `injection-filter` | Aho-Corasick DFA + regex phrase layer over an editable wordlist; fail-closed entry gate |
| `hallucination-check` | Pre-output validator comparing generated text against the user's own supplied values; PASS/WARN/BLOCK with a regeneration instruction |
| `mece-logic-checker` | Deterministic overlap/gap check on a list of argument points |
| `growth-trends` | JSONL score history → trend series + weakest dimension |

Copy the folder, keep the exit-code contract, and the skill works — no installation, no
configuration, no WiseTalk dependency. Attribution under Apache-2.0 is all that is asked.
