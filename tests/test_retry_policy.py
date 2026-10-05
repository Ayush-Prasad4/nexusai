from app.application.reliability.retry import RetryPolicy


def test_retry_policy_allows_attempts_within_limit() -> None:
    policy = RetryPolicy(
        max_attempts=3,
        base_delay_seconds=1.0,
    )

    assert policy.can_retry(1) is True
    assert policy.can_retry(2) is True
    assert policy.can_retry(3) is False


def test_retry_policy_uses_exponential_backoff() -> None:
    policy = RetryPolicy(
        max_attempts=4,
        base_delay_seconds=1.0,
    )

    assert policy.delay_seconds(1) == 1.0
    assert policy.delay_seconds(2) == 2.0
    assert policy.delay_seconds(3) == 4.0
    assert policy.delay_seconds(4) == 8.0
