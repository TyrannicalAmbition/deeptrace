import json
from pathlib import Path
from typing import List
from ..models import Step
from ..registry import register


@register("playwright")
class PlaywrightParser:
    def parse(self, path: str) -> List[Step]:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        steps: List[Step] = []
        for entry in data.get("actions", []):
            steps.append(
                Step(
                    name=entry.get("name", "unknown"),
                    start_ms=int(entry["startTime"]),
                    end_ms=int(entry["endTime"]),
                )
            )
        return steps
