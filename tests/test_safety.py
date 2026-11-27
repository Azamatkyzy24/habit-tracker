"""Tests for the Task 7 mitigations. Every test points the app at a temporary data file
through storage.DATA_FILE, so the real data/habits.json is never read, written or deleted."""
from unittest import mock

import pytest

from habit_tracker import cli, storage
from habit_tracker.models import Habit


@pytest.fixture
def data_path(tmp_path, monkeypatch):
    path = tmp_path / "data" / "habits.json"
    monkeypatch.setattr(storage, "DATA_FILE", str(path))
    return path


def write_data(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


# ---------- Mitigation 1: R1 damaged data file, R2 interrupted save ----------

@pytest.mark.parametrize("content", [
    "{broken",                                   # invalid JSON
    "",                                          # empty file (e.g. after an interrupted save)
    '[{"name": "R", "created": "2026-11-21", "checkins": [], "extra": 1}]',  # unknown key
    '[{"name": "R"}]',                           # missing keys
    '{"name": "R"}',                             # not a list
    '[{"name": "R", "created": "2026-11-21", "checkins": 5}]',     # A06 CHK-1: checkins not a list
    '[{"name": "R", "created": "2026-11-21", "checkins": null}]',  # A06 CHK-1: checkins null
    '[{"name": "R", "created": "2026-11-21", "checkins": [5]}]',   # A06 CHK-1: check-in not a string
])
def test_damaged_data_file_gives_clear_error(data_path, capsys, content):
    write_data(data_path, content)
    with pytest.raises(SystemExit) as exc:
        cli.main(["report"])
    assert exc.value.code == 1
    err = capsys.readouterr().err
    assert "is damaged" in err
    assert "reset" in err                        # tells the user how to recover
    assert data_path.read_text() == content      # the file is not changed


def test_reset_works_when_data_file_is_damaged(data_path, capsys):
    write_data(data_path, "{broken")
    cli.main(["reset"])
    assert capsys.readouterr().out == "All data deleted\n"
    assert not data_path.exists()


def test_interrupted_save_keeps_old_data(data_path):
    storage.save_habits([Habit("Read", "2026-11-21")])
    before = data_path.read_text()
    with mock.patch("json.dump", side_effect=KeyboardInterrupt), pytest.raises(KeyboardInterrupt):
        storage.save_habits([Habit("Gym", "2026-11-21")])
    assert data_path.read_text() == before                   # old data still complete
    assert [h.name for h in storage.load_habits()] == ["Read"]
    assert sorted(p.name for p in data_path.parent.iterdir()) == ["habits.json"]  # no temp file left


# ---------- Mitigation 2: R3 export --out overwrites files, R5 encoding / line endings ----------

def test_export_refuses_to_overwrite_existing_file(data_path, tmp_path, capsys):
    cli.main(["add", "Read"])
    out = tmp_path / "notes.txt"
    out.write_text("my notes")
    with pytest.raises(SystemExit) as exc:
        cli.main(["export", "--out", str(out)])
    assert exc.value.code == 1
    assert "already exists" in capsys.readouterr().err
    assert out.read_text() == "my notes"          # untouched


def test_export_force_overwrites_existing_file(data_path, tmp_path):
    cli.main(["add", "Read"])
    out = tmp_path / "old.csv"
    out.write_text("old")
    cli.main(["export", "--out", str(out), "--force"])
    assert out.read_text(encoding="utf-8").startswith("name,created,streak,weekly_percent")


def test_export_never_overwrites_the_data_file(data_path, capsys):
    cli.main(["add", "Read"])
    before = data_path.read_text()
    for extra in ([], ["--force"]):               # refused even with --force
        with pytest.raises(SystemExit) as exc:
            cli.main(["export", "--format", "csv", "--out", str(data_path), *extra])
        assert exc.value.code == 1
        assert "data file" in capsys.readouterr().err
    assert data_path.read_text() == before
    assert [h.name for h in storage.load_habits()] == ["Read"]


def test_export_file_is_utf8_with_single_crlf(data_path, tmp_path):
    # On Windows the old code wrote "\r\r\n" and crashed on Kazakh letters (cp1251), see Task 4 COR-4.
    cli.main(["add", "Әдет"])
    out = tmp_path / "out.csv"
    cli.main(["export", "--format", "csv", "--out", str(out)])
    raw = out.read_bytes()
    assert "Әдет".encode() in raw              # str.encode() is always UTF-8
    assert b"\r\r\n" not in raw
    assert raw.count(b"\r\n") == 2                # header + 1 row
