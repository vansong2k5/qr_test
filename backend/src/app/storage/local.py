"""Lưu file QR vào thư mục upload."""
from __future__ import annotations

from pathlib import Path
from typing import BinaryIO

from app.core.config import settings


class LocalStorage:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, relative_path: str, data: bytes | BinaryIO) -> str:
        path = self.base_dir / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(data, bytes):
            path.write_bytes(data)
        else:
            path.write_bytes(data.read())
        return relative_path

    def url_for(self, relative_path: str) -> str:
        return f"/static/{relative_path}"


storage = LocalStorage(settings.upload_dir)
