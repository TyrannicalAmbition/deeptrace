from dataclasses import dataclass


@dataclass
class Step:
    name: str
    start_ms: int
    end_ms: int

    @property
    def duration(self) -> int:
        return self.end_ms - self.start_ms
