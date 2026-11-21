"""CLI and export tests. They pin down the current output for valid input (AC1, AC4)
so refactoring can be checked against them. They never touch the real data/habits.json."""
import csv
import io
import json
from datetime import date

import pytest

from habit_tracker import cli, storage
from habit_tracker.exporter import export
from habit_tracker.tracker import add_habit, check_in

TODAY = date(2026, 11, 21)


@pytest.fixture
def data_file(tmp_path, monkeypatch):
    """Redirect the CLI's load/save to a temporary file."""
    path = str(tmp_path / "habits.json")
    real_load, real_save = storage.load_habits, storage.save_habits
    monkeypatch.setattr(storage, "load_habits", lambda: real_load(path))
    monkeypatch.setattr(storage, "save_habits", lambda habits: real_save(habits, path))
    return path


def run_cli(capsys, *args):
    cli.main(list(args))
    return capsys.readouterr().out


def make_habits():
    habits = []
    add_habit(habits, "Read", TODAY)
    for d in [20, 21]:
        check_in(habits, "Read", date(2026, 11, d))
    return habits


# ---------- CLI end-to-end (AC1) ----------

def test_cli_add_done_report_text(data_file, capsys):
    assert run_cli(capsys, "add", "Read") == "Added habit: Read\n"
    today = date.today().isoformat()
    assert run_cli(capsys, "done", "Read") == f"Checked in 'Read' for {today}\n"
    assert run_cli(capsys, "report") == "Read                 streak:   1  week:  14%\n"


def test_cli_report_with_no_habits_prints_nothing(data_file, capsys):
    assert run_cli(capsys, "report") == ""
    assert run_cli(capsys, "report", "--format", "json") == "[]\n"


def test_cli_report_text_same_as_export_text(data_file, capsys):
    run_cli(capsys, "add", "Read")
    run_cli(capsys, "done", "Read")
    assert run_cli(capsys, "report", "--format", "text") == run_cli(capsys, "export", "--format", "text")


def test_cli_report_json_values(data_file, capsys):
    run_cli(capsys, "add", "Read")
    run_cli(capsys, "done", "Read")
    row = json.loads(run_cli(capsys, "report", "--format", "json"))[0]
    assert row["name"] == "Read"
    assert row["streak"] == 1
    assert row["weekly_percent"] == 14


def test_cli_export_to_file(data_file, capsys, tmp_path):
    run_cli(capsys, "add", "Read")
    out = tmp_path / "out.csv"
    assert run_cli(capsys, "export", "--format", "csv", "--out", str(out)) == f"Exported to {out}\n"
    assert out.read_text().splitlines()[0] == "name,created,streak,weekly_percent"


# ---------- Export formats (AC4) ----------

def test_export_csv_columns_and_values():
    rows = list(csv.reader(io.StringIO(export(make_habits(), "csv", TODAY))))
    assert rows[0] == ["name", "created", "streak", "weekly_percent"]
    assert rows[1] == ["Read", "2026-11-21", "2", "29"]


def test_export_json_columns():
    data = json.loads(export(make_habits(), "json", TODAY))
    assert list(data[0].keys()) == ["name", "created", "streak", "weekly_percent"]


def test_export_text():
    assert export(make_habits(), "text", TODAY) == "Read                 streak:   2  week:  29%"


def test_export_unknown_format_raises():
    with pytest.raises(ValueError):
        export(make_habits(), "xml", TODAY)


def test_cli_unknown_format_rejected_consistently(data_file, capsys):
    # Added with the Task 3 refactor: both commands now reject a bad format the same
    # way (argparse error, exit code 2) instead of "Unknown format"+exit 0 / traceback.
    for command in ("report", "export"):
        with pytest.raises(SystemExit) as exc:
            cli.main([command, "--format", "xml"])
        assert exc.value.code == 2
        assert "invalid choice: 'xml'" in capsys.readouterr().err
