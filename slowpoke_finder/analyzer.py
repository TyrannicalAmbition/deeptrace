from typing import List
from .models import Step


def top_slow_steps(steps: List[Step], top: int = 5) -> List[Step]:
    return sorted(steps, key=lambda s: s.duration, reverse=True)[:top]
