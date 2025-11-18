"""SEO monitoring and analysis service"""
import aiohttp
import logging
from typing import Optional, Dict, Any, List
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re

logger = logging.getLogger(__name__)


class SEOMonitor:
    """Service for monitoring SEO metrics"""
    
    async def check_seo(self, url: str) -> Dict[str, Any]:
        """
        Perform comprehensive SEO check on a URL
        
        Args:
            url: URL to check
            
        Returns:
            Dictionary with SEO check results
        """
        result = {
            "title": None,
            "title_length": 0,
            "meta_description": None,
            "meta_description_length": 0,
            "h1_tags": [],
            "h1_count": 0,
            "h2_count": 0,
            "word_count": 0,
            "images_total": 0,
            "images_without_alt": 0,
            "internal_links": 0,
            "external_links": 0,
            "has_robots_txt": False,
            "has_sitemap": False,
            "is_mobile_friendly": False,
            "has_schema_markup": False,
            "has_og_tags": False,
            "has_twitter_tags": False,
            "seo_score": 0,
            "issues": [],
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                # Fetch the page
                async with session.get(url, timeout=30) as response:
                    html = await response.text()
                    
                    # Parse HTML
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Extract SEO elements
                    await self._extract_title(soup, result)
                    await self._extract_meta_description(soup, result)
                    await self._extract_headers(soup, result)
                    await self._analyze_content(soup, result)
                    await self._analyze_images(soup, result)
                    await self._analyze_links(soup, url, result)
                    await self._check_social_tags(soup, result)
                    await self._check_schema_markup(soup, result)
                    await self._check_mobile_friendly(soup, result)
                
                # Check for robots.txt and sitemap
                await self._check_robots_txt(url, session, result)
                await self._check_sitemap(url, session, result)
                
                # Calculate SEO score
                result["seo_score"] = self._calculate_seo_score(result)
        
        except Exception as e:
            logger.error(f"Error performing SEO check on {url}: {str(e)}")
            result["issues"].append({
                "type": "error",
                "message": f"Failed to perform SEO check: {str(e)}"
            })
        
        return result
    
    async def _extract_title(self, soup: BeautifulSoup, result: Dict[str, Any]):
        """Extract and analyze page title"""
        title_tag = soup.find('title')
        if title_tag:
            result["title"] = title_tag.get_text().strip()
            result["title_length"] = len(result["title"])
            
            if result["title_length"] == 0:
                result["issues"].append({
                    "type": "title",
                    "severity": "error",
                    "message": "Page title is empty"
                })
            elif result["title_length"] < 30:
                result["issues"].append({
                    "type": "title",
                    "severity": "warning",
                    "message": f"Page title is too short ({result['title_length']} chars, recommend 50-60)"
                })
            elif result["title_length"] > 60:
                result["issues"].append({
                    "type": "title",
                    "severity": "warning",
                    "message": f"Page title is too long ({result['title_length']} chars, recommend 50-60)"
                })
        else:
            result["issues"].append({
                "type": "title",
                "severity": "error",
                "message": "Page title is missing"
            })
    
    async def _extract_meta_description(self, soup: BeautifulSoup, result: Dict[str, Any]):
        """Extract and analyze meta description"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and 'content' in meta_desc.attrs:
            result["meta_description"] = meta_desc['content'].strip()
            result["meta_description_length"] = len(result["meta_description"])
            
            if result["meta_description_length"] == 0:
                result["issues"].append({
                    "type": "meta_description",
                    "severity": "error",
                    "message": "Meta description is empty"
                })
            elif result["meta_description_length"] < 120:
                result["issues"].append({
                    "type": "meta_description",
                    "severity": "warning",
                    "message": f"Meta description is too short ({result['meta_description_length']} chars, recommend 150-160)"
                })
            elif result["meta_description_length"] > 160:
                result["issues"].append({
                    "type": "meta_description",
                    "severity": "warning",
                    "message": f"Meta description is too long ({result['meta_description_length']} chars, recommend 150-160)"
                })
        else:
            result["issues"].append({
                "type": "meta_description",
                "severity": "error",
                "message": "Meta description is missing"
            })
    
    async def _extract_headers(self, soup: BeautifulSoup, result: Dict[str, Any]):
        """Extract and analyze header tags"""
        h1_tags = soup.find_all('h1')
        h2_tags = soup.find_all('h2')
        
        result["h1_tags"] = [h1.get_text().strip() for h1 in h1_tags]
        result["h1_count"] = len(h1_tags)
        result["h2_count"] = len(h2_tags)
        
        if result["h1_count"] == 0:
            result["issues"].append({
                "type": "headers",
                "severity": "error",
                "message": "No H1 tag found"
            })
        elif result["h1_count"] > 1:
            result["issues"].append({
                "type": "headers",
                "severity": "warning",
                "message": f"Multiple H1 tags found ({result['h1_count']}), recommend only one"
            })
    
    async def _analyze_content(self, soup: BeautifulSoup, result: Dict[str, Any]):
        """Analyze page content"""
        # Get text content
        text = soup.get_text()
        words = re.findall(r'\w+', text)
        result["word_count"] = len(words)
        
        if result["word_count"] < 300:
            result["issues"].append({
                "type": "content",
                "severity": "warning",
                "message": f"Low word count ({result['word_count']} words, recommend 300+)"
            })
    
    async def _analyze_images(self, soup: BeautifulSoup, result: Dict[str, Any]):
        """Analyze images and alt tags"""
        images = soup.find_all('img')
        result["images_total"] = len(images)
        result["images_without_alt"] = sum(1 for img in images if not img.get('alt'))
        
        if result["images_without_alt"] > 0:
            result["issues"].append({
                "type": "images",
                "severity": "warning",
                "message": f"{result['images_without_alt']} of {result['images_total']} images missing alt text"
            })
    
    async def _analyze_links(self, soup: BeautifulSoup, base_url: str, result: Dict[str, Any]):
        """Analyze internal and external links"""
        base_domain = urlparse(base_url).netloc
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link['href']
            link_domain = urlparse(href).netloc
            
            if not link_domain or link_domain == base_domain:
                result["internal_links"] += 1
            else:
                result["external_links"] += 1
    
    async def _check_social_tags(self, soup: BeautifulSoup, result: Dict[str, Any]):
        """Check for Open Graph and Twitter Card tags"""
        og_tags = soup.find_all('meta', property=re.compile(r'^og:'))
        result["has_og_tags"] = len(og_tags) > 0
        
        twitter_tags = soup.find_all('meta', attrs={'name': re.compile(r'^twitter:')})
        result["has_twitter_tags"] = len(twitter_tags) > 0
        
        if not result["has_og_tags"]:
            result["issues"].append({
                "type": "social",
                "severity": "info",
                "message": "No Open Graph tags found"
            })
        
        if not result["has_twitter_tags"]:
            result["issues"].append({
                "type": "social",
                "severity": "info",
                "message": "No Twitter Card tags found"
            })
    
    async def _check_schema_markup(self, soup: BeautifulSoup, result: Dict[str, Any]):
        """Check for schema.org structured data"""
        # Check for JSON-LD
        json_ld = soup.find_all('script', type='application/ld+json')
        
        # Check for microdata
        microdata = soup.find_all(attrs={'itemscope': True})
        
        result["has_schema_markup"] = len(json_ld) > 0 or len(microdata) > 0
        
        if not result["has_schema_markup"]:
            result["issues"].append({
                "type": "schema",
                "severity": "info",
                "message": "No schema.org markup found"
            })
    
    async def _check_mobile_friendly(self, soup: BeautifulSoup, result: Dict[str, Any]):
        """Check for mobile-friendly viewport tag"""
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        result["is_mobile_friendly"] = viewport is not None
        
        if not result["is_mobile_friendly"]:
            result["issues"].append({
                "type": "mobile",
                "severity": "warning",
                "message": "No viewport meta tag found (not mobile-friendly)"
            })
    
    async def _check_robots_txt(self, url: str, session: aiohttp.ClientSession, result: Dict[str, Any]):
        """Check for robots.txt"""
        try:
            parsed_url = urlparse(url)
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
            
            async with session.get(robots_url, timeout=10) as response:
                result["has_robots_txt"] = response.status == 200
        except:
            result["has_robots_txt"] = False
        
        if not result["has_robots_txt"]:
            result["issues"].append({
                "type": "robots",
                "severity": "info",
                "message": "No robots.txt file found"
            })
    
    async def _check_sitemap(self, url: str, session: aiohttp.ClientSession, result: Dict[str, Any]):
        """Check for XML sitemap"""
        try:
            parsed_url = urlparse(url)
            sitemap_urls = [
                f"{parsed_url.scheme}://{parsed_url.netloc}/sitemap.xml",
                f"{parsed_url.scheme}://{parsed_url.netloc}/sitemap_index.xml",
            ]
            
            for sitemap_url in sitemap_urls:
                try:
                    async with session.get(sitemap_url, timeout=10) as response:
                        if response.status == 200:
                            result["has_sitemap"] = True
                            return
                except:
                    pass
            
            result["has_sitemap"] = False
        except:
            result["has_sitemap"] = False
        
        if not result["has_sitemap"]:
            result["issues"].append({
                "type": "sitemap",
                "severity": "warning",
                "message": "No XML sitemap found"
            })
    
    def _calculate_seo_score(self, result: Dict[str, Any]) -> int:
        """Calculate overall SEO score (0-100)"""
        score = 100
        
        # Deduct points for errors
        for issue in result["issues"]:
            severity = issue.get("severity", "info")
            if severity == "error":
                score -= 10
            elif severity == "warning":
                score -= 5
            elif severity == "info":
                score -= 2
        
        # Bonus points for good practices
        if result["has_og_tags"]:
            score += 5
        if result["has_twitter_tags"]:
            score += 5
        if result["has_schema_markup"]:
            score += 5
        if result["is_mobile_friendly"]:
            score += 10
        if result["has_robots_txt"]:
            score += 2
        if result["has_sitemap"]:
            score += 5
        
        # Cap the score between 0 and 100
        return max(0, min(100, score))


# Global instance
seo_monitor = SEOMonitor()
