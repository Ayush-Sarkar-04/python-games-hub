"""Small JSON persistence helper."""

import json
import warnings
from pathlib import Path
from typing import Any


class JsonStore:
    """JSON storage with atomic writes and safe loading."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def load(self, default: Any) -> Any:
        if not self.path.exists():
            return default
        try:
            with self.path.open("r", encoding="utf-8") as file:
                value = json.load(file)
        except json.JSONDecodeError:
            corrupt_path = self._preserve_corrupt_file()
            if corrupt_path is None:
                warnings.warn(
                    f"Corrupt JSON in {self.path}; could not preserve the file and reset to defaults.",
                    RuntimeWarning,
                    stacklevel=2,
                )
            else:
                warnings.warn(
                    f"Corrupt JSON in {self.path}; preserved as {corrupt_path.name} and reset to defaults.",
                    RuntimeWarning,
                    stacklevel=2,
                )
            return default
        except OSError:
            return default
        return value

    def _preserve_corrupt_file(self) -> Path | None:
        """Move a corrupt JSON file aside without overwriting older recovery files."""
        candidate = self.path.with_name(self.path.name + ".corrupt")
        counter = 1
        while candidate.exists():
            candidate = self.path.with_name(f"{self.path.name}.corrupt.{counter}")
            counter += 1
        try:
            self.path.replace(candidate)
        except OSError:
            return None
        return candidate

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
