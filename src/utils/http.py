"""HTTP utilities and rate limiting."""

import time
from typing import Any

import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.core.config import get_settings
from src.utils.logging_config import get_logger

settings = get_settings()
logger = get_logger(__name__)


class RateLimiter:
    """Simple rate limiter for HTTP requests."""
    
    def __init__(self, max_rps: float = 2.0):
        """Initialize rate limiter.
        
        Args:
            max_rps: Maximum requests per second
        """
        self.max_rps = max_rps
        self.min_interval = 1.0 / max_rps
        self.last_request_time = 0.0
    
    def wait_if_needed(self) -> None:
        """Wait if needed to respect rate limit."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_interval:
            wait_time = self.min_interval - time_since_last
            logger.debug(f"Rate limiting: waiting {wait_time:.2f}s")
            time.sleep(wait_time)
        
        self.last_request_time = time.time()


# Global rate limiter
_rate_limiter = RateLimiter(max_rps=settings.http_max_rps)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((requests.exceptions.Timeout, requests.exceptions.ConnectionError)),
)
def get_with_retry(url: str, **kwargs: Any) -> requests.Response:
    """GET request with retry logic and rate limiting.
    
    Args:
        url: URL to request
        **kwargs: Additional arguments for requests.get
        
    Returns:
        Response object
        
    Raises:
        requests.exceptions.RequestException: On request failure
    """
    _rate_limiter.wait_if_needed()
    
    # Set default timeout
    if "timeout" not in kwargs:
        kwargs["timeout"] = settings.requests_timeout
    
    # Set default headers
    if "headers" not in kwargs:
        kwargs["headers"] = {}
    
    if "User-Agent" not in kwargs["headers"]:
        kwargs["headers"]["User-Agent"] = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    
    logger.debug(f"GET {url}")
    response = requests.get(url, **kwargs)
    
    # Check for rate limiting
    if response.status_code == 429:
        retry_after = response.headers.get("Retry-After", "60")
        logger.warning(f"Rate limited. Retry after {retry_after}s")
        time.sleep(int(retry_after))
        raise requests.exceptions.RequestException("Rate limited")
    
    response.raise_for_status()
    return response


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((requests.exceptions.Timeout, requests.exceptions.ConnectionError)),
)
def post_with_retry(url: str, **kwargs: Any) -> requests.Response:
    """POST request with retry logic and rate limiting.
    
    Args:
        url: URL to request
        **kwargs: Additional arguments for requests.post
        
    Returns:
        Response object
        
    Raises:
        requests.exceptions.RequestException: On request failure
    """
    _rate_limiter.wait_if_needed()
    
    # Set default timeout
    if "timeout" not in kwargs:
        kwargs["timeout"] = settings.requests_timeout
    
    # Set default headers
    if "headers" not in kwargs:
        kwargs["headers"] = {}
    
    if "User-Agent" not in kwargs["headers"]:
        kwargs["headers"]["User-Agent"] = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    
    logger.debug(f"POST {url}")
    response = requests.post(url, **kwargs)
    
    # Check for rate limiting
    if response.status_code == 429:
        retry_after = response.headers.get("Retry-After", "60")
        logger.warning(f"Rate limited. Retry after {retry_after}s")
        time.sleep(int(retry_after))
        raise requests.exceptions.RequestException("Rate limited")
    
    response.raise_for_status()
    return response
