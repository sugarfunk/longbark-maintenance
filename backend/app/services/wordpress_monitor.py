"""WordPress-specific monitoring service"""
import aiohttp
import logging
from typing import Optional, Dict, Any, List
from bs4 import BeautifulSoup
import re
from datetime import datetime

logger = logging.getLogger(__name__)


class WordPressMonitor:
    """Service for monitoring WordPress sites"""
    
    async def check_wordpress(self, url: str) -> Dict[str, Any]:
        """
        Check WordPress site for updates and security issues
        
        Args:
            url: WordPress site URL
            
        Returns:
            Dictionary with WordPress check results
        """
        result = {
            "wp_version": None,
            "wp_latest_version": None,
            "wp_update_available": False,
            "plugins_total": 0,
            "plugins_need_update": 0,
            "plugin_details": [],
            "themes_total": 0,
            "themes_need_update": 0,
            "theme_details": [],
            "security_issues": [],
            "security_score": 100,
            "php_version": None,
            "mysql_version": None,
        }
        
        try:
            # Try to detect WordPress version from meta tags and headers
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=30) as response:
                    html = await response.text()
                    headers = response.headers
                    
                    # Check for WordPress version
                    result["wp_version"] = await self._detect_wp_version(html, headers)
                    
                    # Check for common WordPress security issues
                    result["security_issues"] = await self._check_security_issues(url, html, session)
                    
                    # Calculate security score based on issues found
                    result["security_score"] = max(0, 100 - (len(result["security_issues"]) * 10))
                
                # Try to check via WordPress REST API
                api_data = await self._check_wp_rest_api(url, session)
                if api_data:
                    result.update(api_data)
        
        except Exception as e:
            logger.error(f"Error checking WordPress site {url}: {str(e)}")
        
        return result
    
    async def _detect_wp_version(self, html: str, headers: Dict) -> Optional[str]:
        """Detect WordPress version from HTML and headers"""
        try:
            # Check meta generator tag
            soup = BeautifulSoup(html, 'html.parser')
            generator = soup.find('meta', attrs={'name': 'generator'})
            if generator and 'content' in generator.attrs:
                content = generator['content']
                if 'WordPress' in content:
                    # Extract version number
                    version_match = re.search(r'WordPress\s+([\d.]+)', content)
                    if version_match:
                        return version_match.group(1)
            
            # Check for version in RSS feed link
            rss_link = soup.find('link', attrs={'type': 'application/rss+xml'})
            if rss_link and 'href' in rss_link.attrs:
                version_match = re.search(r'ver=([\d.]+)', rss_link['href'])
                if version_match:
                    return version_match.group(1)
            
            # Check for version in script/style tags
            for tag in soup.find_all(['script', 'link']):
                if 'src' in tag.attrs or 'href' in tag.attrs:
                    url = tag.get('src') or tag.get('href')
                    version_match = re.search(r'ver=([\d.]+)', url)
                    if version_match:
                        return version_match.group(1)
        
        except Exception as e:
            logger.error(f"Error detecting WordPress version: {str(e)}")
        
        return None
    
    async def _check_wp_rest_api(self, url: str, session: aiohttp.ClientSession) -> Optional[Dict[str, Any]]:
        """Check WordPress via REST API"""
        try:
            # Try to access WordPress REST API
            api_url = f"{url.rstrip('/')}/wp-json"
            
            async with session.get(api_url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    result = {}
                    
                    # Get WordPress version from API
                    if 'description' in data:
                        # API is available
                        # Try to get version from /wp-json endpoint
                        pass
                    
                    # Try to get namespaces (indicates available endpoints)
                    if 'namespaces' in data:
                        namespaces = data['namespaces']
                        # Check for common plugin/theme namespaces
                        pass
                    
                    return result
        
        except Exception as e:
            logger.debug(f"WordPress REST API not accessible: {str(e)}")
        
        return None
    
    async def _check_security_issues(
        self,
        url: str,
        html: str,
        session: aiohttp.ClientSession
    ) -> List[Dict[str, str]]:
        """Check for common WordPress security issues"""
        issues = []
        
        try:
            # Check for directory listing
            dirs_to_check = [
                '/wp-content/uploads/',
                '/wp-content/plugins/',
                '/wp-content/themes/',
            ]
            
            for directory in dirs_to_check:
                try:
                    check_url = f"{url.rstrip('/')}{directory}"
                    async with session.get(check_url, timeout=10) as response:
                        if response.status == 200:
                            text = await response.text()
                            if 'Index of' in text:
                                issues.append({
                                    "type": "directory_listing",
                                    "severity": "medium",
                                    "message": f"Directory listing enabled: {directory}",
                                })
                except:
                    pass
            
            # Check for readme.html
            try:
                readme_url = f"{url.rstrip('/')}/readme.html"
                async with session.get(readme_url, timeout=10) as response:
                    if response.status == 200:
                        issues.append({
                            "type": "info_disclosure",
                            "severity": "low",
                            "message": "readme.html is publicly accessible",
                        })
            except:
                pass
            
            # Check for xmlrpc.php
            try:
                xmlrpc_url = f"{url.rstrip('/')}/xmlrpc.php"
                async with session.post(xmlrpc_url, timeout=10) as response:
                    if response.status == 200 or response.status == 405:
                        issues.append({
                            "type": "xmlrpc_enabled",
                            "severity": "medium",
                            "message": "XML-RPC is enabled (potential DDoS vector)",
                        })
            except:
                pass
            
            # Check for user enumeration
            try:
                user_url = f"{url.rstrip('/')}/?author=1"
                async with session.get(user_url, timeout=10, allow_redirects=False) as response:
                    if response.status in (200, 301, 302):
                        issues.append({
                            "type": "user_enumeration",
                            "severity": "low",
                            "message": "User enumeration is possible via author parameter",
                        })
            except:
                pass
            
            # Check for WordPress version disclosure
            soup = BeautifulSoup(html, 'html.parser')
            generator = soup.find('meta', attrs={'name': 'generator'})
            if generator:
                issues.append({
                    "type": "version_disclosure",
                    "severity": "low",
                    "message": "WordPress version disclosed in meta generator tag",
                })
        
        except Exception as e:
            logger.error(f"Error checking security issues: {str(e)}")
        
        return issues


# Global instance
wordpress_monitor = WordPressMonitor()
