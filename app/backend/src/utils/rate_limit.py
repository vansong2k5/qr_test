from __future__ import annotations

import asyncio
import logging
from typing import Optional

from redis.asyncio import Redis

from ..config import settings

_logger = logging.getLogger(__name__)
_redis_client: Optional[Redis] = None
_lock = asyncio.Lock()


async def _get_client() -> Optional[Redis]:
    global _redis_client
    if _redis_client is not None:
        return _redis_client

    async with _lock:
        if _redis_client is not None:
            return _redis_client
        try:
            _redis_client = Redis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
        except Exception as exc:  # pragma: no cover - phòng thủ khi thiếu Redis
            _logger.warning("Không thể kết nối Redis: %s", exc)
            _redis_client = None
    return _redis_client


async def is_rate_limited(*, identifier: str, limit: int, window: int) -> bool:
    """Kiểm tra số lượt gọi theo khoá định danh và giới hạn trong khoảng thời gian nhất định."""

    client = await _get_client()
    if client is None:
        return False

    key = f"ratelimit:{identifier}"
    try:
        async with client.pipeline(transaction=True) as pipe:
            pipe.incr(key)
            pipe.expire(key, window, nx=True)
            hits, _ = await pipe.execute()
    except Exception as exc:  # pragma: no cover - không muốn chặn luồng quét khi Redis lỗi
        _logger.warning("Không thể cập nhật rate-limit: %s", exc)
        return False

    return int(hits) > limit
