"""Cấu hình logging JSON đơn giản."""
import json
import logging
from logging import LogRecord


class JsonFormatter(logging.Formatter):
    def format(self, record: LogRecord) -> str:  # type: ignore[override]
        payload = {
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload)


def setup_logging() -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers = [handler]
