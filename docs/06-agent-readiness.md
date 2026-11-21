# Task 6 — Agent-readiness audit

Audited version: commit `f3be64d` (after Tasks 1–5, **before** the Task 7 fixes).
Evidence: [`evidence/task6_readiness.txt`](evidence/task6_readiness.txt) (all commands run on this commit).

## 1. Readiness levels used

| Level | Meaning |
|---|---|
| **1 Baseline** | Code runs and some tests exist, but how to work in the repo is unclear or wrong; an agent would have to guess. |
| **2 Documented** | An accurate, agent-facing guide exists (purpose, setup, safe commands, forbidden actions, review gates) and the documented checks really work. Rules are enforced by **people**, not tooling. |
| **3 Agent-ready** | Level 2, plus: reproducible pinned setup, accurate README, automated gates (CI / hooks) that run tests and lint on every change, technical guardrails for destructive actions, and tests covering the critical paths. |

## 2. Audit checklist

| # | Area | Status | Evidence |
|---|---|---|---|
| 1 | Readable structure | ✅ Pass | 5 small modules with clear roles (`cli`, `tracker`, `exporter`, `storage`, `models`); `tests/`, `docs/` separated. |
| 2 | README accuracy | ❌ Fail | `README.md` lines 15–18 still say `python main.py …` (file does not exist), line 26 says `pytest` (fails: `2 errors during collection`). AGENTS.md corrects this, but humans read the README. |
| 3 | Reproducible setup | ⚠️ Partial | Setup steps in AGENTS.md §3 work (re-run on Windows from scratch in Task 1). No `pyproject.toml`, no declared Python version, no lock file. |
| 4 | Pinned dependencies | ❌ Fail | `requirements.txt` = `pytest` (no version); ruff, mypy, coverage not declared anywhere (risk R10). |
| 5 | Tests | ✅ Pass | `python -m pytest -q` → **16 passed**; coverage **94%** (was 49% at baseline). Gaps: no AC3 test (R7), no `reset` test (R8). |
| 6 | Lint / type checks | ⚠️ Partial | `ruff check --isolated .` passes, `mypy` passes — but neither is configured in the repo, and mypy checks little because there are no type hints. |
| 7 | Build command | ⚠️ Partial | No real build or package. Only `python -m compileall -q habit_tracker` (exit 0) as a syntax check. |
| 8 | Logging | ❌ Fail (minor for a CLI) | No `logging` module; 6 `print()` calls in `cli.py`. Errors appear as raw tracebacks (R1, R11). Nothing records what a command or agent did. |
| 9 | Security safeguards | ⚠️ Partial | ✅ no secret-like strings in code; ✅ `data/` git-ignored (real data never committed). ❌ `.env`, `.coverage`, `.mypy_cache`, `.ruff_cache` not ignored; ❌ no checks on `export --out` path (R3); ❌ `reset` deletes with no confirmation (R6). |
| 10 | AGENTS.md — permissions | ✅ Pass | §8 table: read + safe commands allowed; edits only on a branch; merge, push, dependency changes **human only**. |
| 11 | AGENTS.md — safe commands | ✅ Pass | §4 lists 6 commands; all were run and work (Task 2). Warns against the broken README commands. |
| 12 | AGENTS.md — prohibited actions | ✅ Pass | §7: secrets, deploy/push, destructive commands (`reset`, `git reset --hard`, force-push, deleting the `baseline` tag), dependency changes without approval, out-of-scope edits, disabling tests. |
| 13 | AGENTS.md — review gates | ✅ Pass (manual) | §8: 5-point review before merge (diff, real test output, new tests, AC1–AC5, no forbidden action). §9: required report. All **manual** — nothing enforces them. |
| 14 | AGENTS.md — accuracy | ⚠️ Partial | §2 architecture lists only `test_tracker.py`; `test_cli.py` (added in Task 3) is missing. |
| 15 | Automated gates (CI / hooks) | ❌ Fail | No `.github/workflows`, no `.claude/` settings or hooks, no pre-commit. |

Totals: 6 pass · 5 partial · 4 fail.

## 3. Readiness level: **2 — Documented**

**Why not level 1:** an agent does not need to guess. AGENTS.md gives an accurate purpose,
architecture, setup, verified safe commands, explicit forbidden actions and review gates, and
the documented test command really works (16 passed, on Linux and Windows).

**Why not level 3:** every rule is enforced only by a human reading the diff. The environment is
not reproducible (unpinned, undeclared tools), the README contradicts AGENTS.md, there is no CI or
hook to run the tests automatically, and dangerous actions (`reset`, `export --out` overwriting files)
are blocked only by text, not by the code or tooling.

## 4. Missing evidence for level 3

| Needed for level 3 | Status / evidence missing | Related risk |
|---|---|---|
| README matches reality | README still says `python main.py` and `pytest` | W1, W2 |
| Pinned, complete dependencies | No versions; no dev-requirements file; no Python version | R10 |
| CI runs tests + lint on every push | No workflow; no recorded CI run | — |
| Technical guardrails for destructive commands | `reset` has no confirmation; no agent hook/permission settings | R6 |
| Safe file handling | `export --out` overwrites anything; broken data file locks the app | R3, R1 → **fixed in Task 7** |
| Tests for critical guarantees | No AC3 (old data loads) test, no `reset` test | R7, R8 |
| Logging / clean errors | Raw tracebacks, no log of actions | R1, R11 |
| AGENTS.md tested with an agent that auto-loads it | Never run with Claude Code or another auto-loading agent (disclosed in Task 2) | — |
| `.gitignore` covers secrets and tool caches | `.env`, `.coverage`, `.mypy_cache`, `.ruff_cache` missing | — |

Task 7 addresses the top two risks (R1, R3). The level is re-checked after Task 7 in the release
decision (Task 9); fixing two risks alone does **not** reach level 3.
