import json
import os

from .models import Habit

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "habits.json")


def load_habits(path=DATA_FILE):
    if not os.path.exists(path):
        return []
    with open(path) as f:
        raw = json.load(f)
    return [Habit(**item) for item in raw]


def save_habits(habits, path=DATA_FILE):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump([h.__dict__ for h in habits], f, indent=2)


def reset(path=DATA_FILE):
    if os.path.exists(path):
        os.remove(path)
