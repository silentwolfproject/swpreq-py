from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class RetryPolicy:
    max_retries: int = 3
    base_delay_ms: int = 100
    max_delay_ms: int = 30000
    retry_on_status: List[int] = field(
        default_factory=lambda: [408, 429, 500, 502, 503, 504]
    )
    retry_on_error: bool = True
    exponential: bool = True
    jitter: bool = True

    @classmethod
    def none(cls) -> "RetryPolicy":
        return cls(max_retries=0)

    @classmethod
    def aggressive(cls) -> "RetryPolicy":
        return cls(
            max_retries=5,
            base_delay_ms=50,
            max_delay_ms=60000,
            retry_on_status=[408, 425, 429, 500, 502, 503, 504, 522, 524],
            retry_on_error=True,
            exponential=True,
            jitter=True,
        )

    @classmethod
    def conservative(cls) -> "RetryPolicy":
        return cls(
            max_retries=2,
            base_delay_ms=500,
            max_delay_ms=10000,
            retry_on_status=[500, 502, 503, 504],
            retry_on_error=True,
            exponential=True,
            jitter=True,
        )