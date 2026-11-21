# Habit Tracker

A small command-line app for tracking daily habits: add habits, check in each day,
see your streaks and weekly progress, and export your data.

## Setup

```
pip install -r requirements.txt
```

## Usage

```
python main.py add "Read 20 pages"
python main.py done "Read 20 pages"
python main.py report
python main.py export --format csv --out habits.csv
```

Data is saved in `data/habits.json`.

## Tests

```
pytest
```
