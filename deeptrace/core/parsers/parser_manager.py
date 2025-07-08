"""
Auto-selects the first parser that can successfully parse the given path.
"""

from __future__ import annotations
from pathlib import Path
from typing import Optional, Tuple

from deeptrace.core.models import Step
from deeptrace.core.registry import get_all, preload_all_parsers


def autodetect_parser(path: Path) -> Tuple[Optional[str], list[Step]]:
    preload_all_parsers()

    for name, factory in get_all().items():
        parser = factory()
        try:
            steps = parser.parse(str(path))
            if steps:
                return name, steps
        except ValueError:
            # Expected when parser does not support the given input.
            continue
        except Exception as exc:
            print(f"[ERROR] {name} parser failed: {exc}")

    return None, []
