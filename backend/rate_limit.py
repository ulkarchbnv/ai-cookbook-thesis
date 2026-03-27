from collections import defaultdict, deque
from dataclasses import dataclass
from threading import Lock
from time import time

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


@dataclass(frozen=True)
class RateLimitRule:
    max_requests: int
    window_seconds: int


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._requests: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def check(self, key: str, rule: RateLimitRule) -> tuple[bool, int]:
        now = time()
        window_start = now - rule.window_seconds

        with self._lock:
            bucket = self._requests[key]

            while bucket and bucket[0] <= window_start:
                bucket.popleft()

            if len(bucket) >= rule.max_requests:
                retry_after = max(1, int(bucket[0] + rule.window_seconds - now))
                return False, retry_after

            bucket.append(now)
            return True, 0


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, default_rule: RateLimitRule, route_rules: dict[str, RateLimitRule]) -> None:
        super().__init__(app)
        self.default_rule = default_rule
        self.route_rules = route_rules
        self.rate_limiter = InMemoryRateLimiter()

    async def dispatch(self, request: Request, call_next):
        rule = self._resolve_rule(request)
        client_identifier = self._get_client_identifier(request)
        key = f"{request.method}:{request.url.path}:{client_identifier}"
        allowed, retry_after = self.rate_limiter.check(key, rule)

        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded. Please try again later.",
                },
                headers={"Retry-After": str(retry_after)},
            )

        return await call_next(request)

    def _resolve_rule(self, request: Request) -> RateLimitRule:
        return self.route_rules.get(request.url.path, self.default_rule)

    @staticmethod
    def _get_client_identifier(request: Request) -> str:
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        if request.client and request.client.host:
            return request.client.host

        return "unknown"
