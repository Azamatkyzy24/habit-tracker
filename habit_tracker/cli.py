import argparse
from datetime import date

from . import storage
from .exporter import FORMATTERS, export
from .tracker import add_habit, check_in


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

    sub.add_parser("reset", help="delete all data")

    args = parser.parse_args(argv)
    habits = storage.load_habits()

    if args.command == "add":
        add_habit(habits, args.name)
        storage.save_habits(habits)
        print(f"Added habit: {args.name}")

    elif args.command == "done":
        day = date.fromisoformat(args.date) if args.date else date.today()
        check_in(habits, args.name, day)
        storage.save_habits(habits)
        print(f"Checked in '{args.name}' for {day.isoformat()}")

    elif args.command == "report":
        output = export(habits, args.format)
        if output:
            print(output)

    elif args.command == "export":
        data = export(habits, args.format)
        if args.out:
            with open(args.out, "w") as f:
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
