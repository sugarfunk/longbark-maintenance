"""Broken links monitoring service for finding and checking broken links on pages"""
import aiohttp
import asyncio
import logging
from typing import Dict, Any, List, Set, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from app.core.config import settings

logger = logging.getLogger(__name__)


class BrokenLinksMonitor:
    """Service for finding and checking broken links on web pages"""

    def __init__(self):
        self.timeout = settings.UPTIME_TIMEOUT
        self.max_concurrent = settings.BROKEN_LINK_MAX_THREADS

    def _is_internal_link(self, base_url: str, link_url: str) -> bool:
        """
        Check if a link is internal (same domain as base URL)

        Args:
            base_url: The base URL of the page
            link_url: The link URL to check

        Returns:
            True if link is internal, False otherwise
        """
        base_domain = urlparse(base_url).netloc
        link_domain = urlparse(link_url).netloc

        # If link has no domain, it's relative (internal)
        if not link_domain:
            return True

        # Compare domains
        return base_domain == link_domain

    def _normalize_url(self, url: str) -> str:
        """
        Normalize URL by removing fragment and trailing slash

        Args:
            url: URL to normalize

        Returns:
            Normalized URL
        """
        # Remove fragment
        url = url.split('#')[0]

        # Remove trailing slash for consistency
        if url.endswith('/') and url.count('/') > 2:
            url = url.rstrip('/')

        return url

    async def _fetch_page_html(self, url: str) -> Optional[str]:
        """
        Fetch HTML content of a page

        Args:
            url: URL to fetch

        Returns:
            HTML content or None if fetch failed
        """
        try:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, ssl=False) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        logger.warning(f"Failed to fetch {url}: HTTP {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None

    def _extract_links(self, html: str, base_url: str) -> List[str]:
        """
        Extract all links from HTML

        Args:
            html: HTML content
            base_url: Base URL for resolving relative links

        Returns:
            List of absolute URLs
        """
        links = []

        try:
            soup = BeautifulSoup(html, 'html.parser')

            # Find all anchor tags
            for anchor in soup.find_all('a', href=True):
                href = anchor['href']

                # Skip empty links and anchors
                if not href or href.startswith('#') or href.startswith('javascript:') or href.startswith('mailto:') or href.startswith('tel:'):
                    continue

                # Convert relative URLs to absolute
                absolute_url = urljoin(base_url, href)

                # Normalize URL
                normalized_url = self._normalize_url(absolute_url)

                links.append(normalized_url)

        except Exception as e:
            logger.error(f"Error extracting links: {str(e)}")

        return links

    async def _check_link(self, url: str, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """
        Check if a link is broken

        Args:
            url: URL to check
            session: aiohttp session

        Returns:
            Dict with URL, status_code, and is_broken
        """
        result = {
            "url": url,
            "status_code": None,
            "is_broken": True,
            "error": None
        }

        try:
            # Use HEAD request first (faster)
            async with session.head(
                url,
                allow_redirects=True,
                ssl=False,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                result["status_code"] = response.status
                result["is_broken"] = response.status >= 400

        except aiohttp.ClientError:
            # If HEAD fails, try GET
            try:
                async with session.get(
                    url,
                    allow_redirects=True,
                    ssl=False,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    result["status_code"] = response.status
                    result["is_broken"] = response.status >= 400

            except aiohttp.ClientError as e:
                result["error"] = f"Connection error: {str(e)}"
                result["is_broken"] = True

            except asyncio.TimeoutError:
                result["error"] = "Timeout"
                result["is_broken"] = True

            except Exception as e:
                result["error"] = f"Error: {str(e)}"
                result["is_broken"] = True

        except asyncio.TimeoutError:
            result["error"] = "Timeout"
            result["is_broken"] = True

        except Exception as e:
            result["error"] = f"Error: {str(e)}"
            result["is_broken"] = True

        return result

    async def _check_links_batch(
        self,
        links: List[str],
        session: aiohttp.ClientSession,
        semaphore: asyncio.Semaphore
    ) -> List[Dict[str, Any]]:
        """
        Check multiple links concurrently with semaphore limiting

        Args:
            links: List of URLs to check
            session: aiohttp session
            semaphore: Semaphore for limiting concurrent requests

        Returns:
            List of check results
        """
        async def check_with_semaphore(url: str):
            async with semaphore:
                return await self._check_link(url, session)

        tasks = [check_with_semaphore(link) for link in links]
        return await asyncio.gather(*tasks)

    async def check_broken_links(self, url: str) -> Dict[str, Any]:
        """
        Check for broken links on a page

        Args:
            url: The URL of the page to check

        Returns:
            Dict containing:
                - total_links: Total number of links found
                - broken_links: Number of broken links
                - broken_link_details: List of broken links with details
                - internal_links: Number of internal links
                - external_links: Number of external links
        """
        result = {
            "total_links": 0,
            "broken_links": 0,
            "broken_link_details": [],
            "internal_links": 0,
            "external_links": 0,
            "error_message": None
        }

        try:
            # Fetch page HTML
            html = await self._fetch_page_html(url)
            if not html:
                result["error_message"] = "Failed to fetch page"
                return result

            # Extract all links
            all_links = self._extract_links(html, url)

            # Remove duplicates while preserving order
            unique_links = list(dict.fromkeys(all_links))

            result["total_links"] = len(unique_links)

            # Categorize links as internal/external
            internal = []
            external = []

            for link in unique_links:
                if self._is_internal_link(url, link):
                    internal.append(link)
                else:
                    external.append(link)

            result["internal_links"] = len(internal)
            result["external_links"] = len(external)

            # Check all links
            if unique_links:
                timeout = aiohttp.ClientTimeout(total=self.timeout)
                semaphore = asyncio.Semaphore(self.max_concurrent)

                async with aiohttp.ClientSession(timeout=timeout) as session:
                    check_results = await self._check_links_batch(
                        unique_links,
                        session,
                        semaphore
                    )

                    # Filter broken links
                    broken = []
                    for check_result in check_results:
                        if check_result["is_broken"]:
                            broken.append({
                                "url": check_result["url"],
                                "status_code": check_result["status_code"],
                                "error": check_result["error"],
                                "is_internal": self._is_internal_link(url, check_result["url"])
                            })

                    result["broken_links"] = len(broken)
                    result["broken_link_details"] = broken

            logger.info(
                f"Broken links check for {url}: "
                f"total={result['total_links']}, "
                f"broken={result['broken_links']}, "
                f"internal={result['internal_links']}, "
                f"external={result['external_links']}"
            )

        except Exception as e:
            result["error_message"] = f"Unexpected error: {str(e)}"
            logger.error(f"Unexpected error checking broken links for {url}: {str(e)}")

        return result

    async def check_multiple_sites(self, urls: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Check broken links for multiple URLs sequentially

        Args:
            urls: List of URLs to check

        Returns:
            Dict mapping URL to check results
        """
        url_results = {}

        for url in urls:
            try:
                result = await self.check_broken_links(url)
                url_results[url] = result
            except Exception as e:
                url_results[url] = {
                    "total_links": 0,
                    "broken_links": 0,
                    "broken_link_details": [],
                    "internal_links": 0,
                    "external_links": 0,
                    "error_message": f"Check failed: {str(e)}"
                }

        return url_results


# Global instance
broken_links_monitor = BrokenLinksMonitor()
