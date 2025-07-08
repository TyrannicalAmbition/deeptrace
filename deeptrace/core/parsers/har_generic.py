from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from deeptrace.core.models import Step
from deeptrace.core.registry import register

@register("har_generic")
class HarParser:
    """Supports standalone *.har files (directories are not accepted)."""

    def parse(self, path: str) -> List[Step]:
        p = Path(path)
        if p.is_dir():
            raise ValueError("har_generic parser supports *.har files only")

        data = json.loads(p.read_text(encoding="utf-8"))
        entries = data.get("log", {}).get("entries", [])
        steps: List[Step] = []

        for entry in entries:
            url = entry.get("request", {}).get("url", "request")
            started = entry.get("startedDateTime", "")
            duration = int(float(entry.get("time", 0)))

            try:
                t0 = datetime.fromisoformat(started.rstrip("Z")).replace(tzinfo=timezone.utc)
                start_ms = int(t0.timestamp() * 1000)
            except Exception:
                start_ms = 0
            steps.append(Step(url[:120], start_ms, start_ms + duration))
        return steps
