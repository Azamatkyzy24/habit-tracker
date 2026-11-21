# Task 2 — Agent instructions

**Files:** [`AGENTS.md`](../AGENTS.md) (root) and [`CLAUDE.md`](../CLAUDE.md), which imports it with `@AGENTS.md`.

## What AGENTS.md covers

| Required item | Section in AGENTS.md |
|---|---|
| Purpose | 1. Purpose |
| Architecture | 2. Architecture (module map + where code belongs) |
| Setup | 3. Setup |
| Safe commands | 4. Safe commands (each one was run and works — see below) |
| Coding conventions | 5. Coding conventions |
| Test expectations | 6. Test expectations |
| Forbidden actions: secrets, deployments, destructive commands, unreviewed dependency changes | 7. Forbidden actions (items 1–4, plus scope, evidence files and disabling tests) |
| Permissions and review gates (used in Task 6) | 8. Permissions and review gates |

AGENTS.md also corrects the README's broken commands (W1, W2 from Task 1), so an agent
following it uses `python -m pytest` instead of `pytest`.

## Safe commands checked

Every command in AGENTS.md section 4 was run on the baseline code and works (exit code 0):
`python -m pytest -v` (6 passed), `ruff check --isolated .`, `mypy habit_tracker`,
`python -m compileall -q habit_tracker`, `python -m habit_tracker.cli --help`.
Output: [`evidence/task1_baseline.txt`](evidence/task1_baseline.txt).

## Disclosure: how the instructions reached the AI tool

The AI assistant used for this assignment is **Claude (Opus 5.5) in the claude.ai chat app**,
not Claude Code. The chat app does **not** load `AGENTS.md` or `CLAUDE.md` from a repository
automatically. Claude wrote this AGENTS.md in the same conversation, so its rules were part of
the conversation context from then on. For the later tasks I explicitly told the assistant to
follow AGENTS.md (especially sections 6–8).

`CLAUDE.md` is there for agents that load it automatically (Claude Code reads `CLAUDE.md`
and supports `@file` imports). This was not tested with Claude Code — no Claude Code session
was used.
