from __future__ import annotations
import json
from pathlib import Path
from typing import List

from deeptrace.core.models import Step
from deeptrace.core.registry import register


@register("allure")
class AllureParser:
    """
    Accepts a single result*.json OR an allure-results directory and
    recursively collects all `steps` / `children`.
    """

    def parse(self, path: str) -> List[Step]:
        p = Path(path)
        files = [p] if p.is_file() else list(p.glob("*.json"))
        steps: List[Step] = []

        for file in files:
            try:
                data = json.loads(file.read_text(encoding="utf-8"))
                steps.extend(self._collect(data))
            except Exception:
                # broken JSON – ignore
                continue
        return steps

    # ------------------------------------------------------------------ #
    def _collect(self, node) -> List[Step]:
        out: List[Step] = []
        if not isinstance(node, list):
            node = node.get("steps") or node.get("children") or []
        for step in node:
            name = step.get("name", "unknown")
            start = int(step.get("start", 0))
            stop = int(step.get("stop", start))
            out.append(Step(name, start, stop))
            if step.get("steps") or step.get("children"):
                out.extend(self._collect(step.get("steps") or step.get("children")))
        return out
