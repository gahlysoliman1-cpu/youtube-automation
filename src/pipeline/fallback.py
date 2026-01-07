from collections.abc import Callable
from typing import TypeVar

from utils.log import warn

T = TypeVar("T")


def try_chain(label: str, handlers: list[Callable[[], T]]) -> T:
    last_error: Exception | None = None
    for idx, handler in enumerate(handlers, start=1):
        try:
            return handler()
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            warn(f"{label} provider {idx} failed: {exc}")
    if last_error:
        raise last_error
    raise RuntimeError(f"{label} chain has no providers")
