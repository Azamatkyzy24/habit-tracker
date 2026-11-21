# Task 9 — Release decision

**Reviewed version:** `main` at commit `d6549c3` (after Task 7), compared with tag `baseline` (`b2aa99e`).
"Release" here means: tag the version as `v0.2.0` and use it for my own habit tracking. There is no
server or deployment.

## Decision: **CONDITIONAL**

The version may be released **only after** the conditions in section 3 are met. They are small,
have an owner and a deadline, and none of them needs a code change to the app logic.

## 1. Evidence

### Test evidence

| Check | Baseline | Reviewed version | Where |
|---|---|---|---|
| Tests | 6 passed | **27 passed, 0 failed** — Linux **and** Windows | `task7_final_checks.txt`, `task7_windows_tests.png` |
| Coverage | 49% | **98%** | `task7_final_checks.txt` |
| ruff / mypy / compileall | pass | pass | `task7_final_checks.txt` |
| AC1–AC5 | — | all hold (AC1 with the documented `--force` change; AC3 proven with a baseline-written data file) | `07-mitigations.md` |
| Critical behaviours | data loss on broken file / `--out` | both fixed and tested, incl. Windows export with Kazakh letters | `07-mitigations.md` |

### Risk register (after Task 7)

| Risk | Score | Status for release |
|---|---|---|
| R1 damaged data file | 6 → **2** | Mitigated, verified |
| R3 `export --out` overwrites | 6 → **2** | Mitigated, verified |
| R5 Windows export | 6 → **1** | Mitigated, verified on Windows |
| R2 interrupted save | 3 → **1** | Mitigated (simulated test) |
| **R4** duplicate check-ins → weekly % > 100% | **6** | **Open** — wrong number, no data loss |
| **R6** `reset` deletes without confirmation | **6** | **Open** — data loss only if the user/agent runs `reset` |
| R7, R8, R11 | 3 | Open, low/medium |
| R9, R10 | 2 | Open, low |

### Readiness assessment

Level **2 — Documented** (Task 6). Enough for a human working with an AI assistant under review;
**not** enough for an unattended agent (no CI, no technical guardrails, unpinned dependencies).

## 2. Why not GO, why not NO-GO

**Not GO:** "no unacceptable unresolved risks" is not fully true — two risks still score 6 (R4, R6),
the README still tells users to run commands that fail (`python main.py`, `pytest`), and several
checks were only simulated (Ctrl-C, concurrent runs) or not run (Excel, macOS).

**Not NO-GO:** all critical checks pass on both platforms, the two data-loss risks that happen
**without the user asking** (R1, R3) are fixed and verified, and every remaining high risk has a
known cause, a limited impact for a single local user, and an owner and control below.
There is no critical verification gap for the main use (add, check in, report, export).

## 3. Conditions (must be true before tagging `v0.2.0`)

| # | Condition | Control | Owner | Deadline |
|---|---|---|---|---|
| C1 | README gives correct commands | Replace `python main.py` with `python -m habit_tracker.cli`, `pytest` with `python -m pytest`; document `--force`. Update AGENTS.md §2 (missing `test_cli.py`, `test_safety.py`). | Aidana | before tag, 23 Nov 2026 |
| C2 | Known limitations are visible to the user | README "Known limitations": `done` twice a day counts twice (R4); `reset` deletes everything immediately, no undo (R6); back up `data/habits.json` by copying it. | Aidana | before tag |
| C3 | No unattended AI agent works on the repo | Agents only with human review of every diff (AGENTS.md §8) until readiness level 3; background-agent rules in `08-background-agent.md`. | Aidana | ongoing |
| C4 | R4 and R6 get fixed next | R4 as the first (reviewed) agent task (Task 8 design); R6: add `--yes` confirmation. Re-score both after the fix. | Aidana | next version (v0.3.0) |
| C5 | Tests pass on the tagged commit | Run `python -m pytest -v` on Windows on the exact commit that is tagged; result must be all passed. | Aidana | at tagging |

If C1, C2 or C5 is not met → **do not tag** (treat as NO-GO for that commit).
C3 and C4 are controls that continue after the release.

## 4. Residual risk accepted with this release

Wrong weekly % if `done` is run twice (R4); total data loss if the user runs `reset` by mistake (R6,
reduced by the README warning and backup advice); concurrent runs can lose one update (R2 residual);
other OS errors and wrong field types still show a traceback (Task 7 limitations); CSV formula
injection if the CSV is opened in Excel with a malicious name (R9, low for a single user).
