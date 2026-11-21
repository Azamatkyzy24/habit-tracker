import csv
import io
import json

from .tracker import current_streak, weekly_completion


def export(habits, fmt, today=None):
    if fmt == "json":
        rows = []
        for h in habits:
            rows.append({
                "name": h.name,
                "created": h.created,
                "streak": current_streak(h, today),
                "weekly_percent": weekly_completion(h, today),
            })
        return json.dumps(rows, indent=2)
    elif fmt == "csv":
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["name", "created", "streak", "weekly_percent"])
        for h in habits:
            writer.writerow([h.name, h.created, current_streak(h, today), weekly_completion(h, today)])
        return buf.getvalue()
    elif fmt == "text":
        lines = []
        for h in habits:
            lines.append(f"{h.name:<20} streak: {current_streak(h, today):>3}  week: {weekly_completion(h, today):>3}%")
        return "\n".join(lines)
    else:
        raise ValueError(f"Unknown format: {fmt}")
