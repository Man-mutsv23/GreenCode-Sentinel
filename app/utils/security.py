"""
Security utilities for GreenCode Sentinel.
Includes rate limiting to prevent API abuse.
"""

import time
from functools import wraps
from collections import defaultdict
from typing import Callable, Any


class RateLimiter:
    """Simple rate limiter to prevent API abuse."""
    
    def __init__(self, max_requests: int = 5, time_window: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum number of requests allowed
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = defaultdict(list)
    
    def is_allowed(self, identifier: str = "default") -> bool:
        """
        Check if a request is allowed.
        
        Args:
            identifier: Unique identifier for the requester
            
        Returns:
            True if request is allowed, False otherwise
        """
        current_time = time.time()
        
        # Clean old requests outside the time window
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if current_time - req_time < self.time_window
        ]
        
        # Check if under limit
        if len(self.requests[identifier]) < self.max_requests:
            self.requests[identifier].append(current_time)
            return True
        
        return False
    
    def get_wait_time(self, identifier: str = "default") -> float:
        """
        Get time to wait before next request is allowed.
        
        Args:
            identifier: Unique identifier for the requester
            
        Returns:
            Seconds to wait, or 0 if request is allowed
        """
        if not self.requests[identifier]:
            return 0.0
        
        current_time = time.time()
        oldest_request = min(self.requests[identifier])
        wait_time = self.time_window - (current_time - oldest_request)
        
        return max(0.0, wait_time)


# Global rate limiter instance
_rate_limiter = RateLimiter(max_requests=5, time_window=60)


def rate_limit(max_requests: int = 5, time_window: int = 60, identifier: str = "default"):
    """
    Decorator to rate limit function calls.
    
    Args:
        max_requests: Maximum number of requests allowed
        time_window: Time window in seconds
        identifier: Unique identifier for the rate limit
        
    Usage:
        @rate_limit(max_requests=5, time_window=60)
        def my_function():
            pass
    """
    def decorator(func: Callable) -> Callable:
        limiter = RateLimiter(max_requests, time_window)
        
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            if not limiter.is_allowed(identifier):
                wait_time = limiter.get_wait_time(identifier)
                raise RuntimeError(
                    f"Rate limit exceeded. Please wait {wait_time:.1f} seconds before trying again. "
                    f"(Limit: {max_requests} requests per {time_window} seconds)"
                )
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def check_rate_limit(identifier: str = "default") -> tuple[bool, float]:
    """
    Check if a request is allowed under the global rate limiter.
    
    Args:
        identifier: Unique identifier for the requester
        
    Returns:
        Tuple of (is_allowed, wait_time_seconds)
    """
    is_allowed = _rate_limiter.is_allowed(identifier)
    wait_time = 0.0 if is_allowed else _rate_limiter.get_wait_time(identifier)
    return is_allowed, wait_time


# Made with Bob