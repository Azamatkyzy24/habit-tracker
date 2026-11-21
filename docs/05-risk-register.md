# Task 5 — Risk register

Reviewed version: commit `28ed354` (after Tasks 1–4). Every risk below was **confirmed** with
real output in Task 4 ([`04-risk-review.md`](04-risk-review.md),
[`evidence/task4_verification.txt`](evidence/task4_verification.txt)) unless marked otherwise.
No execution evidence is invented: "planned" values are estimates until Task 7 re-runs the checks.

## Scoring scale

**Likelihood (L)** — 1 = needs an unusual event · 2 = can happen in normal use or by a typo /
agent action · 3 = happens in everyday use.
**Impact (I)** — 1 = annoyance, no wrong data · 2 = wrong numbers or a broken export, stored data safe ·
3 = stored habit data lost or the app unusable.
**Score = L × I** (1–9). 6–9 high · 3–4 medium · 1–2 low.
Context used for scoring: single-user, local CLI, no server, the owner uses Windows (cp1251) and
may type Kazakh/Russian habit names.

## A. Identification and scoring

| ID | Finding | Category | Cause → Event → Consequence | Component | Evidence | L | I | Score |
|---|---|---|---|---|---|---|---|---|
| R1 | COR-2 | Correctness | `load_habits` has no error handling and runs before every command → `habits.json` is invalid (empty, partial, edited, wrong keys) → **every** command crashes, including `reset`; user must fix the file by hand | `storage.load_habits`, `cli.main` | `{broken` → `reset` exit 1 `JSONDecodeError`, file still there; extra key → `TypeError` | 2 | 3 | **6** |
| R2 | COR-3 | Correctness | `save_habits` opens with `"w"` (truncates first) → process interrupted during write → file left empty → R1 lockout, all data gone | `storage.save_habits` | Simulated interruption: 76 bytes → `''` | 1 | 3 | 3 |
| R3 | SEC-1 | Security | `export --out` writes to any path with no checks → user/agent passes an existing file (or `data/habits.json`) → file silently replaced; if it is the store, all habits lost | `cli.main` (export) | `export --out data/habits.json` OK, then `report` → `JSONDecodeError` | 2 | 3 | **6** |
| R4 | COR-1 | Correctness | `check_in` stores duplicates and `weekly_completion` counts entries → user runs `done` twice in a day → weekly % wrong, can exceed 100% | `tracker.check_in`, `weekly_completion` | 8 check-ins one day → `114%` | 3 | 2 | **6** |
| R5 | COR-4 | Correctness | `open(args.out, "w")` without `encoding`/`newline` → export on Windows → CSV rows end `\r\r\n`; Kazakh letters crash with `UnicodeEncodeError` and leave a 0-byte file | `cli.main` (export) | Windows: `\r\r\n` bytes; `'ә'` → `UnicodeEncodeError`; `out2.csv` 0 bytes | 3 | 2 | **6** |
| R6 | AGT-1 | Agent ops | `reset` deletes the data file immediately, no confirmation/backup; only AGENTS.md prose forbids it → agent or user runs it by mistake → all data lost, not in git | `cli.main` (reset), `storage.reset` | `reset` → "All data deleted", exit 0, no prompt; no hooks/CI | 2 | 3 | **6** |
| R7 | AGT-2 | Agent ops | AC3 (old data loads) has no automated test; AC5 check text says "≥ 6 passed" → agent changes `Habit` fields or serialization → existing user files stop loading while all tests pass | `models.Habit`, `storage`, `docs/01` §5 | No AC3 test; `≥ 6` vs 16 collected. (AC5 deletion claim was **unsupported**.) | 1 | 3 | 3 |
| R8 | MNT-1 | Maintainability | Data path is baked into default arguments; fixture doesn't cover `reset` → someone writes a `reset` CLI test → test deletes the developer's real `data/habits.json` | `storage` defaults, `tests/test_cli.py` | `signature(reset)` → path fixed; no `reset` test | 1 | 3 | 3 |
| R9 | SEC-2 | Security | Names written to CSV unescaped → name starting `=`/`@`/`+`/`-` exported and opened in Excel → evaluated as a formula | `exporter.to_csv` | CSV line `=1+1,2026-11-21,0,0` (Excel not tested → impact plausible) | 1 | 2 | 2 |
| R10 | DEP-1 | Dependency | `requirements.txt` = `pytest` unpinned; ruff/mypy/coverage not declared; no `pyproject.toml` → new environment gets different versions or lacks tools → results not reproducible | `requirements.txt` | pytest 9.1.1 vs 9.2.0 from same file; tools "not listed" | 2 | 1 | 2 |
| R11 | Extra | Correctness | No input validation in `add`/`done` → unknown habit, bad date or empty name → Python traceback / nameless habit | `cli.main`, `tracker` | `done Nope` → traceback; `--date 2026-13-40` → traceback; `add ''` accepted | 3 | 1 | 3 |

Not registered as a risk: "streak is 0 until you check in today" (confirmed, but it is a design
choice covered by AC2 — changing it would be a feature decision, not a fix).

## B. Treatment

| ID | Score | Mitigation | Owner | Verification plan | Residual (planned) |
|---|---|---|---|---|---|
| R1 | 6 | Load errors give a clear message and exit code instead of a traceback; `reset` must work without loading the file | Aidana | New test: invalid JSON and wrong keys → clean error; `reset` succeeds on a broken file | L1 × I2 = 2 (file can still break; the user can recover) |
| R2 | 3 | Atomic save: write to a temp file, then `os.replace` | Aidana | Test: simulated interruption leaves the old file intact | L1 × I1 = 1 |
| R3 | 6 | Refuse to overwrite an existing file unless `--force`; never allow the data store as `--out` | Aidana | Tests: existing file → error, unchanged; `--force` overwrites; data store path always refused | L1 × I2 = 2 (`--force` can still overwrite other files) |
| R4 | 6 | Ignore a check-in for a day already checked in (and/or count distinct days) | Aidana | Test: `done` twice → 1 entry, weekly ≤ 100% | 1 |
| R5 | 6 | Open with `encoding="utf-8", newline=""` | Aidana | Test: Kazakh name exported and read back; bytes end with `\r\n` once; re-run on Windows | 1 |
| R6 | 6 | Add confirmation (`--yes`) or a backup before deleting; keep AGENTS.md rule; optionally a hook that blocks `reset` for agents | Aidana | Test: `reset` without `--yes` does not delete | L1 × I3 = 3 |
| R7 | 3 | Add an AC3 regression test with a baseline-format `habits.json` fixture; change AC5 check to "≥ current number of tests" | Aidana | Test exists in CI-like run; review gate in AGENTS.md §8 | 2 |
| R8 | 3 | Make the data path configurable (e.g. env var `HABITS_FILE`) and redirect it in a shared test fixture | Aidana | Test that `reset` uses the temp path | 1 |
| R9 | 2 | Prefix cells starting with `= + - @` with `'` in CSV export | Aidana | Test: `=1+1` exported as `'=1+1` | 1 |
| R10 | 2 | Pin versions (`pytest==9.2.0`), add `requirements-dev.txt` with ruff/mypy/coverage; fix README commands | Aidana | Fresh venv install from file only, record versions | 1 |
| R11 | 3 | Catch `ValueError` in CLI → short message, exit 1; reject empty names | Aidana | Tests for each bad input | 1 |

Owner: Aidana (Azamatkyzy Aidana) — single-developer project; an AI assistant may propose
changes, but she reviews and approves every diff (AGENTS.md §8).

## C. Top TWO confirmed risks for corrective action (Task 7)

Five risks share the highest score (6): R1, R3, R4, R5, R6. Tie-break rules, in order:
1. **Impact 3 before impact 2** — permanent data loss is worse than a wrong number or broken export
   → R1, R3, R6 stay; R4, R5 drop.
2. **Silent / unintended before explicit** — R6 (`reset`) is a command whose *purpose* is deletion
   and is already named in AGENTS.md §7; R1 and R3 destroy or lock data **without the user asking for it**.
3. **Coverage of other risks by the same fix**.

| Rank | Risk | Why it is first | The fix also reduces |
|---|---|---|---|
| **1** | **R1 — broken data file locks out every command (COR-2)** | It is the end state of R2 and R3: all three paths end with an unreadable file and no way to recover inside the app, not even `reset`. | R2 (adding atomic save in the same `storage.py` change is cheap) |
| **2** | **R3 — `export --out` silently overwrites any file, including the data store (SEC-1)** | Silent loss with no warning, easy to trigger by a typo or an agent; confirmed end-to-end. | R5 (the same `open()` call gets `encoding="utf-8", newline=""`) |

Next highest, kept for future work with owners above: R6, R4, R5.
