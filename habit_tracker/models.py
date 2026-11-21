from dataclasses import dataclass, field


@dataclass
class Habit:
    name: str
    created: str  # ISO date, e.g. "2026-11-21"
    checkins: list = field(default_factory=list)  # list of ISO date strings
