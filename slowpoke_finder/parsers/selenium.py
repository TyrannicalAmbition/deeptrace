from typing import List
import json
from ..models import Step
from ..registry import register


@register("selenium")
class SeleniumParser:
    """
    Поддерживает Selenium-логи в HAR, массиве действий и популярных json-структурах.
    """

    def parse(self, path: str) -> List[Step]:
        """
        Возвращает список Step, найденных в логе.
        Поддержка форматов:
          - HAR (log.entries[])
          - Массив событий [{...}]
          - Корневой ключ seleniumEvents: [{...}]
          - Корневой ключ actions: [{...}]
        """
        with open(path, encoding="utf-8") as f:
            try:
                data = json.load(f)
            except Exception as e:
                raise ValueError(f"Ошибка разбора JSON: {e}")

        # HAR: log.entries[]
        if isinstance(data, dict) and "log" in data and "entries" in data["log"]:
            steps = []
            for entry in data["log"]["entries"]:
                # Network HAR: используем startedDateTime и time
                name = entry.get("request", {}).get("url") or entry.get(
                    "pageref", "step"
                )
                start = entry.get("startedDateTime")
                duration = entry.get("time", 0)
                # HAR не хранит endTime, только start+duration. Для совместимости:
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

        # Ключ seleniumEvents (как в некоторых custom json логах)
        if isinstance(data, dict) and "seleniumEvents" in data:
            return self._extract_from_list(data["seleniumEvents"])

        # Ключ actions (аналогично playwright, встречается иногда)
        if isinstance(data, dict) and "actions" in data:
            return self._extract_from_list(data["actions"])

        # Простой массив в корне
        if isinstance(data, list):
            return self._extract_from_list(data)

        # Попробовать entries в корне
        if isinstance(data, dict) and "entries" in data:
            return self._extract_from_list(data["entries"])

        raise ValueError("Не удалось найти поддерживаемый формат для selenium-логов")

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
        # Преобразует ISO 8601 дату в миллисекунды с начала эпохи (UTC)
        from datetime import datetime

        if not iso_str:
            return 0
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        epoch = datetime(1970, 1, 1, tzinfo=dt.tzinfo)
        return int((dt - epoch).total_seconds() * 1000)
