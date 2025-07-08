from __future__ import annotations
from typing import List

from deeptrace.core.models import Step

__all__ = ["deduplicate_avg"]

def deduplicate_avg(steps: List[Step]) -> List[Step]:
    """
    Combine steps having the same name: keep the average duration.
    start_ms is set to 0 because it is not used further.
    """
    bucket: dict[str, list[int]] = {}
    for s in steps:
        bucket.setdefault(s.name, []).append(s.duration)

    return [Step(name, 0, int(sum(d) / len(d))) for name, d in bucket.items()]
