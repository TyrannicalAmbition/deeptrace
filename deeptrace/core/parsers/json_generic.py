from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List

from deeptrace.core.models import Step
from deeptrace.core.registry import register

@register("json_generic")
class JSONGenericParser:
    """
    Universal JSON parser:
      • {"actions": [...]}
      • {"events": [...]}
      • {"steps": [...]}
      • {"seleniumEvents": [...]}
      • {"entries": [...]}
      • or a list at the root.
    Directories are not supported (handled by Allure).
    """

    KEYS = ("actions", "events", "steps", "seleniumEvents", "entries")

    def parse(self, path: str) -> List[Step]:
        p = Path(path)
        if p.is_dir():
            raise ValueError("json_generic parser supports **single** *.json files only")

        data = json.loads(p.read_text(encoding="utf-8"))
        events = self._events(data)
        return self._to_steps(events)

    # -------------------------------------------------------------- #
    def _events(self, data: Any) -> List[Dict[str, Any]]:
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            for k in self.KEYS:
                if isinstance(data.get(k), list):
                    return data[k]
        raise ValueError("json_generic: no event list found")

    @staticmethod
    def _to_steps(events: List[Dict[str, Any]]) -> List[Step]:
        out: List[Step] = []
        for ev in events:
            name = ev.get("name") or ev.get("event") or ev.get("eventName") or ev.get("message") or "step"
            start = int(float(ev.get("startTime") or ev.get("timestamp") or 0))
            if "endTime" in ev:
                end = int(float(ev["endTime"]))
            elif "duration" in ev:
                end = start + int(float(ev["duration"]))
            else:
                end = start
            out.append(Step(name, start, end))
        return out
