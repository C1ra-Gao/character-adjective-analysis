"""Small I/O helpers for the 2026 repair of the 2023 course submission."""
import hashlib
import json
from pathlib import Path


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def distinct_paths(input_path, output_path):
    if Path(input_path).resolve() == Path(output_path).resolve():
        raise ValueError("Input and output must be different files.")

