import json
from datetime import date

import pytest

from habit_tracker import storage
from habit_tracker.exporter import export
from habit_tracker.tracker import add_habit, check_in, current_streak, weekly_completion

TODAY = date(2026, 11, 21)


def test_add_habit():
    habits = []
    add_habit(habits, "Read", TODAY)
    assert len(habits) == 1
    assert habits[0].name == "Read"
    assert habits[0].created == "2026-11-21"


def test_add_duplicate_habit_raises():
    habits = []
    add_habit(habits, "Read", TODAY)
    with pytest.raises(ValueError):
        add_habit(habits, "Read", TODAY)


def test_streak_three_days():
    habits = []
    add_habit(habits, "Gym", TODAY)
    for d in [19, 20, 21]:
        check_in(habits, "Gym", date(2026, 11, d))
    assert current_streak(habits[0], TODAY) == 3


def test_weekly_completion():
    habits = []
    add_habit(habits, "Korean", TODAY)
    for d in [17, 19, 21]:
        check_in(habits, "Korean", date(2026, 11, d))
    assert weekly_completion(habits[0], TODAY) == 43  # 3 of 7 days


def test_export_json():
    habits = []
    add_habit(habits, "Read", TODAY)
    check_in(habits, "Read", TODAY)
    data = json.loads(export(habits, "json", TODAY))
    assert data[0]["name"] == "Read"
    assert data[0]["streak"] == 1


def test_save_and_load(tmp_path):
    path = tmp_path / "habits.json"
    habits = []
    add_habit(habits, "Read", TODAY)
    storage.save_habits(habits, str(path))
    loaded = storage.load_habits(str(path))
    assert loaded[0].name == "Read"
