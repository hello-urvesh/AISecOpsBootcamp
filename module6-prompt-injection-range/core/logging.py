"""Append-only JSONL telemetry logger.

Each lab session gets its own file under data/logs/. One JSON object per
line so the file is greppable, awk-able, and importable into anything from
pandas to Splunk without preprocessing.
"""
from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.config import LOG_DIR


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


class JSONLLogger:
    """Thread-safe newline-delimited JSON writer."""

    def __init__(self, lab_id: str, session_id: str) -> None:
        self.lab_id = lab_id
        self.session_id = session_id
        self.path: Path = LOG_DIR / f"{lab_id}_{session_id}.jsonl"
        self._lock = threading.Lock()
        # Touch so downstream reads don't have to handle a missing file
        self.path.touch(exist_ok=True)

    def log(self, event: dict[str, Any]) -> None:
        record = {
            "ts": _utc_now_iso(),
            "lab_id": self.lab_id,
            "session_id": self.session_id,
            **event,
        }
        line = json.dumps(record, ensure_ascii=False, default=str)
        with self._lock:
            with self.path.open("a", encoding="utf-8") as f:
                f.write(line + "\n")

    def read_all(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        events: list[dict[str, Any]] = []
        with self._lock:
            with self.path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        events.append(json.loads(line))
                    except json.JSONDecodeError:
                        # Skip corrupt lines rather than crashing the UI
                        continue
        return events
