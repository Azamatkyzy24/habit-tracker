"""Tests for the Assignment 06 feature: "Check in a habit for a date".
Example data from the report (section 1.4): today = 2026-11-27,
"Read 20 pages" already has check-ins on 11-24, 11-25 and 11-26."""
from datetime import date

import pytest

from habit_tracker import cli, storage
from habit_tracker.exporter import format_checkin
from habit_tracker.models import Habit
from habit_tracker.tracker import DuplicateCheckinError, check_in, weekly_completion
from habit_tracker.validation import ValidationError, parse_checkin_date, validate_name

TODAY = date(2026, 11, 27)


def make_habits():
    return [Habit("Read 20 pages", "2026-11-20", ["2026-11-24", "2026-11-25", "2026-11-26"])]


# ---------- E1, E3: valid check-ins (AC1) ----------

def test_e1_valid_checkin_today():
    habits = make_habits()
    habit = check_in(habits, "Read 20 pages", TODAY)
    assert format_checkin(habit, TODAY, TODAY) == (
        "Checked in 'Read 20 pages' for 2026-11-27 - streak: 4 days, this week: 57%"
    )


def test_e3_valid_checkin_past_day():
    habits = make_habits()
    check_in(habits, "Read 20 pages", TODAY)
    habit = check_in(habits, "Read 20 pages", date(2026, 11, 23))
    assert format_checkin(habit, date(2026, 11, 23), TODAY).endswith("streak: 5 days, this week: 71%")


# ---------- E2: duplicate (AC2) ----------

def test_e2_duplicate_rejected_and_data_unchanged():
    habits = make_habits()
    check_in(habits, "Read 20 pages", TODAY)
    with pytest.raises(DuplicateCheckinError, match="Already checked in 'Read 20 pages' for 2026-11-27"):
        check_in(habits, "Read 20 pages", TODAY)
    assert habits[0].checkins.count("2026-11-27") == 1
    assert weekly_completion(habits[0], TODAY) == 57


def test_weekly_never_above_100_even_with_old_duplicate_data():
    days = [f"2026-11-{d}" for d in range(21, 28)]
    habit = Habit("Read 20 pages", "2026-11-20", days + days)  # every day saved twice (old bug)
    assert weekly_completion(habit, TODAY) == 100


# ---------- E4: unknown habit (AC3) ----------

def test_e4_unknown_habit():
    with pytest.raises(ValueError, match="No habit called 'Swim'"):
        check_in(make_habits(), "Swim", TODAY)


# ---------- E5, E6: dates (AC4) ----------

def test_no_date_means_today():
    assert parse_checkin_date(None, TODAY) == TODAY


def test_today_is_allowed_boundary():
    assert parse_checkin_date("2026-11-27", TODAY) == TODAY


@pytest.mark.parametrize("text, message", [
    ("2026-11-28", "Date 2026-11-28 is in the future"),
    ("2026-12-31", "Date 2026-12-31 is in the future"),
    ("2026-13-01", "Invalid date '2026-13-01' - use YYYY-MM-DD"),
    ("2026-02-30", "Invalid date '2026-02-30' - use YYYY-MM-DD"),
    ("27.11.2026", "Invalid date '27.11.2026' - use YYYY-MM-DD"),
    ("20261127", "Invalid date '20261127' - use YYYY-MM-DD"),
    ("", "Invalid date '' - use YYYY-MM-DD"),
])
def test_e5_e6_bad_dates(text, message):
    with pytest.raises(ValidationError, match=message):
        parse_checkin_date(text, TODAY)


# ---------- E7: names (AC5) ----------

@pytest.mark.parametrize("raw", ["", "   ", None])
def test_e7_empty_name(raw):
    with pytest.raises(ValidationError, match="Habit name must not be empty"):
        validate_name(raw)


def test_name_length_boundary():
    assert validate_name("a" * 50) == "a" * 50
    with pytest.raises(ValidationError, match="at most 50 characters"):
        validate_name("a" * 51)


def test_name_is_trimmed():
    assert validate_name("  Read 20 pages  ") == "Read 20 pages"


# ---------- CLI: no traceback, exit codes (AC6) ----------

@pytest.fixture
def data_file(tmp_path, monkeypatch):
    path = str(tmp_path / "habits.json")
    real_load, real_save = storage.load_habits, storage.save_habits
    monkeypatch.setattr(storage, "load_habits", lambda: real_load(path))
    monkeypatch.setattr(storage, "save_habits", lambda habits: real_save(habits, path))
    return path


@pytest.mark.parametrize("args, message", [
    (["done", "Swim"], "error: No habit called 'Swim'"),
    (["done", ""], "error: Habit name must not be empty"),
    (["done", "Read", "--date", "2026-13-01"], "error: Invalid date '2026-13-01' - use YYYY-MM-DD"),
    (["done", "Read", "--date", "2999-01-01"], "error: Date 2999-01-01 is in the future"),
])
def test_cli_errors_exit_1_without_traceback(data_file, capsys, args, message):
    cli.main(["add", "Read"])
    capsys.readouterr()
    with pytest.raises(SystemExit) as exc:
        cli.main(args)
    assert exc.value.code == 1
    err = capsys.readouterr().err
    assert err.strip() == message
    assert "Traceback" not in err


def test_cli_duplicate_exit_1_and_nothing_saved(data_file, capsys):
    cli.main(["add", "Read"])
    cli.main(["done", "Read"])
    with pytest.raises(SystemExit) as exc:
        cli.main(["done", "Read"])
    assert exc.value.code == 1
    assert "error: Already checked in 'Read'" in capsys.readouterr().err
    assert len(storage.load_habits()[0].checkins) == 1


# ---------- Added after the agentic code review (Task 5) ----------

def test_cli_done_with_past_date_is_saved(data_file, capsys):
    """CHK-9: a successful --date check-in through the CLI is printed and saved."""
    cli.main(["add", "Read"])
    capsys.readouterr()
    cli.main(["done", "Read", "--date", "2026-11-20"])
    assert capsys.readouterr().out.startswith("Checked in 'Read' for 2026-11-20 - streak: ")
    assert storage.load_habits()[0].checkins == ["2026-11-20"]


def test_cli_save_failure_gives_clear_error(data_file, capsys, monkeypatch):
    """CHK-2: if the file cannot be written, show an error line and exit 1, no traceback."""
    cli.main(["add", "Read"])
    capsys.readouterr()

    def broken_save(habits):
        raise PermissionError(13, "Permission denied")

    monkeypatch.setattr(storage, "save_habits", broken_save)
    with pytest.raises(SystemExit) as exc:
        cli.main(["done", "Read"])
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert captured.err.strip() == "error: could not save the data file (Permission denied)"
    assert "Traceback" not in captured.err
    assert "Checked in" not in captured.out
