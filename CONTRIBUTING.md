# Contributing to WiseTalk

WiseTalk is Apache-2.0 and built to be extended in three directions: **new communication
models** (the curriculum), **new skills** (the capability layer), and **new demo scenarios**
(the evidence). All three are additive and none of them require touching application code.

## Setup

```
git clone https://github.com/ay4322-a11y/WiseTalk_GOAI.git && cd WiseTalk_GOAI
python demo.py                      # should end "as declared" on all 5 scenarios
python -m unittest discover tests   # 29 tests
```

*Windows note:* the deepest path in the tree is 107 characters
(`agents/*/claude-code/.claude/skills/hallucination-check/scripts/…`). Cloning into an
already-deep directory can exceed the 260-character `MAX_PATH` limit; clone somewhere
shallow, or enable long paths with `git config --global core.longpaths true`.

Python 3.9+ is the only requirement. **There is nothing to install** — this repo is
standard library only, and a pull request that adds a third-party dependency to the
executable layer will be asked to justify it against that property.

## Before you open a PR

All four must pass locally. CI runs the same four on Python 3.9 and 3.12.

```
python -m unittest discover tests    # tests green
python skills-library/sync.py --verify   # no skill drift
python demo.py                       # exits 0 — no scenario deviated
python tools/metrics.py              # metrics still compute
```

## Adding a communication model (the curriculum)

This is the main extension point, and it is the reason an instructor can add a framework
without an engineer. **Zero code files change.**

1. Add a section to [`reference/wisetalk-model-catalog.md`](reference/wisetalk-model-catalog.md)
   following the existing shape: structure, when to use it, common mistakes, best reference,
   **fill-in field table**, generation prompt, critique dimensions, use cases.
2. Add a row to
   [`agents/wisetalk-router-agent/claude-code/config/agent-routing-map.md`](agents/wisetalk-router-agent/claude-code/config/agent-routing-map.md).
3. Generate an agent package from [`templates/`](templates/) — intake form → spec →
   `claude-code/` workspace.
4. Add keyword signals for the new use cases to `ROUTING_KEYWORDS` in `demo.py` so the demo
   router can reach them. (The Claude Code router needs no change — it reads the map.)
5. Add a scenario under `demo/scenarios/` exercising it.

The catalog table is parsed at runtime, so the model's cards appear in `demo.py` and in the
browser demo's fill-in UI immediately. `tests/test_skills.py::CatalogAndRouting` will fail
if the catalog and the routing map disagree.

## Adding or changing a skill

Read [`docs/skill-contract.md`](docs/skill-contract.md) first — it specifies the frontmatter,
the JSON-line-plus-exit-code contract, and the fail-closed / fail-soft rule.

**Edit the library, never an agent copy.** `skills-library/` is canonical; agent copies are
generated. An edit to a copy is erased by the next sync and is a silent behavioural fork
until then.

```
# edit skills-library/<name>/...
python skills-library/sync.py --skill <name>
python skills-library/sync.py --verify
```

Tests must assert **both** the exit code and the JSON verdict. Agents branch on both, so
covering only one leaves the other unprotected.

## Adding a demo scenario

Scenarios are the project's evidence, not its illustrations. Each one declares what it
expects, and `demo.py` exits non-zero if reality disagrees.

```json
{
  "id": "06-your-scenario",
  "title": "One line a reviewer can read",
  "user_message": "what the user types",
  "cards": { "Field": "value" },
  "recorded_draft": "the generated text",
  "recorded_regenerations": ["the clean rewrite, if the first draft is meant to BLOCK"],
  "expect": { "stage0": "SAFE", "routed_agent": "Agent 6 (RIDE)", "final_verdict": "PASS" }
}
```

An `expect` block is mandatory — a scenario that declares nothing proves nothing, and
`tests/test_skills.py::DemoScenarios` enforces it.

## Two standards this project holds

**No unverifiable claims.** Every number in the README, `METRICS.md` and `RUN_EVIDENCE.md`
is produced by a command a reader can run. If you add a claim, add the command that
produces it. Scores that no run produced get removed, not carried forward — that has
already happened once here, and the audit note is left in place in the affected files.

**The gates stay deterministic.** Anything that decides whether text reaches a user is a
script with an exit code, not a prompt. A security control phrased as an instruction is a
suggestion, and this project does not ship suggestions as controls.

## Reporting security issues

The injection filter's wordlist (`skills-library/injection-filter/scripts/sensitive-words.txt`)
and the gate's patterns are open. If you find a bypass, open an issue with the exact input —
a reproducible bypass is a welcome contribution, and adding it to
`demo/corpus/injection-attacks.txt` alongside the fix is the expected shape of the PR.

Equally useful: a **false positive**. An ordinary workplace sentence that the filter blocks
is a bug of the same severity, and belongs in `demo/corpus/benign-workplace.txt`.

## License

By contributing you agree your contributions are licensed under [Apache-2.0](LICENSE).
