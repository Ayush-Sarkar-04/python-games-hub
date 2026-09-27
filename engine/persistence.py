"""Safe JSON persistence boundary for V2 systems."""

import json
from pathlib import Path
from typing import Any


class JsonStore:
    """Small JSON store with atomic replacement and defensive loading."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def load(self, default: Any) -> Any:
        if not self.path.exists():
            return default
        try:
            with self.path.open("r", encoding="utf-8") as file:
                value = json.load(file)
        except (OSError, json.JSONDecodeError):
            return default
        return value

    def save(self, value: Any) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self.path.with_name(self.path.name + ".tmp")
        try:
            with temp_path.open("w", encoding="utf-8") as file:
                json.dump(value, file, indent=4, sort_keys=True)
                file.write("\n")
            temp_path.replace(self.path)
        except OSError:
            if temp_path.exists():
                temp_path.unlink()
            raise
