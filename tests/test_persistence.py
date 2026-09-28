import json
from pathlib import Path

import pytest

from engine.persistence import JsonStore


def test_json_store_round_trip(tmp_path):
    store = JsonStore(tmp_path / "state.json")
    store.save({"value": 3})
    assert store.load({}) == {"value": 3}


def test_json_store_preserves_corrupt_json_and_returns_default(tmp_path):
    path = tmp_path / "state.json"
    path.write_text("{not-json", encoding="utf-8")

    with pytest.warns(RuntimeWarning, match="Corrupt JSON"):
        assert JsonStore(path).load({"default": True}) == {"default": True}

    corrupt_path = tmp_path / "state.json.corrupt"
    assert corrupt_path.read_text(encoding="utf-8") == "{not-json"
    assert not path.exists()



def test_json_store_handles_failure_to_preserve_corrupt_file(tmp_path, monkeypatch):
    path = tmp_path / "state.json"
    path.write_text("{not-json", encoding="utf-8")

    def fail_replace(self, target):
        raise OSError("file is locked")

    monkeypatch.setattr(Path, "replace", fail_replace)

    with pytest.warns(RuntimeWarning, match="could not preserve"):
        assert JsonStore(path).load({"default": True}) == {"default": True}

    assert path.exists()

def test_json_store_replaces_existing_file_atomically(tmp_path):
    path = tmp_path / "state.json"
    store = JsonStore(path)
    store.save({"version": 1})
    store.save({"version": 2})
    assert json.loads(path.read_text(encoding="utf-8"))["version"] == 2
    assert not path.with_name("state.json.tmp").exists()
