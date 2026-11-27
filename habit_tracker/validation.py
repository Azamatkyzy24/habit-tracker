"""Input validation for the check-in feature (Assignment 06).

These functions only check and clean user input. They do not touch the data file
and do not print anything. Each problem raises ValidationError with a message
that can be shown to the user as it is.
"""
import re
from datetime import date

MAX_NAME_LENGTH = 50
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class ValidationError(ValueError):
    """The user's input is not acceptable."""


def validate_name(raw):
    """Return the habit name without spaces at the ends, or raise ValidationError."""
    name = (raw or "").strip()
    if not name:
        raise ValidationError("Habit name must not be empty")
    if len(name) > MAX_NAME_LENGTH:
        raise ValidationError(f"Habit name must be at most {MAX_NAME_LENGTH} characters")
    return name


def parse_checkin_date(raw, today=None):
    """Turn the --date text into a date. No text means today. Future dates are rejected."""
    today = today or date.today()
    if raw is None:
        return today
    text = raw.strip()
    if not DATE_PATTERN.match(text):
        raise ValidationError(f"Invalid date '{raw}' - use YYYY-MM-DD")
    try:
        day = date.fromisoformat(text)
    except ValueError:
        raise ValidationError(f"Invalid date '{raw}' - use YYYY-MM-DD") from None
    if day > today:
        raise ValidationError(f"Date {day.isoformat()} is in the future")
    return day
