# Task 7 — Mitigation and verification

Fixed: the top two risks from Task 5 — **R1** (damaged data file locks out every command) and
**R3** (`export --out` silently overwrites files). Each fix also covered a related risk in the
same code: R2 (interrupted save) and R5 (Windows encoding / line endings).

## Process (how each AI-proposed diff was reviewed)

1. Work on a separate branch `task7-fixes` (AGENTS.md §8: no edits on `main`).
2. **Tests first:** write tests for the risk, run them on the unfixed code → they must fail.
3. Apply the smallest fix; run all tests, ruff, mypy, compileall → all must pass.
4. The AI (Claude) produced the diffs as patch files. **I reviewed them before accepting:** applied
   them to the `task7-fixes` branch on my laptop, read the code diff with `git diff main -- habit_tracker`
   (screenshots: [`task7_review_diff_1.png`](evidence/task7_review_diff_1.png),
   [`task7_review_diff_2.png`](evidence/task7_review_diff_2.png)), ran the full test suite on Windows,
   and only then merged into `main` myself (`git merge task7-fixes`, commit `9dbcc9e` on GitHub).

## Mitigation record 1 — R1 (+ R2)

| Field | Detail |
|---|---|
| Risk | R1 COR-2: invalid `habits.json` → every command crashes with a traceback, even `reset`. R2 COR-3: interrupted save leaves an empty file. |
| Change | `storage.py`: `load_habits` catches `ValueError`/`TypeError` and raises `DataFileError` with the file path and reason. `save_habits` writes to `habits.json.tmp`, then `os.replace` (atomic) and removes the temp file on failure. Path defaults are now looked up at call time (`path=None` → `DATA_FILE`), so tests can redirect them safely. `cli.py`: `reset` no longer loads the file; other commands catch `DataFileError` → message + exit code 1. |
| Size | `storage.py` +28/−10, `cli.py` +6/−1 (from `git show --numstat`) |
| New tests | `tests/test_safety.py`: 5 damaged-file variants (bad JSON, empty, extra key, missing keys, not a list), `reset` on a damaged file, interrupted save keeps old data and leaves no temp file — 7 tests |
| Before fix | **7 failed / 0 passed** ([`task7_m1_before.txt`](evidence/task7_m1_before.txt)). Note: on the old code some failures are also caused by R8 (old storage ignores the redirected path); the bugs themselves were reproduced directly in Task 4. |
| After fix | **23 passed / 0 failed**, ruff + mypy clean ([`task7_m1_after.txt`](evidence/task7_m1_after.txt)). Real CLI with `{broken` file: `report` → `error: data file … is damaged (…)` + `Fix the file by hand, or run 'reset'…`, exit 1; `add` same; `reset` → `All data deleted`, exit 0. |
| Lint issue found during the fix | First run: ruff `SIM117` (nested `with`) in my new test → combined, re-run clean. |

## Mitigation record 2 — R3 (+ R5)

| Field | Detail |
|---|---|
| Risk | R3 SEC-1: `export --out` overwrites any file, including `data/habits.json`. R5 COR-4: on Windows the export has `\r\r\n` line endings and crashes on Kazakh letters (cp1251), leaving a 0-byte file. |
| Change | `cli.py`: new `--force` flag. Before writing, `_is_data_file()` refuses the data file (compared with `os.path.samefile`, or normalized absolute path if a file does not exist yet) — **even with `--force`**. An existing file is refused unless `--force`. The file is opened with `encoding="utf-8", newline=""`. |
| Size | `cli.py` +15/−1 (from `git show --numstat`) |
| New tests | refuse existing file (content untouched), `--force` overwrites, data file refused with and without `--force` (data still loads), Kazakh name `Әдет` exported as UTF-8 with exactly one `\r\n` per line — 4 tests |
| Before fix | **3 failed / 8 passed** on Linux ([`task7_m2_before.txt`](evidence/task7_m2_before.txt)). The UTF-8 test **passed** before the fix on Linux, because Linux defaults hide the bug — the real "before" is the Windows run in Task 4 (`\r\r\n`, `UnicodeEncodeError`, 0-byte file). |
| After fix | **27 passed / 0 failed** on Linux ([`task7_m2_after.txt`](evidence/task7_m2_after.txt)) **and on Windows** ([`task7_windows_tests.png`](evidence/task7_windows_tests.png)) — including `test_export_file_is_utf8_with_single_crlf`. Windows export bytes: `b'name,created,streak,weekly_percent\r\n'` (single `\r\n`) ([`task7_windows_export_merge.png`](evidence/task7_windows_export_merge.png)). Real CLI: `--out data/habits.json` → refused (exit 1) with and without `--force`, `report` still works; existing `notes.txt` → refused, content kept; with `--force` → overwritten. |
| Lint issue found during the fix | First run: ruff `UP012` (`.encode("utf-8")` is redundant) in my new test → fixed, re-run clean. |

## Baseline vs final checks

| Check | Baseline (`baseline` tag) | Final (`main` after Task 7) |
|---|---|---|
| `python -m pytest` | 6 passed, 0 failed | **27 passed, 0 failed** (Linux and Windows) |
| Coverage (`--source=habit_tracker`) | 49% (`cli.py` 0%) | **98%** (`cli.py` 97%, `storage.py` 100%) |
| `ruff check --isolated .` | pass | pass |
| `mypy habit_tracker` | pass | pass |
| `python -m compileall -q habit_tracker` | pass | pass |

Evidence: [`task1_baseline.txt`](evidence/task1_baseline.txt), [`task7_final_checks.txt`](evidence/task7_final_checks.txt).

### Acceptance criteria after Task 7

| AC | Holds? | Evidence |
|---|---|---|
| AC1 CLI works, output format kept | Yes for valid input. **Intended change:** `export --out` to an *existing* file now stops with an error unless `--force`. | 10 CLI tests pass; demo in `task7_m2_after.txt` |
| AC2 streak / weekly % unchanged | Yes | `tracker.py` not changed; tests pass |
| AC3 old data file still loads | Yes | `habits.json` written by the **baseline** version exported correctly by the final version (`task7_final_checks.txt`) |
| AC4 export columns kept | Yes | `test_export_*` pass |
| AC5 no tests removed or weakened | Yes | `git diff baseline -- tests/test_tracker.py` → no changes; 6 → 27 tests |

## Tests NOT executed

- Real Ctrl-C / power loss during a save (only simulated with `mock.patch("json.dump", side_effect=KeyboardInterrupt)`).
- Two commands running at the same time (concurrent writes) — the lost-update part of R2 is **not** fixed.
- `os.replace` on Windows while `habits.json` is open in another program (could raise `PermissionError`).
- Opening the exported CSV in Excel (R9 formula injection — not in scope).
- macOS; Python versions other than 3.13; a symbolic link pointing at the data file (handled by `samefile` in code, not tested).
- The full CLI demos (damaged file, `--out` refusal) were run on Linux; on Windows only the test suite and one export were run.

## Updated risk scores

| ID | Before (L×I) | After (L×I) | Why |
|---|---|---|---|
| **R1** | 2×3 = **6** | 2×1 = **2** | The file can still be damaged (hand edit, other programs), but now the user gets a clear message and `reset` works. Impact drops from "app unusable" to "annoyance + one command". |
| **R2** | 1×3 = 3 | 1×1 = **1** | Atomic save: an interrupted save keeps the old complete file (tested). Concurrent runs can still lose one update. |
| **R3** | 2×3 = **6** | 1×2 = **2** | Data file can never be overwritten; other files need an explicit `--force`. Residual: `--force` can still overwrite a wrong file the user chose. |
| **R5** | 3×2 = 6 | 1×1 = **1** | UTF-8 + `newline=""`; verified on Windows. |
| R4, R6, R7, R8, R9, R10, R11 | unchanged | unchanged | Not in scope (see register). R8 is **partly** reduced: storage now uses `DATA_FILE` at call time, and the new tests redirect it — but the old `test_cli.py` fixture is unchanged. |

New top risks after Task 7: **R4** (duplicate check-ins, 6), **R6** (`reset` without confirmation, 6).

## Remaining limitations and trade-offs

- **Recovery is still manual:** the message tells the user to fix the file or run `reset`, which deletes all data. A backup file (e.g. keep `habits.json.bak` on every save) would be better — not done to keep the change minimal.
- `DataFileError` covers bad JSON and wrong structure, but not `PermissionError` or other OS errors — they still show a traceback.
- A wrong `created`/`checkins` *type* (e.g. `"checkins": 5`) still loads and then crashes in a calculation with `TypeError: 'int' object is not iterable` (checked) — validation of field types was not added.
- `--force` is a new flag: scripts that relied on overwriting `--out` silently must now add it (deliberate behaviour change).
- The error message shows the raw data path including `..` (e.g. `habit_tracker/../data/habits.json`); correct, but not pretty.
