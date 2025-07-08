from __future__ import annotations
from dataclasses import dataclass

@dataclass(slots=True)
class Step:
    """
    Unified model that represents a single log step.

    All parsers must return List[Step].
    """
    name: str
    start_ms: int
    end_ms: int

    @property
    def duration(self) -> int:
        """Step duration in milliseconds (non-negative)."""
        return max(self.end_ms - self.start_ms, 0)
