from backend.rate_limit import InMemoryRateLimiter, RateLimitRule


def test_in_memory_rate_limiter_allows_requests_within_limit():
    limiter = InMemoryRateLimiter()
    rule = RateLimitRule(max_requests=2, window_seconds=60)

    first_allowed, first_retry_after = limiter.check("GET:/recipes:test-user", rule)
    second_allowed, second_retry_after = limiter.check("GET:/recipes:test-user", rule)

    assert first_allowed is True
    assert first_retry_after == 0
    assert second_allowed is True
    assert second_retry_after == 0


def test_in_memory_rate_limiter_blocks_requests_after_limit():
    limiter = InMemoryRateLimiter()
    rule = RateLimitRule(max_requests=1, window_seconds=60)

    limiter.check("POST:/login:test-user", rule)
    allowed, retry_after = limiter.check("POST:/login:test-user", rule)

    assert allowed is False
    assert retry_after >= 1
