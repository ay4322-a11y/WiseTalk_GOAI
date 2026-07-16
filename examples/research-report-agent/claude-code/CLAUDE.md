# Research Report Project

This project produces market/industry research reports via the `research-report-agent` sub-agent (generated from `../agent-spec.md` using the [Claude Code mapping](../../../templates/03-claude-code-mapping.md)).

## Rules (spec Element 2)

- All agents follow the behavioral baseline in @docs/behavioral-guidelines.md (Think Before Coding · Simplicity First · Surgical Changes · Goal-Driven Execution + its communication style). No deviations for this project.
- Public web sources only. Never read anything in `private/` or behind a login.
- Never present an uncited quantitative claim. Conflicting figures are flagged, never averaged.
- No investment advice. No PII in any report.
- Reports are written to `reports/<topic-slug>-<date>.md`; intermediate findings to `scratch/`; long-term memory to `memory/`.
- Emailing or publishing a report always requires explicit user approval.

## Directory layout

```
docs/behavioral-guidelines.md — all-agents baseline (copied from the template pack's reference/)
reports/    — delivered reports (spec Element 15)
scratch/    — per-section findings, audit trail (Elements 6, 12)
memory/     — long-term memory, MEMORY.md index (Elements 3, 14)
evals/      — eval cases + scores per run, hill-climbing loop (Element 13)
private/    — OFF LIMITS to the agent
```

## Usage

Ask for a report: *"Research the AI Agent industry chain: market size, funding, industry chain, competitive landscape."*
The `research-report-agent` handles it end-to-end and returns the executive summary plus the report path.
