# Release condition C1: every command in the new README, run on a throwaway copy of the release-candidate commit (Linux)
$ python -m pip install -r requirements.txt
Requirement already satisfied: iniconfig>=2 in ~/venv/lib/python3.13/site-packages (from pytest->-r requirements.txt (line 1)) (2.3.1)
Requirement already satisfied: packaging>=24 in ~/venv/lib/python3.13/site-packages (from pytest->-r requirements.txt (line 1)) (26.3)
Requirement already satisfied: pluggy<2,>=1.6 in ~/venv/lib/python3.13/site-packages (from pytest->-r requirements.txt (line 1)) (1.7.0)
Requirement already satisfied: pygments>=2.15 in ~/venv/lib/python3.13/site-packages (from pytest->-r requirements.txt (line 1)) (2.21.0)
[exit code: 0]
$ python -m habit_tracker.cli add "Read 20 pages"
Added habit: Read 20 pages
[exit code: 0]
$ python -m habit_tracker.cli done "Read 20 pages"
Checked in 'Read 20 pages' for 2026-11-21
[exit code: 0]
$ python -m habit_tracker.cli done "Read 20 pages" --date 2026-11-20
Checked in 'Read 20 pages' for 2026-11-20
[exit code: 0]
$ python -m habit_tracker.cli report
Read 20 pages        streak:   2  week:  29%
[exit code: 0]
$ python -m habit_tracker.cli report --format json
    "streak": 2,
    "weekly_percent": 29
  }
]
[exit code: 0]
$ python -m habit_tracker.cli export --format csv --out habits.csv
Exported to habits.csv
[exit code: 0]
$ python -m pytest -v
tests/test_tracker.py::test_export_json PASSED                           [ 96%]
tests/test_tracker.py::test_save_and_load PASSED                         [100%]

============================== 27 passed in 0.13s ==============================
[exit code: 0]
$ pytest -q   (README says this does NOT work)
3 errors in 0.10s
