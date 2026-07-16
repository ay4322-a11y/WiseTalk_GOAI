# Trigger setup — competitor-intel-agent

> Generated from the trigger-setup skeleton in [templates/03-claude-code-mapping.md](../../../../templates/03-claude-code-mapping.md). These are **instructions** — arming the trigger is your consent decision; no agent arms it for you.

- **Trigger:** scheduled(Mon 09:00) — from Intake C
- **Dedup rule:** fires mid-run: **skip** — the running instance finishes; the skipped fire is noted in `memory/state.md` (Element 1)

## Arm it (run yourself)

Scheduled weekly run via the `/schedule` skill:

```
/schedule weekly Mon 09:00 — "Run the weekly competitor-intel digest: invoke the
competitor-intel-agent sub-agent. It reads config/competitors.md, resumes from
memory/state.md if the last run is incomplete, and delivers reports/digest-<date>.md."
```

No hooks or `/loop` needed — this agent has a single scheduled trigger and an on-demand path that needs no arming.

## Verify once armed (scores checklist Element 1)

- [ ] Trigger fired and started a run (see `scratch/<week>/run-log.md` / `memory/state.md` last-run line)
- [ ] A mid-run fire followed the dedup rule (skipped, noted in `state.md`) — eval case 5
- [ ] The run ended via checker PASS or a stop condition — not by hanging

After the first observed Monday fire: upgrade Element 1 to score 2 in [../validation-checklist.md](../../validation-checklist.md) and score eval case 5.
