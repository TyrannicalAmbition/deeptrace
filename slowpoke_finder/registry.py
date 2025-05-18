import importlib
from typing import Protocol, Callable, Dict, List
from .models import Step


class BaseParser(Protocol):
    def parse(self, path: str) -> List[Step]: ...


_parsers: Dict[str, Callable[[], BaseParser]] = {}


def register(fmt: str):
    def decorator(factory: Callable[[], BaseParser]):
        _parsers[fmt] = factory
        return factory

    return decorator


def get(fmt: str) -> BaseParser:
    if fmt not in _parsers:
        importlib.import_module(f"slowpoke_finder.parsers.{fmt}")
    return _parsers[fmt]()
