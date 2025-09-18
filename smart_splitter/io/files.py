from __future__ import annotations
import csv
import json
from pathlib import Path
from typing import Any, Dict, List
import yaml


def ensure_dir(path: Path | str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def read_yaml(path: Path) -> Dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")


def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    if not rows:
        Path(path).write_text("", encoding="utf-8")
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["index", "title", "start", "end"])
        w.writeheader()
        for i, r in enumerate(rows, start=1):
            w.writerow({
                "index": i,
                "title": r.get("title", f"Track {i}"),
                "start": r.get("start", ""),
                "end": r.get("end", ""),
            })