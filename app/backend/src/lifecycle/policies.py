from __future__ import annotations

from typing import Iterable


def is_allowed(status: str, allowed: Iterable[str]) -> bool:
    return status in set(allowed)
