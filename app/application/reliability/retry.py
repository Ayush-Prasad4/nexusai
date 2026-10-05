from dataclasses import dataclass


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3
    base_delay_seconds: float = 1.0

    def can_retry(self, attempt: int) -> bool:
        return attempt < self.max_attempts

    def delay_seconds(self, attempt: int) -> float:
        return self.base_delay_seconds * (2 ** (attempt - 1))
