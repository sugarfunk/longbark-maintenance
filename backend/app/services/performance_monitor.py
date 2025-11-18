"""Performance monitoring service for measuring page load times and resources"""
import logging
import time
import asyncio
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, WebDriverException
from app.core.config import settings

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Service for monitoring website performance metrics"""

    def __init__(self):
        self.timeout = settings.UPTIME_TIMEOUT
        self.performance_threshold = settings.PERFORMANCE_THRESHOLD

    def _get_chrome_options(self) -> Options:
        """Configure Chrome options for headless browsing"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-logging')
        chrome_options.add_argument('--log-level=3')
        chrome_options.add_argument(f'--window-size={settings.SCREENSHOT_WIDTH},{settings.SCREENSHOT_HEIGHT}')

        # Performance optimizations
        chrome_options.add_experimental_option('prefs', {
            'profile.managed_default_content_settings.images': 1,  # Enable images
        })

        return chrome_options

    def _calculate_performance_score(
        self,
        load_time: int,
        ttfb: int,
        page_size: int,
        num_requests: int
    ) -> int:
        """
        Calculate performance score (0-100) based on metrics

        Args:
            load_time: Total load time in milliseconds
            ttfb: Time to first byte in milliseconds
            page_size: Page size in bytes
            num_requests: Number of HTTP requests

        Returns:
            Performance score from 0-100 (100 is best)
        """
        score = 100

        # Deduct points for slow load time
        if load_time > 1000:
            score -= min(30, (load_time - 1000) // 100)

        # Deduct points for slow TTFB
        if ttfb > 200:
            score -= min(20, (ttfb - 200) // 50)

        # Deduct points for large page size (>2MB)
        if page_size > 2 * 1024 * 1024:
            score -= min(20, (page_size - 2 * 1024 * 1024) // (500 * 1024))

        # Deduct points for too many requests
        if num_requests > 50:
            score -= min(15, (num_requests - 50) // 10)

        # Ensure score is between 0 and 100
        return max(0, min(100, score))

    def _analyze_resources(self, performance_logs: List[Dict]) -> Dict[str, int]:
        """
        Analyze network requests from performance logs

        Args:
            performance_logs: Chrome performance logs

        Returns:
            Dict with resource counts and sizes
        """
        resources = {
            'num_requests': 0,
            'num_css': 0,
            'num_js': 0,
            'num_images': 0,
            'page_size': 0
        }

        for log in performance_logs:
            try:
                message = log.get('message', {})
                if isinstance(message, str):
                    import json
                    message = json.loads(message)

                msg = message.get('message', {})
                method = msg.get('method', '')

                # Track responses
                if method == 'Network.responseReceived':
                    resources['num_requests'] += 1
                    response = msg.get('params', {}).get('response', {})
                    mime_type = response.get('mimeType', '').lower()

                    if 'css' in mime_type or response.get('url', '').endswith('.css'):
                        resources['num_css'] += 1
                    elif 'javascript' in mime_type or response.get('url', '').endswith('.js'):
                        resources['num_js'] += 1
                    elif 'image' in mime_type:
                        resources['num_images'] += 1

                # Track data received
                elif method == 'Network.dataReceived':
                    data_length = msg.get('params', {}).get('dataLength', 0)
                    resources['page_size'] += data_length

            except Exception as e:
                logger.debug(f"Error parsing performance log: {str(e)}")
                continue

        return resources

    async def check_performance(self, url: str) -> Dict[str, Any]:
        """
        Check performance metrics for a given URL

        Args:
            url: The URL to check

        Returns:
            Dict containing:
                - load_time: Total load time in milliseconds
                - time_to_first_byte: TTFB in milliseconds
                - dom_load_time: DOM load time in milliseconds
                - page_size: Total page size in bytes
                - num_requests: Total number of HTTP requests
                - num_css: Number of CSS files
                - num_js: Number of JavaScript files
                - num_images: Number of images
                - performance_score: Score from 0-100
        """
        result = {
            "load_time": None,
            "time_to_first_byte": None,
            "dom_load_time": None,
            "page_size": None,
            "num_requests": None,
            "num_css": None,
            "num_js": None,
            "num_images": None,
            "performance_score": None,
            "error_message": None
        }

        driver = None

        try:
            # Setup Chrome driver
            chrome_options = self._get_chrome_options()

            # Enable performance logging
            chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()

            def create_driver():
                return webdriver.Chrome(options=chrome_options)

            driver = await loop.run_in_executor(None, create_driver)

            # Record start time
            start_time = time.time()

            # Navigate to URL
            def navigate():
                driver.set_page_load_timeout(self.timeout)
                driver.get(url)
                return time.time()

            navigation_end = await loop.run_in_executor(None, navigate)

            # Calculate initial load time
            load_time_ms = int((navigation_end - start_time) * 1000)

            # Get performance timing from browser
            def get_timing():
                return driver.execute_script("""
                    var timing = window.performance.timing;
                    var navigation = window.performance.getEntriesByType('navigation')[0];
                    return {
                        navigationStart: timing.navigationStart,
                        responseStart: timing.responseStart,
                        domContentLoaded: timing.domContentLoadedEventEnd,
                        loadComplete: timing.loadEventEnd,
                        ttfb: navigation ? navigation.responseStart : null,
                        domComplete: timing.domComplete
                    };
                """)

            timing = await loop.run_in_executor(None, get_timing)

            # Calculate metrics
            if timing.get('navigationStart') and timing.get('responseStart'):
                ttfb = timing['responseStart'] - timing['navigationStart']
                result["time_to_first_byte"] = int(ttfb) if ttfb > 0 else None

            if timing.get('navigationStart') and timing.get('domContentLoaded'):
                dom_time = timing['domContentLoaded'] - timing['navigationStart']
                result["dom_load_time"] = int(dom_time) if dom_time > 0 else None

            result["load_time"] = load_time_ms

            # Get performance logs
            def get_logs():
                return driver.get_log('performance')

            performance_logs = await loop.run_in_executor(None, get_logs)

            # Analyze resources
            resources = self._analyze_resources(performance_logs)
            result.update(resources)

            # Calculate performance score
            if all([
                result["load_time"] is not None,
                result["time_to_first_byte"] is not None,
                result["page_size"] is not None,
                result["num_requests"] is not None
            ]):
                result["performance_score"] = self._calculate_performance_score(
                    result["load_time"],
                    result["time_to_first_byte"] or 0,
                    result["page_size"],
                    result["num_requests"]
                )

            logger.info(
                f"Performance check for {url}: "
                f"load_time={result['load_time']}ms, "
                f"ttfb={result['time_to_first_byte']}ms, "
                f"score={result['performance_score']}"
            )

        except TimeoutException:
            result["error_message"] = f"Page load timeout after {self.timeout} seconds"
            logger.error(f"Performance check timeout for {url}")

        except WebDriverException as e:
            result["error_message"] = f"WebDriver error: {str(e)}"
            logger.error(f"WebDriver error checking {url}: {str(e)}")

        except Exception as e:
            result["error_message"] = f"Unexpected error: {str(e)}"
            logger.error(f"Unexpected error in performance check for {url}: {str(e)}")

        finally:
            # Clean up driver
            if driver:
                try:
                    def quit_driver():
                        driver.quit()
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, quit_driver)
                except Exception as e:
                    logger.error(f"Error closing WebDriver: {str(e)}")

        return result

    async def check_multiple_sites(self, urls: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Check performance for multiple URLs sequentially
        (Selenium doesn't work well with parallel instances)

        Args:
            urls: List of URLs to check

        Returns:
            Dict mapping URL to check results
        """
        url_results = {}

        for url in urls:
            try:
                result = await self.check_performance(url)
                url_results[url] = result
            except Exception as e:
                url_results[url] = {
                    "load_time": None,
                    "time_to_first_byte": None,
                    "dom_load_time": None,
                    "page_size": None,
                    "num_requests": None,
                    "num_css": None,
                    "num_js": None,
                    "num_images": None,
                    "performance_score": None,
                    "error_message": f"Check failed: {str(e)}"
                }

        return url_results


# Global instance
performance_monitor = PerformanceMonitor()
