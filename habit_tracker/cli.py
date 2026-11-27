import argparse
import os
from datetime import date

from . import storage
from .exporter import FORMATTERS, export, format_checkin
from .tracker import add_habit, check_in
from .validation import parse_checkin_date, validate_name


def _is_data_file(path):
    """True if path points to the habit data file (also via another spelling or a link)."""
    data = storage.DATA_FILE
    if os.path.exists(path) and os.path.exists(data):
        return os.path.samefile(path, data)
    return os.path.normcase(os.path.abspath(path)) == os.path.normcase(os.path.abspath(data))


def main(argv=None):
    parser = argparse.ArgumentParser(prog="habits", description="Simple habit tracker")
    sub = parser.add_subparsers(dest="command")

    p_add = sub.add_parser("add", help="add a new habit")
    p_add.add_argument("name")

    p_done = sub.add_parser("done", help="mark a habit as done")
    p_done.add_argument("name")
    p_done.add_argument("--date", help="YYYY-MM-DD (default: today)")

    p_report = sub.add_parser("report", help="show streaks and weekly progress")
    p_report.add_argument("--format", default="text", choices=FORMATTERS)

    p_export = sub.add_parser("export", help="export habits to csv/json/text")
    p_export.add_argument("--format", default="csv", choices=FORMATTERS)
    p_export.add_argument("--out", help="output file (default: print)")
    p_export.add_argument("--force", action="store_true", help="overwrite --out if it already exists")

    sub.add_parser("reset", help="delete all data")

    args = parser.parse_args(argv)
    habits = []
    if args.command not in (None, "reset"):  # reset must still work when the file is damaged
        try:
            habits = storage.load_habits()
        except storage.DataFileError as e:
            parser.exit(1, f"error: {e}\nFix the file by hand, or run 'reset' to delete it and start over.\n")

    if args.command == "add":
        add_habit(habits, args.name)
        storage.save_habits(habits)
        print(f"Added habit: {args.name}")

    elif args.command == "done":
        today = date.today()
        try:
            name = validate_name(args.name)               # 1. validation
            day = parse_checkin_date(args.date, today)
            habit = check_in(habits, name, day)           # 2. core logic
        except ValueError as e:
            parser.exit(1, f"error: {e}\n")              # 3. output (error)
        try:
            storage.save_habits(habits)
        except OSError as e:                              # A06 review finding CHK-2
            parser.exit(1, f"error: could not save the data file ({e.strerror or e})\n")
        print(format_checkin(habit, day, today))          # 3. output (success)

    elif args.command == "report":
        output = export(habits, args.format)
        if output:
            print(output)

    elif args.command == "export":
        data = export(habits, args.format)
        if args.out:
            if _is_data_file(args.out):
                parser.exit(1, "error: --out must not be the habit data file\n")
            if os.path.exists(args.out) and not args.force:
                parser.exit(1, f"error: {args.out} already exists (use --force to overwrite)\n")
            with open(args.out, "w", encoding="utf-8", newline="") as f:
                f.write(data)
            print(f"Exported to {args.out}")
        else:
            print(data)

    elif args.command == "reset":
        storage.reset()
        print("All data deleted")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
