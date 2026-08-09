"""Caching and rate limiting utilities with Redis-first strategy."""

from __future__ import annotations

import asyncio
import hashlib
import json
import time
from collections import defaultdict, deque
from typing import Any

from app.config import settings

try:
    import redis.asyncio as redis
except Exception:  # pragma: no cover - fallback path when redis package missing
    redis = None


class CacheAndRateLimiter:
    def __init__(self):
        self._redis = None
        if settings.redis_url and redis is not None:
            self._redis = redis.from_url(settings.redis_url, decode_responses=True)
        self._memory_cache: dict[str, tuple[float, Any]] = {}
        self._rate_windows: dict[str, deque[float]] = defaultdict(deque)
        self._lock = asyncio.Lock()

    @staticmethod
    def _cache_key(prefix: str, payload: str) -> str:
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        return f"{prefix}:{digest}"

    async def get_cached(self, prefix: str, payload: str) -> Any | None:
        key = self._cache_key(prefix, payload)
        if self._redis is not None:
            value = await self._redis.get(key)
            if value:
                return json.loads(value)
            return None

        record = self._memory_cache.get(key)
        if not record:
            return None
        expires_at, value = record
        if expires_at < time.time():
            self._memory_cache.pop(key, None)
            return None
        return value

    async def set_cached(self, prefix: str, payload: str, value: Any, ttl_seconds: int = 180) -> None:
        key = self._cache_key(prefix, payload)
        if self._redis is not None:
            await self._redis.setex(key, ttl_seconds, json.dumps(value))
            return
        self._memory_cache[key] = (time.time() + ttl_seconds, value)

    async def check_rate_limit(self, user_key: str) -> tuple[bool, int]:
        max_requests = settings.rate_limit_requests
        window = settings.rate_limit_window_seconds
        now = time.time()

        if self._redis is not None:
            key = f"ratelimit:{user_key}"
            pipeline = self._redis.pipeline()
            pipeline.zremrangebyscore(key, 0, now - window)
            pipeline.zadd(key, {str(now): now})
            pipeline.zcard(key)
            pipeline.expire(key, window)
            _, _, count, _ = await pipeline.execute()
            remaining = max(0, max_requests - int(count))
            return int(count) <= max_requests, remaining

        async with self._lock:
            bucket = self._rate_windows[user_key]
            while bucket and bucket[0] <= now - window:
                bucket.popleft()
            bucket.append(now)
            count = len(bucket)
        remaining = max(0, max_requests - count)
        return count <= max_requests, remaining


_service: CacheAndRateLimiter | None = None


def get_cache_rate_limiter() -> CacheAndRateLimiter:
    global _service
    if _service is None:
        _service = CacheAndRateLimiter()
    return _service
