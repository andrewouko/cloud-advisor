"""Redis caching and rate limiting service.

Provides response caching to reduce Anthropic API calls and
per-session rate limiting to protect the API budget.
"""

import hashlib
import json
import logging
from dataclasses import dataclass

import redis.asyncio as redis

from app.config import Settings

logger = logging.getLogger(__name__)

# Cache TTL: 1 hour
CACHE_TTL_SECONDS = 3600

# Rate limit: requests per window
RATE_LIMIT_MAX_REQUESTS = 20
RATE_LIMIT_WINDOW_SECONDS = 60


@dataclass
class CachedResponse:
    """A cached Claude response retrieved from Redis."""

    content: str
    model: str
    input_tokens: int
    output_tokens: int


class CacheService:
    """Redis-backed caching and rate limiting for Claude responses.

    Features:
    - Response caching by normalised question hash
    - Per-IP sliding window rate limiting
    """

    def __init__(self, settings: Settings) -> None:
        self._redis: redis.Redis | None = None
        self._url = settings.redis_url

    async def connect(self) -> None:
        """Establish Redis connection."""
        try:
            self._redis = redis.from_url(self._url, decode_responses=True)
            await self._redis.ping()
            logger.info("Redis connected at %s", self._url)
        except Exception as exc:
            logger.warning("Redis connection failed, caching disabled: %s", exc)
            self._redis = None

    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self._redis:
            await self._redis.aclose()
            logger.info("Redis disconnected")

    @property
    def is_connected(self) -> bool:
        return self._redis is not None

    @staticmethod
    def _question_key(question: str) -> str:
        """Generate a cache key from a normalised question."""
        normalised = question.strip().lower()
        question_hash = hashlib.sha256(normalised.encode()).hexdigest()[:16]
        return f"cache:response:{question_hash}"

    @staticmethod
    def _rate_limit_key(client_ip: str) -> str:
        """Generate a rate limit key for a client IP."""
        return f"ratelimit:{client_ip}"

    async def get_cached_response(self, question: str) -> CachedResponse | None:
        """Look up a cached response for the given question.

        Args:
            question: The user's question.

        Returns:
            CachedResponse if found in cache, None otherwise.
        """
        if not self._redis:
            return None

        try:
            key = self._question_key(question)
            data = await self._redis.get(key)
            if data:
                parsed = json.loads(data)
                logger.info("Cache HIT for question '%.60s...'", question)
                return CachedResponse(**parsed)
        except Exception as exc:
            logger.warning("Cache read error: %s", exc)

        return None

    async def cache_response(
        self,
        question: str,
        content: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> None:
        """Store a Claude response in cache.

        Args:
            question: The user's question (used as cache key).
            content: The response text.
            model: The model ID.
            input_tokens: Input token count.
            output_tokens: Output token count.
        """
        if not self._redis:
            return

        try:
            key = self._question_key(question)
            payload = json.dumps({
                "content": content,
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
            })
            await self._redis.setex(key, CACHE_TTL_SECONDS, payload)
            logger.debug("Cached response for question '%.60s...'", question)
        except Exception as exc:
            logger.warning("Cache write error: %s", exc)

    async def check_rate_limit(self, client_ip: str) -> tuple[bool, int]:
        """Check if a client IP has exceeded the rate limit.

        Uses a sliding window counter in Redis.

        Args:
            client_ip: The client's IP address.

        Returns:
            Tuple of (allowed: bool, remaining: int requests left).
        """
        if not self._redis:
            return True, RATE_LIMIT_MAX_REQUESTS

        try:
            key = self._rate_limit_key(client_ip)
            current = await self._redis.incr(key)

            if current == 1:
                await self._redis.expire(key, RATE_LIMIT_WINDOW_SECONDS)

            remaining = max(0, RATE_LIMIT_MAX_REQUESTS - current)
            allowed = current <= RATE_LIMIT_MAX_REQUESTS

            if not allowed:
                logger.warning("Rate limit exceeded for IP %s", client_ip)

            return allowed, remaining
        except Exception as exc:
            logger.warning("Rate limit check error: %s", exc)
            return True, RATE_LIMIT_MAX_REQUESTS