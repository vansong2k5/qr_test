from __future__ import annotations

from pathlib import Path
from typing import BinaryIO

from ..config import settings


class LocalStorage:
    def __init__(self, base_path: str | None = None) -> None:
        self.base_path = Path(base_path or settings.file_storage)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save(self, *, filename: str, data: bytes) -> str:
        path = self.base_path / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return str(path)

    def open(self, *, filename: str) -> BinaryIO:
        return (self.base_path / filename).open("rb")


storage = LocalStorage()
