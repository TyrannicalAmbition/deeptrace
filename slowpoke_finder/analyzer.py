import heapq
from typing import List
from .models import Step
from collections import defaultdict


def top_slow_steps(steps: List[Step], top: int = 5) -> List[Step]:
    return heapq.nlargest(top, steps, key=lambda s: s.duration)


def deduplicate_avg(steps: list[Step]) -> list[Step]:
    buckets: dict[str, list[int]] = defaultdict(list)
    for s in steps:
        buckets[s.name].append(s.duration)

    unique_steps: list[Step] = []
    for name, durs in buckets.items():
        avg_dur = sum(durs) // len(durs)
        unique_steps.append(Step(name=name, start_ms=0, end_ms=avg_dur))
    return unique_steps
