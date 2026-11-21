# AGENTS.md — instructions for AI coding agents

Read this file before changing anything in this repository. If something here
conflicts with `README.md`, **this file wins**.

## 1. Purpose

Habit Tracker is a small, single-user command-line app. Users add habits, check in
each day, and see their current streak and weekly completion %, or export the data
to JSON / CSV / text. Data is stored locally in `data/habits.json`.
It is a university project (Software Engineering, Assignment #05) — no production
deployment, no server, no real user data.

## 2. Architecture

```
habit_tracker/
  cli.py       entry point: argparse commands add / done / report / export / reset
  tracker.py   business logic (pure functions): add_habit, check_in,
               current_streak, weekly_completion
  exporter.py  export(habits, fmt) -> str   (json / csv / text)
  storage.py   load_habits / save_habits / reset  (JSON file, data/habits.json)
  models.py    Habit dataclass: name, created (ISO date), checkins (list of ISO dates)
tests/
  test_tracker.py   business logic, JSON export, save/load
  test_cli.py       CLI end-to-end and export formats (redirects load/save)
  test_safety.py    damaged data file, atomic save, export --out safety
                    (redirects storage.DATA_FILE to a temp folder - copy this fixture)
docs/               assignment write-ups and evidence (not code)
```

Rules for where code goes:
- Calculations and rules → `tracker.py`. Keep them pure (no printing, no file access).
- Output formatting → `exporter.py`. File access → `storage.py`.
- `cli.py` only parses arguments, calls the other modules and prints.
- Functions that use "today" take an optional `today` / `day` argument so tests can pass a fixed date.

## 3. Setup

Requires Python 3.10+ (tested with 3.13). Only standard library at runtime; pytest for tests.

```
python -m venv .venv
.venv\Scripts\activate        # Windows   (Linux/macOS: source .venv/bin/activate)
python -m pip install -r requirements.txt
```

## 4. Safe commands (allowed without asking)

| Purpose | Command |
|---|---|
| Run tests | `python -m pytest -v` |
| Lint (if installed) | `ruff check --isolated .` |
| Type check (if installed) | `mypy habit_tracker` |
| Syntax/build check | `python -m compileall -q habit_tracker` |
| Show CLI help | `python -m habit_tracker.cli --help` |
| Read-only git | `git status`, `git diff`, `git log` |

Do **not** use plain `pytest` (fails: `ModuleNotFoundError`) or `python main.py`
(file does not exist) — older versions of the README showed these.

Trying the CLI by hand writes to the real `data/habits.json`. Only do it if the user
asks, and never run `reset` (see section 7).

## 5. Coding conventions

- Plain, simple Python in the existing style: small functions, `snake_case`, f-strings,
  short docstrings for non-obvious logic. No new frameworks or classes unless needed.
- Dates are stored as ISO strings (`YYYY-MM-DD`). Do not change the JSON format of
  `data/habits.json` — old files must still load (acceptance criterion AC3).
- Keep JSON/CSV export columns: `name, created, streak, weekly_percent` (AC4).
- Errors in logic raise `ValueError` with a clear message.
- Keep changes small and focused: one problem per commit, clear commit message.

## 6. Test expectations

- Before and after every change run `python -m pytest -v` and report the **real**
  pass/fail totals. Never claim a test passed without running it, and never
  invent output.
- All existing tests must keep passing. Do not delete, skip or weaken a test to make
  a change pass (AC5).
- Every bug fix comes with a test that fails before the fix and passes after it.
- Tests must not touch the real `data/habits.json`: use pytest's `tmp_path` and pass
  the path to `storage` functions. Use fixed dates, not `date.today()`.
- Acceptance criteria AC1–AC5 are in `docs/01-baseline.md` and must stay true.

## 7. Forbidden actions

An agent must **never**:
1. Read, create, print or commit secrets: passwords, API keys, tokens, `.env` files,
   or real personal data. Test data must be made up.
2. Deploy, publish or release anything (no PyPI upload, no `git push` to any remote,
   no GitHub releases).
3. Run destructive commands: `python -m habit_tracker.cli reset`, deleting
   `data/` or other files outside the task, `git reset --hard`, `git push --force`,
   `git clean`, rewriting history, or deleting branches/tags (especially the `baseline` tag).
4. Add, remove or upgrade dependencies (`requirements.txt`, `pip install <new package>`)
   without the human's explicit approval of the exact change.
5. Change files outside the task's scope, or edit `docs/evidence/` (those are recorded results).
6. Disable, skip or delete tests or checks.

If a task seems to require any of these, **stop and ask** the human.

## 8. Permissions and review gates

| Action | Permission |
|---|---|
| Read any file, run section 4 commands | Allowed |
| Edit code and tests inside the task scope | Allowed, on a branch — not on `main` |
| Commit | Allowed on the task branch, small commits |
| Merge to `main`, push, change dependencies | **Human only**, after review |

Before a change can be merged, the human reviewer checks:
1. The diff — every changed line is understood and needed.
2. Test output — `python -m pytest -v` was run, all pass, totals reported honestly.
3. New/updated tests exist for the change.
4. Acceptance criteria AC1–AC5 still hold.
5. No forbidden action from section 7 happened.

## 9. What the agent must report after a task

A short summary of what changed and why, the diff, the exact commands run with their
real output (pass/fail totals), anything not tested, and remaining risks.
