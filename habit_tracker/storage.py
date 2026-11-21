import json
import os

from .models import Habit

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "habits.json")


class DataFileError(Exception):
    """The data file exists but cannot be read as a list of habits."""


# path=None means "use DATA_FILE", looked up at call time so tests can redirect it.

def load_habits(path=None):
    path = path or DATA_FILE
    if not os.path.exists(path):
        return []
    try:
        with open(path) as f:
            raw = json.load(f)
        return [Habit(**item) for item in raw]
    except (ValueError, TypeError) as e:  # bad JSON / wrong or missing keys / not a list
        raise DataFileError(f"data file {path} is damaged ({e})") from e


def save_habits(habits, path=None):
    path = path or DATA_FILE
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    try:
        with open(tmp, "w") as f:
            json.dump([h.__dict__ for h in habits], f, indent=2)
        os.replace(tmp, path)  # the old file stays complete until the new one is fully written
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def reset(path=None):
    path = path or DATA_FILE
    if os.path.exists(path):
        os.remove(path)
