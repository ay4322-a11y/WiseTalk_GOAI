# System metrics

Every figure below is computed from this repository by `python tools/metrics.py`.
Nothing is estimated, and nothing is typed in by hand — re-run the command and you get
these numbers back.

**Captured 2026-08-11.**

> **What these are.** System measurements: what WiseTalk provably does. They are **not**
> user outcomes. No number here claims a learner communicated better — that requires a
> study this project has not run, and inventing one would be exactly the failure mode the
> hallucination gate exists to prevent.

---

## Coverage

| Measure | Value |
|---|---:|
| Communication models | 8 |
| Routable use cases | 32 |
| Agent packages (1 router + 8 experts) | 9 |
| Mandatory fill-in cards across all models | 28 |
| Reusable library skills | 9 |
| Agent skill copies (38 library-synced, drift-gated) | 55 |
| Executable files | 9 |
| **Third-party runtime dependencies** | **0** |

## Security — Skill-11 injection filter

Measured by running the real filter over two corpora in `demo/corpus/`.

| Measure | Value |
|---|---:|
| Attack corpus | 28 messages |
| Blocked | **28 / 28 (100%)** |
| Benign workplace corpus | 24 messages |
| False positives | **0 (0%)** |

The benign corpus matters as much as the attack corpus. A filter that blocks
*"Please ignore my previous email"* or *"we need to bypass the staging queue"* has broken
the product to look safe. Both are in the corpus; both pass.

## Security — Skill-12 hallucination gate

Measured over six labelled fixtures spanning the full verdict range.

| Measure | Value |
|---|---:|
| Labelled fixtures | 6 |
| Verdict matches label | **6 / 6 (100%)** |
| Drafts blocked before delivery | 2 |
| Median gate latency | ~300 ms |

Latency is dominated by Python interpreter startup — the gate itself is a regex pass over
the draft, and it runs with **no model call**, so the security layer costs nothing per token
and cannot be talked out of its verdict.

## Loop and pipeline behaviour

From the shipped scenarios (`demo/scenarios/`, verified on every CI run):

| Measure | Value |
|---|---:|
| Scenarios behaving exactly as declared | **5 / 5** |
| Fabrications caught in the BLOCK scenario | 4 (1 currency, 1 authority citation, 2 statistics) |
| Regenerations needed to reach a clean draft | 1 (cap is 2) |
| Critique iterations before force-exit | 3 (hard cap) |
| Automated tests | **28, all passing** |

## Eval status — stated honestly

| Agent | Cases specified | Cases scored |
|---|---:|---:|
| wisetalk-router-agent | 10 | 10 |
| wisetalk-star-agent | 13 | 13 |
| wisetalk-scrtv-agent | 13 | 13 |
| wisetalk-mece-agent | 13 | 13 |
| wisetalk-ride-agent | 13 | 13 |
| wisetalk-prep-agent | 13 | 0 |
| wisetalk-scqa-agent | 14 | 0 |
| wisetalk-ffc-agent | 13 | 0 |
| wisetalk-funnel-agent | 13 | 0 |
| **Total** | **115** | **62 (54%)** |

Five agents are fully scored. Four are specified but unscored — their eval files
previously carried a `26/26` baseline header that no run produced and that did not match
their own case counts; it was removed on 2026-08-11 rather than carried into a submission.
See the audit note at the top of each of those files.

Separately, the deterministic script behaviour those cases reference — Skill-11 and
Skill-12 verdicts and exit codes — **is** covered by the 28 automated tests, which run on
every commit. The 53 unscored cases are agent-behaviour cases that require a Claude Code
session to score.

## Extensibility

Adding a 9th communication model touches **0 code files**:

1. One section in `reference/wisetalk-model-catalog.md` — structure, cards, generation prompt, critique dimensions.
2. One row in `agents/wisetalk-router-agent/claude-code/config/agent-routing-map.md`.
3. One agent package generated from `templates/`.

`demo.py` and `demo_server.py` parse the catalog and routing map at runtime, so the new
model appears in the CLI, in the browser fill-in cards, and in the router with no code
change. This is the property that makes the system a **curriculum an instructor can
extend**, rather than a fixed feature set.

## Reproduce

```
python tools/metrics.py          # this report
python tools/metrics.py --json   # machine-readable
python demo.py                   # the five scenarios
python -m unittest discover tests
python skills-library/sync.py --verify
```
