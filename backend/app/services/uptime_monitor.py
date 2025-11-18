"""Uptime monitoring service for checking site availability and response times"""
import aiohttp
import logging
import time
from typing import Dict, Any, Optional, List
from app.core.config import settings

logger = logging.getLogger(__name__)


class UptimeMonitor:
    """Service for monitoring website uptime and response metrics"""

    def __init__(self):
        self.timeout = settings.UPTIME_TIMEOUT

    async def check_uptime(self, url: str) -> Dict[str, Any]:
        """
        Check uptime for a given URL

        Args:
            url: The URL to check

        Returns:
            Dict containing:
                - status_code: HTTP status code
                - response_time: Response time in milliseconds
                - is_up: Boolean indicating if site is accessible
                - error_message: Error message if check failed
                - headers: Response headers as dict
                - redirect_url: Final URL if redirected
                - redirect_chain: List of redirect URLs
        """
        start_time = time.time()
        result = {
            "status_code": None,
            "response_time": None,
            "is_up": False,
            "error_message": None,
            "headers": None,
            "redirect_url": None,
            "redirect_chain": []
        }

        try:
            # Configure timeout
            timeout = aiohttp.ClientTimeout(total=self.timeout)

            # Track redirect chain
            redirect_chain = []

            async with aiohttp.ClientSession(timeout=timeout) as session:
                # Allow redirects and track them
                async with session.get(
                    url,
                    allow_redirects=True,
                    ssl=False  # Don't verify SSL here (that's for ssl_monitor)
                ) as response:
                    # Calculate response time
                    end_time = time.time()
                    response_time_ms = int((end_time - start_time) * 1000)

                    # Get redirect history
                    if response.history:
                        redirect_chain = [str(r.url) for r in response.history]
                        result["redirect_url"] = str(response.url)
                        result["redirect_chain"] = redirect_chain

                    # Get response headers (convert to dict)
                    headers_dict = dict(response.headers)

                    # Store results
                    result["status_code"] = response.status
                    result["response_time"] = response_time_ms
                    result["headers"] = headers_dict

                    # Check if site is up (2xx or 3xx status codes)
                    result["is_up"] = 200 <= response.status < 400

                    if not result["is_up"]:
                        result["error_message"] = f"HTTP {response.status}"

                    logger.info(
                        f"Uptime check for {url}: "
                        f"status={response.status}, time={response_time_ms}ms, "
                        f"redirects={len(redirect_chain)}"
                    )

        except aiohttp.ClientError as e:
            # Handle connection errors
            end_time = time.time()
            result["response_time"] = int((end_time - start_time) * 1000)
            result["is_up"] = False
            result["error_message"] = f"Connection error: {str(e)}"
            logger.error(f"Uptime check failed for {url}: {str(e)}")

        except asyncio.TimeoutError:
            end_time = time.time()
            result["response_time"] = int((end_time - start_time) * 1000)
            result["is_up"] = False
            result["error_message"] = f"Timeout after {self.timeout} seconds"
            logger.error(f"Uptime check timeout for {url}")

        except Exception as e:
            end_time = time.time()
            result["response_time"] = int((end_time - start_time) * 1000)
            result["is_up"] = False
            result["error_message"] = f"Unexpected error: {str(e)}"
            logger.error(f"Unexpected error in uptime check for {url}: {str(e)}")

        return result

    async def check_multiple_urls(self, urls: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Check uptime for multiple URLs concurrently

        Args:
            urls: List of URLs to check

        Returns:
            Dict mapping URL to check results
        """
        import asyncio

        tasks = [self.check_uptime(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Map results to URLs
        url_results = {}
        for url, result in zip(urls, results):
            if isinstance(result, Exception):
                url_results[url] = {
                    "status_code": None,
                    "response_time": None,
                    "is_up": False,
                    "error_message": f"Check failed: {str(result)}",
                    "headers": None,
                    "redirect_url": None,
                    "redirect_chain": []
                }
            else:
                url_results[url] = result

        return url_results


# Add asyncio import at module level
import asyncio

# Global instance
uptime_monitor = UptimeMonitor()
