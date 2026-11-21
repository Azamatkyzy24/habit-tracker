# Task 1 — Baseline and context

**Reviewed version:** tag `baseline` (commit `b2aa99e`, tree `d9e2ed5a`)
**Full command output:** [`evidence/task1_baseline.txt`](evidence/task1_baseline.txt)

## 1. Repository map

| Area | Location | Notes |
|---|---|---|
| Entry point | `habit_tracker/cli.py` → `main()` | Run as `python -m habit_tracker.cli <command>`. Commands: `add`, `done`, `report`, `export`, `reset`. There is **no** `main.py`. |
| Domain model | `habit_tracker/models.py` | `Habit` dataclass: `name`, `created` (ISO date), `checkins` (list of ISO dates). |
| Business logic | `habit_tracker/tracker.py` | `add_habit`, `check_in`, `current_streak`, `weekly_completion`. Pure functions, `today` can be injected for tests. |
| Export | `habit_tracker/exporter.py` | `export(habits, fmt)` with `if/elif` for `json` / `csv` / `text`. |
| Storage | `habit_tracker/storage.py` | JSON file at `data/habits.json` (git-ignored). `load_habits`, `save_habits`, `reset` (deletes the file). |
| Tests | `tests/test_tracker.py` | 6 pytest tests: tracker logic, JSON export, save/load. |
| Dependencies | `requirements.txt` | One line: `pytest` (no version). Runtime uses only the Python standard library. |
| Build / CI | — | None: no `pyproject.toml`, no CI workflow, no lint or type-check config. |

Size: 289 lines in 10 tracked files.

## 2. Checks run on the baseline

Environment: Python 3.13.18, fresh virtual environment, Linux.

| Check | Command | Result |
|---|---|---|
| Install | `pip install -r requirements.txt` | OK — installed **pytest 9.2.0** |
| Tests (works) | `python -m pytest -v` | **6 passed**, 0 failed (exit 0) |
| Tests (as in README) | `pytest -q` | **ERROR** — `ModuleNotFoundError: No module named 'habit_tracker'` (exit 2) |
| Lint | `ruff check --isolated .` (ruff defaults; not configured in repo) | All checks passed (exit 0) |
| Type check | `mypy habit_tracker` and `mypy --check-untyped-defs habit_tracker` | Success, no issues (exit 0) |
| Build | `python -m compileall -q habit_tracker` (no real build exists) | OK (exit 0) |
| Run (as in README) | `python main.py report` | **ERROR** — `can't open file ... main.py` (exit 2) |
| Run (actual) | `python -m habit_tracker.cli add/done/report/export` | Works (exit 0) |
| Coverage | `python -m coverage run --source=habit_tracker -m pytest` | **49%** total; `cli.py` **0%**, `exporter.py` 43%, `storage.py` 82%, `tracker.py` 97% |

## 3. Weaknesses and missing checks

| # | Weakness | Evidence |
|---|---|---|
| W1 | README run instructions are wrong. | `README.md` says `python main.py add ...`; `main.py` does not exist → exit 2. |
| W2 | The documented test command fails. | `pytest -q` → `ModuleNotFoundError` (no `pyproject.toml`/`conftest.py` puts the package on the path). Only `python -m pytest` works. |
| W3 | Dependencies are not pinned. | `requirements.txt` = `pytest`. Same file gave pytest **9.1.1** in the global Python and **9.2.0** in a fresh venv on the same day. |
| W4 | Large untested areas. | Coverage 49%. `cli.py` 0% (lines 1–78), `exporter.py` CSV/text branches (lines 19–32), `storage.reset` (lines 24–25) and the "file missing" branch (line 11) never run. |
| W5 | Lint and type checks exist only by accident. | No lint/type config in the repo. mypy reports "success", but the functions have **no type hints**, so it checks almost nothing. |
| W6 | No build/packaging or CI. | No `pyproject.toml`, so the `habits` program name in `cli.py` is never installed as a command. No `.github/workflows/`. |

## 4. Facts vs assumptions vs unverified suggestions

**Observed facts** (from commands above): W1–W6; 6/6 tests pass with `python -m pytest`; CLI works via `python -m habit_tracker.cli`.

**Assumptions** (not yet checked):
- The app is single-user and local only; nobody else writes to `data/habits.json`.
- Behaviour on Windows is the same as on Linux.
- Python 3.10+ is needed (code style suggests it; no minimum version is declared).

**Unverified AI suggestions** (to investigate in Task 4, not counted as findings yet):
- Behaviour with bad input (duplicate check-ins, future dates, empty names, broken JSON file) has not been tested.
- The `reset` command deletes data with no confirmation — risky for humans and agents.

## 5. Acceptance criteria (must stay true after every change)

| ID | Criterion | How to verify |
|---|---|---|
| AC1 | `add`, `done`, `report` and `export` work end-to-end for valid input and keep their current output format. | Smoke run in `evidence/` + CLI tests (to be added). |
| AC2 | Streak and weekly % are calculated the same way for valid data. | `test_streak_three_days`, `test_weekly_completion` pass. |
| AC3 | A `data/habits.json` written by the baseline version still loads in the final version (no data format break). | Save/load test with a baseline-format file. |
| AC4 | JSON and CSV exports keep the columns `name, created, streak, weekly_percent`. | `test_export_json` + CSV test (to be added). |
| AC5 | All existing tests still pass and none are deleted or weakened. | `python -m pytest -v` shows ≥ 6 passed, 0 failed. |
