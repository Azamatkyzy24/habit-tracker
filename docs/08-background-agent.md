# Task 8 — Background agent safeguards (hypothetical design)

This is a **design only**. No paid background-agent service was used, and nothing below was run
as a background task. Example configuration is illustrative and **not tested**.

## 1. The task given to the agent

> **Fix risk R4:** `done` run twice on the same day stores the day twice, so the weekly % can
> exceed 100% (confirmed in Task 4: 8 check-ins → 114%). Make a repeated check-in for the same
> day have no effect, add tests, and report back. Do not change anything else.

Why this task: it is the highest remaining risk after Task 7 (score 6), it is small and contained
in one module (`tracker.py`), and success is easy to check with tests — a good first task for an
unattended agent.

## 2. Isolation

| Safeguard | Setting |
|---|---|
| Branch | New branch `agent/r4-dedupe-checkins`, created from the current `main` (`d6549c3`) |
| Working copy | Separate **git worktree**: `git worktree add ../habit-tracker-agent -b agent/r4-dedupe-checkins main` |
| Data | The worktree has its own `data/` folder (the data path is relative to the package folder — verified in Task 3 and Task 7, where a `git worktree` of the `baseline` tag wrote its own `data/habits.json` inside the worktree), so the agent can never touch my real `data/habits.json`. Tests also redirect `storage.DATA_FILE` to a temp folder. |
| Network | None. Not needed: the code uses only the standard library and pytest is already installed, so there is no `pip install` |
| Credentials | No GitHub token, no SSH key in the agent environment → it physically cannot push |

## 3. Allowed files

| May change | May read only | Must not touch |
|---|---|---|
| `habit_tracker/tracker.py` | everything else in the repo | `data/`, `docs/evidence/`, `AGENTS.md`, `CLAUDE.md`, `requirements.txt`, `.gitignore`, `.github/`, any existing test function |
| new file `tests/test_dedupe.py` | | |
| `docs/agent-report-r4.md` (its report) | | |

A diff touching any other path is **rejected automatically** at review (rule 1 of the checklist below).

## 4. Allowed commands

```
python -m pytest -v
ruff check --isolated .
mypy habit_tracker
python -m compileall -q habit_tracker
git status | git diff | git log | git add <allowed files> | git commit   (only on its branch)
```

Everything else needs a human. Example of how this could be enforced with a Claude Code
project settings file (illustrative, not tested):

```json
{
  "permissions": {
    "allow": ["Bash(python -m pytest:*)", "Bash(ruff check:*)", "Bash(mypy:*)",
              "Bash(python -m compileall:*)", "Bash(git status)", "Bash(git diff:*)",
              "Bash(git add:*)", "Bash(git commit:*)"],
    "deny":  ["Bash(git push:*)", "Bash(git merge:*)", "Bash(git reset:*)", "Bash(git rebase:*)",
              "Bash(git tag:*)", "Bash(rm:*)", "Bash(pip:*)", "Bash(python -m habit_tracker.cli reset:*)"]
  }
}
```

## 5. Time and effort limits

| Limit | Value | Why |
|---|---|---|
| Total wall-clock time | 30 minutes | The fix is ~5 lines; longer means it is stuck or drifting |
| Single command | 2 minutes | The whole test suite runs in < 1 s |
| Fix attempts | 3 (edit → test cycles that still fail) | After that it must stop and report, not keep guessing |
| Diff size | ≤ 60 changed lines in total | Larger diff = scope creep → reject |

## 6. Prohibited operations

1. `git push`, `git merge`, `git rebase`, `git reset --hard`, force-push, deleting or moving tags (especially `baseline`).
2. Running `python -m habit_tracker.cli reset` or deleting any file outside its own new files.
3. Installing, removing or upgrading packages; editing `requirements.txt`.
4. Deleting, skipping (`@pytest.mark.skip`), or weakening any existing test or assertion.
5. Changing the data file format or the export columns (AC3, AC4).
6. Reading or creating secrets (`.env`, tokens); using real personal data in tests.
7. Deploying or publishing anything.

## 7. Artifacts the agent must deliver

| Artifact | Content |
|---|---|
| Change summary | `docs/agent-report-r4.md`: what changed and why, in 5–10 lines |
| Diff | `git diff main...agent/r4-dedupe-checkins` (also saved as `r4.patch`) |
| Test logs | Full output of `python -m pytest -v` **before** the fix (new tests must fail) and **after** (all pass, count ≥ 27 + new tests) |
| Build result | Output and exit codes of `ruff`, `mypy`, `compileall` |
| Risk notes | Edge cases considered, anything **not** tested, any behaviour change (e.g. "running `done` twice now prints a note instead of saving"), residual risk for R4 |

If any artifact is missing, the task counts as **failed**, even if the code looks correct.

## 8. Human review and approval (required before merge)

The agent cannot merge or push (no credentials, and denied commands). I (Aidana) review:

1. **Scope:** the diff only touches the allowed files.
2. **Diff:** I read every changed line and can explain it.
3. **Tests:** I re-run `python -m pytest -v` myself on Windows — I do not trust the agent's log alone.
4. **Before/after:** the new tests really failed before the fix (check the before log).
5. **Acceptance criteria AC1–AC5** still hold; no existing test changed (`git diff main -- tests/test_tracker.py tests/test_cli.py tests/test_safety.py` is empty).
6. **Prohibited operations:** none in `git log` / the report.

Only then: `git switch main`, `git merge agent/r4-dedupe-checkins`, `git push` — done by me.
There is no deployment step in this project; "release" = a tagged commit on `main` (see Task 9).

## 9. Failure and rollback handling

| Situation | What happens |
|---|---|
| Agent hits a time or attempt limit | It stops, commits nothing more, and writes the report with what it tried and the last test output. I decide: retry with a clearer task, or fix it myself. |
| Tests fail or a check is red at the end | No merge. The branch stays for inspection. |
| Diff touches a forbidden file or is too large | Rejected without merging; branch deleted. |
| Agent did something prohibited (e.g. tried `reset`) | Rejected; the worktree is thrown away (`git worktree remove --force ../habit-tracker-agent`, `git branch -D agent/r4-dedupe-checkins`); because it worked in an isolated worktree, `main` and my data are unaffected. Rules/permissions are tightened before the next run. |
| A problem is found **after** merging | `git revert <merge commit>` on `main` (a new commit, no history rewrite), push, and the risk goes back into the register. The `baseline` tag and every earlier commit stay available. |

## 10. Why this is safe enough

All damage the agent could do is limited to a throwaway worktree and a branch I can delete. It
cannot reach my data, cannot push, and cannot merge; every change passes the same human review gate
as Task 7. The weakest point is that the permission file above is untested, so for now the
**real** guarantees are the missing credentials and my manual review.
