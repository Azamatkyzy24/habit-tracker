# Task 3 — Focused pattern decision

## 1. Maintainability problem: duplicated format conditionals

The rule "how do we show a habit in format X" was written **twice**: in `exporter.py`
(`export` command) and again inside `cli.py` (`report` command, mixed with printing).

```
$ grep -n -E 'format ==|fmt ==' habit_tracker/*.py        (baseline)
habit_tracker/cli.py:45:        if args.format == "text":
habit_tracker/cli.py:48:        elif args.format == "json":
habit_tracker/exporter.py:9:    if fmt == "json":
habit_tracker/exporter.py:19:   elif fmt == "csv":
habit_tracker/exporter.py:26:   elif fmt == "text":
```

The two copies had **already drifted apart** (observed by running both commands, baseline):

| Input | `report` | `export` |
|---|---|---|
| `--format json` | no `created` field | has `created` field |
| `--format csv` | not supported ("Unknown format") | supported |
| `--format xml` (invalid) | prints `Unknown format`, **exit code 0** (looks like success) | Python **traceback**, exit code 1 |

Consequence: every new format or column has to be changed in two places, and the copies
disagree. Also `cli.py` mixed UI (argument parsing, printing) with formatting logic.

## 2. Options considered

| Option | Verdict |
|---|---|
| **A. Do nothing** | Rejected — the drift above is a real defect, not just style. |
| **B. Adapter** | Not applicable — there is no incompatible external interface to wrap. |
| **C. Class-based Strategy** (`Formatter` base class + `JsonFormatter`, `CsvFormatter`, …) | Rejected — 3 formats of 1–5 lines each; classes would add more code than they save. |
| **D. Function-based Strategy**: one function per format in a `FORMATTERS` dict; `report` and `export` both use it | **Chosen** |

**Is a pattern actually necessary?** Only a light one. Most of the benefit comes from
`report` reusing `export` (removing the copy). The `FORMATTERS` dict adds two things a
plain `if/elif` would not: one place to add a format, and one list of valid formats that
argparse can use (`choices=FORMATTERS`) so both commands validate input the same way.
In Python a dict of functions *is* the Strategy pattern without extra classes — so this is
the smallest version that solves the problem.

## 3. The refactoring (one focused change)

- `exporter.py`: `_rows()` builds the values once; `to_json`, `to_csv`, `to_text` each
  format them; `FORMATTERS` maps format name → function; `export()` looks it up.
- `cli.py`: `report` now calls `export(habits, args.format)`; both `report` and `export`
  use `choices=FORMATTERS`. Removed unused imports (`json`, `current_streak`, `weekly_completion`).

### Before / after structure

| Metric | Before (`baseline`) | After |
|---|---|---|
| Format `if/elif` branches | 5 (in 2 files) | **0** (dict lookup in 1 place) |
| Places that define text/JSON output | 2 | **1** |
| How invalid format is handled | 2 different ways (exit 0 / traceback) | 1 way: argparse error, exit 2 |
| `cli.py` lines | 78 | 66 |
| `exporter.py` lines | 32 | 52 |

Trade-off: `exporter.py` got longer (one small named function per format + docstring),
but the total logic is in one place and `cli.py` no longer does formatting.

## 4. Proof that acceptance criteria still hold

**Step 1 — before refactoring**, 9 characterization tests were added to `tests/test_cli.py`
and run on the **unchanged** production code: **15 passed** ([`task3_before.txt`](evidence/task3_before.txt)).

**Step 2 — after refactoring**: **16 passed, 0 failed** (the 15 above + 1 new test for the
consistent invalid-format error). ruff and mypy clean. Coverage 49% → 94%
([`task3_after.txt`](evidence/task3_after.txt)).

**Step 3 — real output comparison**: baseline and refactored versions run on the same
`habits.json` with 2 habits ([`task3_output_comparison.txt`](evidence/task3_output_comparison.txt)):

| Command | Result |
|---|---|
| `report`, `report --format text` | identical |
| `export --format csv / json / text` | identical |
| `report --format json` | **different: now also includes `"created"`** |

| Criterion | Holds? | Evidence |
|---|---|---|
| AC1 CLI works, output format kept | Yes, with one documented change: `report --format json` gained the `created` field. Existing fields and values are unchanged; this was the drift being fixed. | output comparison, `test_cli_*` |
| AC2 streak / weekly % unchanged | Yes | `test_streak_three_days`, `test_weekly_completion`, identical outputs |
| AC3 old data file loads | Yes (storage not touched) | baseline-format `habits.json` used in Step 3 |
| AC4 export columns kept | Yes | `test_export_json_columns`, `test_export_csv_columns_and_values`, identical exports |
| AC5 no tests removed/weakened | Yes — 6 original tests unchanged, 10 added | `git diff baseline -- tests/test_tracker.py` is empty |

Behaviour change for **invalid** input (intended): `report --format xml` used to print
"Unknown format" and exit 0; it now exits with code 2 and an argparse error, like `export`.
