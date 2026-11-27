from datetime import date, timedelta

from .models import Habit


def find_habit(habits, name):
    for h in habits:
        if h.name == name:
            return h
    return None


def add_habit(habits, name, today=None):
    today = today or date.today()
    if find_habit(habits, name):
        raise ValueError(f"Habit '{name}' already exists")
    habit = Habit(name=name, created=today.isoformat())
    habits.append(habit)
    return habit


class DuplicateCheckinError(ValueError):
    """The habit already has a check-in for that day."""


def check_in(habits, name, day=None):
    """Add one check-in. A habit can have at most one check-in per day."""
    day = day or date.today()
    habit = find_habit(habits, name)
    if habit is None:
        raise ValueError(f"No habit called '{name}'")
    if day.isoformat() in habit.checkins:
        raise DuplicateCheckinError(f"Already checked in '{name}' for {day.isoformat()}")
    habit.checkins.append(day.isoformat())
    return habit


def current_streak(habit, today=None):
    """Number of consecutive days, ending today, with a check-in."""
    today = today or date.today()
    days = set(habit.checkins)
    streak = 0
    d = today
    while d.isoformat() in days:
        streak += 1
        d -= timedelta(days=1)
    return streak


def weekly_completion(habit, today=None):
    """Percent of the last 7 days (including today) with a check-in."""
    today = today or date.today()
    start = today - timedelta(days=6)
    days_in_week = set()  # a set, so a day is counted once even if old data repeats it
    for c in habit.checkins:
        if start.isoformat() <= c <= today.isoformat():
            days_in_week.add(c)
    return round(len(days_in_week) / 7 * 100)
