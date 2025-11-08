"""Bộ đếm rate limit dựa trên Redis với fallback in-memory."""
from __future__ import annotations

import threading
import time
from collections import defaultdict

import redis
from fastapi import HTTPException, status

from app.core.config import settings


class RateLimiter:
    def __init__(self, redis_url: str, limit_per_minute: int):
        self.redis_url = redis_url
        self.limit_per_minute = limit_per_minute
        self._client: redis.Redis | None = None
        self._fallback_counter: dict[str, tuple[int, float]] = defaultdict(lambda: (0, 0.0))
        self._lock = threading.Lock()

    @property
    def client(self) -> redis.Redis | None:
        if self._client is None:
            try:
                self._client = redis.Redis.from_url(self.redis_url, decode_responses=True)
                self._client.ping()
            except redis.RedisError:
                self._client = None
        return self._client

    def check(self, key: str) -> None:
        ttl = 60
        now = time.time()
        bucket_key = f"rate:{key}:{int(now // ttl)}"
        client = self.client
        if client is not None:
            current = client.incr(bucket_key)
            if current == 1:
                client.expire(bucket_key, ttl)
        else:
            with self._lock:
                count, bucket = self._fallback_counter[key]
                if int(bucket) != int(now // ttl):
                    count = 0
                    bucket = now // ttl
                count += 1
                self._fallback_counter[key] = (count, now // ttl)
            current = count
        if current > self.limit_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Quá nhiều lượt quét, vui lòng thử lại sau",
            )


rate_limiter = RateLimiter(settings.redis_url, settings.rate_limit_scan_per_minute)
