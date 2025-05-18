import json
from pathlib import Path
from typing import Iterator
from ..models import Step
from ..registry import register


@register("allure")
class AllureParser:
    """
    Парсер для allure-логов (allure-results/result*.json, container*.json и т.д.)
    """

    def parse(self, path: str) -> Iterator[Step]:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if isinstance(data, dict) and "steps" in data:
            for step in data["steps"]:
                name = step.get("name", "unknown")
                start = int(step.get("start", 0)) // 1_000_000
                stop = int(step.get("stop", step.get("start", 0))) // 1_000_000
                yield Step(name=name, start_ms=start, end_ms=stop)
        else:
            return
