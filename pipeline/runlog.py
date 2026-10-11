import json
from datetime import datetime
from pathlib import Path

RUNS_DIR = Path("runs")


def save_run(record: dict) -> str:
    """Save one run's record as JSON in runs/. Returns the file path."""
    RUNS_DIR.mkdir(exist_ok=True)
    path = RUNS_DIR / f"{datetime.now():%Y-%m-%d-%H%M%S}.json"
    path.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
    return str(path)