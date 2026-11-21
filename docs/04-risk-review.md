# Task 4 — Read-only AI risk review

## 1. How the review was done

| Item | Detail |
|---|---|
| Reviewer | A **separate, fresh** Claude chat (claude.ai, free plan, 21 Nov 2026) with no access to this project's main conversation |
| Input | `habit-tracker-main.zip` downloaded from GitHub at commit `0309ee3` (after Task 3; GitHub commit ID) |
| Prompt | Read-only review: "do NOT rewrite files, do NOT produce patches"; 8–10 risks across correctness, maintainability, security, dependency, agent operations; cause → event → consequence, location, reproduction command, confidence; "do not invent test results" |
| Did it modify files? | No. It read files with `unzip -p` and produced no code changes. It marked every expected output "not executed". |
| Output | 10 numbered findings + 4 extra notes — full text in the AI evidence appendix |

**Verification:** I re-ran every reproduction command myself — on Linux on a **throwaway copy** of the
repo, and COR-4 on my Windows laptop with a temporary file only (so no real data could be affected). Full output: [`evidence/task4_verification.txt`](evidence/task4_verification.txt).

Classification used: **Confirmed** = reproduced with a command or seen directly in code/files ·
**Plausible / unverified** = mechanism is real but the consequence was not demonstrated ·
**Unsupported** = the claim does not hold when checked.

## 2. Findings and verdicts

| ID | Category | AI claim (short) | My verification (actual result) | Verdict |
|---|---|---|---|---|
| COR-1 | Correctness | `done` twice on a day is stored twice → weekly % can exceed 100% | 8 check-ins on one day → `114 1 8` (114%, streak 1, 8 entries) | **Confirmed** |
| COR-2 | Correctness | A broken `habits.json` makes every command fail, even `reset` | `{broken` → `reset` exits 1 with `JSONDecodeError`, file still there. Extra key → `TypeError: unexpected keyword argument 'extra'`. Only `--help` works. | **Confirmed** |
| COR-3 | Correctness | `save_habits` truncates the file before writing → interruption leaves it empty; concurrent runs lose updates | Simulated interruption during `json.dump`: file 76 bytes → `''`. Concurrent-run part not tested (single-user assumption). | **Confirmed** (interruption) / **Plausible** (concurrency) |
| COR-4 | Correctness / portability | `export --out` uses `open(..., "w")` with no `encoding`/`newline` → `\r\r\n` line endings and possible `UnicodeEncodeError` on Windows | Run by me on **Windows 11** (locale encoding `cp1251`), same `open(path, "w")` call as `export --out`: CSV bytes = `b'name,created,streak,weekly_percent\r\r\nRead,2026-11-21,0,0\r\r\n'` (doubled `\r`). Habit name `әdet` → `UnicodeEncodeError: 'charmap' codec can't encode character '\u04d9'`. The failed write still **created an empty file**: `dir *.csv` → `out2.csv` length **0**. Screenshots: [`task4_windows_cor4.png`](evidence/task4_windows_cor4.png), [`task4_windows_cor4_empty_file.png`](evidence/task4_windows_cor4_empty_file.png) | **Confirmed** (Windows) |
| SEC-1 | Security | `export --out` writes to any path with no check → can overwrite the data store | `export --format csv --out data/habits.json` succeeded, then `report` crashed with `JSONDecodeError` — all habits lost | **Confirmed** |
| SEC-2 | Security | Habit names are written to CSV unescaped → formula injection (`=1+1`) in Excel | CSV line is `=1+1,2026-11-21,0,0` (unescaped). Not opened in Excel, so the "evaluated as formula" part is not demonstrated. | **Confirmed** (unescaped output) / **Plausible** (Excel impact) |
| DEP-1 | Dependency | `requirements.txt` is only `pytest`, unpinned; ruff/mypy/coverage not listed; no `pyproject.toml`. Also: Task 1 evidence says "fresh venv" but shows "Requirement already satisfied" | All facts confirmed by `cat`/`grep`/`ls`. The evidence-wording point is **correct** — it was an error in my Task 1 write-up, now corrected in `01-baseline.md`. | **Confirmed** |
| MNT-1 | Maintainability | Test fixture doesn't redirect `storage.reset`; data path is fixed as a default argument so patching `DATA_FILE` can't redirect it; `test_cli.py:44` uses `date.today()` | `inspect.signature(storage.reset)` → `(path='.../data/habits.json')` (path baked in); no `reset` test exists; `date.today` found at line 44. Harm only occurs if someone writes such a test. | **Confirmed** (gaps) / **Plausible** (data loss from a future test) |
| AGT-1 | Agent ops | `reset` deletes all data instantly; only AGENTS.md prose prevents an agent from running it; no hooks/CI/settings | `reset` → "All data deleted", `data/` empty, exit 0, no prompt. No `.claude/`, `.github/`, `pyproject.toml`; no `input(`/`--yes`/confirm in `cli.py`. | **Confirmed** |
| AGT-2 | Agent ops | AC3 (old data loads) has no test; AC5 check "≥ 6 passed" is stale with 16 tests, so "deleting the 10 CLI tests still meets AC5" | No AC3 test (confirmed); `≥ 6` wording confirmed (16 collected). **But** the claim that deleting tests "still meets AC5" is wrong: AC5's criterion text says "none are deleted or weakened" — only the *verification command* is weak. | **Confirmed** (AC3, stale check) / **Unsupported** (AC5 can be met by deleting tests) |

### Extra AI notes (checked, not counted in the 10)

| Note | Result | Verdict |
|---|---|---|
| Streak is 0 until you check in today | 11-day streak, before today's check-in → `0` | Confirmed (design choice; see register) |
| Invalid input gives tracebacks; empty name accepted | `done Nope` → `ValueError` traceback; `--date 2026-13-40` → traceback; `add ''` → "Added habit: " | Confirmed |
| `save_habits('habits.json')` (bare file name) fails | `FileNotFoundError: ... ''` from `os.makedirs` | Confirmed (not reachable from the CLI) |
| README still wrong; AGENTS.md §2 lists only `test_tracker.py` | Both true (README = W1 from Task 1; AGENTS.md is outdated since Task 3) | Confirmed |

## 3. Summary

- **10 findings, 5 categories** (correctness 4, security 2, dependency 1, maintainability 1, agent operations 2).
- **All 10 confirmed in their main claim** with real command output (COR-4 on Windows, the rest on Linux); in 4 findings
  part of the claim stays **plausible** (concurrency, Excel impact, future test, AC5 deletion).
- **1 unsupported claim** (AGT-2's AC5 part): the AI read the verification command but missed the
  criterion text.
- **Useful catch:** DEP-1 found a real inaccuracy in my own evidence description.
- Overlap with my own Task 1 review: DEP-1 = W3, AGT-1 extends the `reset` concern noted as
  "unverified" in Task 1. COR-1, COR-2, COR-3, COR-4, SEC-1, SEC-2 are **new** — the independent review added value.

These findings feed the risk register in Task 5.
