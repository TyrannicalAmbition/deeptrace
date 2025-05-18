import json
from pathlib import Path
from typing import List
from ..models import Step
from ..registry import register


@register("playwright")
class PlaywrightParser:
    def parse(self, path: str) -> List[Step]:
        data = json.loads(Path(path).read_text(encoding="utf-8"))

        action_keys = ("actions", "events", "steps", "playwrightActions")
        actions = []
        if isinstance(data, dict):
            for key in action_keys:
                if key in data and isinstance(data[key], list):
                    actions = data[key]
                    break
            else:
                if isinstance(data, list):
                    actions = data
        elif isinstance(data, list):
            actions = data
        else:
            raise ValueError(
                "The Playwright log does not contain a suitable list of actions."
            )

        steps: List[Step] = []
        for entry in actions:
            try:
                start = int(entry.get("startTime", 0))
                end = int(entry.get("endTime", start))
                name = entry.get("name") or entry.get("event") or "unknown"
                steps.append(Step(name=name, start_ms=start, end_ms=end))
            except Exception:
                continue
        return steps
