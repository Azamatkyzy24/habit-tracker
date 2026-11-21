import csv
import io
import json

from .tracker import current_streak, weekly_completion

COLUMNS = ["name", "created", "streak", "weekly_percent"]


def _rows(habits, today):
    """One dict per habit with the values every format shows."""
    return [
        {
            "name": h.name,
            "created": h.created,
            "streak": current_streak(h, today),
            "weekly_percent": weekly_completion(h, today),
        }
        for h in habits
    ]


def to_json(rows):
    return json.dumps(rows, indent=2)


def to_csv(rows):
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=COLUMNS)
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


def to_text(rows):
    return "\n".join(
        f"{r['name']:<20} streak: {r['streak']:>3}  week: {r['weekly_percent']:>3}%" for r in rows
    )


# Strategy: each output format is one function. To add a format, add one entry here.
FORMATTERS = {
    "json": to_json,
    "csv": to_csv,
    "text": to_text,
}


def export(habits, fmt, today=None):
    if fmt not in FORMATTERS:
        raise ValueError(f"Unknown format: {fmt}")
    return FORMATTERS[fmt](_rows(habits, today))
