"""
A very small plugin registry for parsers.
"""

from __future__ import annotations
import importlib
import pkgutil
from typing import Callable, Dict, List, Protocol

from deeptrace.core.models import Step

class BaseParser(Protocol):
    """Every parser must expose parse(path: str) -> List[Step]."""
    def parse(self, path: str) -> List[Step]: ...

_parsers: Dict[str, Callable[[], BaseParser]] = {}

def register(fmt: str):
    """Decorator: @register("my_fmt") registers a parser factory."""
    def decorator(factory: Callable[[], BaseParser]):
        _parsers[fmt] = factory
        return factory
    return decorator

def get_all() -> Dict[str, Callable[[], BaseParser]]:
    return _parsers.copy()

def preload_all_parsers() -> None:
    """
    Import every module in deeptrace.core.parsers so that @register
    decorators are executed.
    """
    import deeptrace.core.parsers  # noqa: F401
    for _, name, _ in pkgutil.iter_modules(deeptrace.core.parsers.__path__):
        importlib.import_module(f"deeptrace.core.parsers.{name}")
