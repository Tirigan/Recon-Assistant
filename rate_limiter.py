"""
Rate Limiter
============
Simple thread-safe token-bucket limiter so multi-threaded scans don't
hammer a target faster than you intend. Shared by any module that
fires off concurrent requests.
"""

import threading
import time


class RateLimiter:
    """
    Token-bucket rate limiter.

    rate_per_sec: max operations allowed per second, across all threads.
    Call .acquire() before each request; it blocks just long enough to
    stay under the configured rate.
    """

    def __init__(self, rate_per_sec):
        self.rate = max(rate_per_sec, 0.01)  # guard against 0/negative
        self.lock = threading.Lock()
        self.tokens = self.rate
        self.last_check = time.monotonic()

    def acquire(self):
        with self.lock:
            now = time.monotonic()
            elapsed = now - self.last_check
            self.last_check = now

            self.tokens = min(self.rate, self.tokens + elapsed * self.rate)

            if self.tokens < 1:
                sleep_time = (1 - self.tokens) / self.rate
                time.sleep(sleep_time)
                self.tokens = 0
            else:
                self.tokens -= 1
