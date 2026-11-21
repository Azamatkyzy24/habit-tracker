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
