from typing import List
import json
from ..models import Step
from ..registry import register


@register("selenium")
class SeleniumParser:
    """
    Supports Selenium logs in HAR, action array and popular json structures.
    """

    def parse(self, path: str) -> List[Step]:
        """
        Returns a list of Steps found in the log.
        Supported formats:
            - HAR (log.entries[])
            - Array of events [{...}]
            - Root key seleniumEvents: [{...}]
            - Root key actions: [{...}]
        """
        with open(path, encoding="utf-8") as f:
            try:
                data = json.load(f)
            except Exception as e:
                raise ValueError(f"JSON parsing error: {e}")

        if isinstance(data, dict) and "log" in data and "entries" in data["log"]:
            steps = []
            for entry in data["log"]["entries"]:
                name = entry.get("request", {}).get("url") or entry.get(
                    "pageref", "step"
                )
                start = entry.get("startedDateTime")
                duration = entry.get("time", 0)
                try:
                    start_ms = self._iso_to_ms(start)
                except Exception:
                    start_ms = 0
                steps.append(
                    Step(
                        name=name,
                        start_ms=start_ms,
                        end_ms=start_ms + int(duration),
                    )
                )
            return steps

        if isinstance(data, dict) and "seleniumEvents" in data:
            return self._extract_from_list(data["seleniumEvents"])

        if isinstance(data, dict) and "actions" in data:
            return self._extract_from_list(data["actions"])

        if isinstance(data, list):
            return self._extract_from_list(data)

        if isinstance(data, dict) and "entries" in data:
            return self._extract_from_list(data["entries"])

        raise ValueError("Could not find supported format for selenium logs")

    def _extract_from_list(self, lst):
        steps = []
        for entry in lst:
            name = (
                entry.get("name")
                or entry.get("eventName")
                or entry.get("message", "step")
            )
            start = entry.get("startTime") or entry.get("timestamp") or 0
            end = entry.get("endTime") or (start + entry.get("duration", 0)) or 0
            try:
                start_ms = int(float(start))
                end_ms = int(float(end))
            except Exception:
                start_ms = end_ms = 0
            steps.append(Step(name=name, start_ms=start_ms, end_ms=end_ms))
        return steps

    def _iso_to_ms(self, iso_str):
        from datetime import datetime

        if not iso_str:
            return 0
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        epoch = datetime(1970, 1, 1, tzinfo=dt.tzinfo)
        return int((dt - epoch).total_seconds() * 1000)
