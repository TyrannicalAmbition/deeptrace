import json
from pathlib import Path
from typing import Iterator
from ..models import Step
from ..registry import register


@register("allure")
class AllureParser:
    """
    Parser for allure logs (allure-results/result*.json, container*.json, etc.)
    """

    def parse(self, path: str) -> Iterator[Step]:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        yield from self._parse_steps(data.get("steps", []))

    def _parse_steps(self, steps):
        for step in steps:
            name = step.get("name", "unknown")
            start = int(step.get("start", 0))
            stop = int(step.get("stop", step.get("start", 0)))
            yield Step(name=name, start_ms=start, end_ms=stop)
            if "steps" in step and step["steps"]:
                yield from self._parse_steps(step["steps"])
