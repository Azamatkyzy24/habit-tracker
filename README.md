# Habit Tracker

A small command-line app for tracking daily habits: add habits, check in each day,
see your streaks and weekly progress, and export your data.

## Setup

Requires Python 3.10+ (tested with 3.13 on Windows and Linux).

```
python -m pip install -r requirements.txt
```

## Usage

```
python -m habit_tracker.cli add "Read 20 pages"
python -m habit_tracker.cli done "Read 20 pages"
python -m habit_tracker.cli done "Read 20 pages" --date 2026-11-20
python -m habit_tracker.cli report
python -m habit_tracker.cli report --format json
python -m habit_tracker.cli export --format csv --out habits.csv
```

Formats: `text`, `json`, `csv`. `export --out` will not overwrite an existing file
unless you add `--force`, and it never overwrites the habit data file.

Data is saved in `data/habits.json` (not committed to git).

## Tests

```
python -m pytest -v
```

(Plain `pytest` does not work in this project; use `python -m pytest`.)

## Known limitations

- Running `done` twice for the same day counts that day twice, so the weekly % can be wrong
  (can even go above 100%).
- `reset` deletes **all** data immediately, without asking, and cannot be undone.
- To keep a backup, copy `data/habits.json` somewhere else from time to time.
- If `data/habits.json` is damaged, commands stop with an error message. Fix the file by hand
  or restore your backup; `reset` also works but deletes everything.
- Do not run two commands at the same time — one update can be lost.

## For AI coding agents

Read [`AGENTS.md`](AGENTS.md) first. Assignment documents are in [`docs/`](docs/).
