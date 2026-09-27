import json

from engine.persistence import JsonStore


def test_json_store_round_trip(tmp_path):
    store = JsonStore(tmp_path / "state.json")
    store.save({"value": 3})
    assert store.load({}) == {"value": 3}


def test_json_store_returns_default_for_corrupt_json(tmp_path):
    path = tmp_path / "state.json"
    path.write_text("{not-json", encoding="utf-8")
    assert JsonStore(path).load({"default": True}) == {"default": True}


def test_json_store_replaces_existing_file_atomically(tmp_path):
    path = tmp_path / "state.json"
    store = JsonStore(path)
    store.save({"version": 1})
    store.save({"version": 2})
    assert json.loads(path.read_text(encoding="utf-8"))["version"] == 2
    assert not path.with_name("state.json.tmp").exists()
