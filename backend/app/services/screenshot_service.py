"""Screenshot capture service using Selenium"""
import logging
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from PIL import Image
import os
from app.core.config import settings

logger = logging.getLogger(__name__)


class ScreenshotService:
    """Service for capturing website screenshots"""
    
    def __init__(self):
        self.enabled = settings.SCREENSHOT_ENABLED
        self.width = settings.SCREENSHOT_WIDTH
        self.height = settings.SCREENSHOT_HEIGHT
        self.screenshot_dir = "/app/screenshots"
        
        # Create screenshot directory if it doesn't exist
        os.makedirs(self.screenshot_dir, exist_ok=True)
    
    def capture_screenshot(self, url: str, filename: str) -> Optional[str]:
        """
        Capture a screenshot of a URL
        
        Args:
            url: URL to capture
            filename: Filename to save screenshot as (without extension)
            
        Returns:
            Path to saved screenshot or None if failed
        """
        if not self.enabled:
            logger.info("Screenshots are disabled")
            return None
        
        driver = None
        try:
            # Set up Chrome options
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument(f'--window-size={self.width},{self.height}')
            
            # Create driver
            driver = webdriver.Chrome(options=chrome_options)
            
            # Navigate to URL
            driver.get(url)
            
            # Wait for page to load
            driver.implicitly_wait(5)
            
            # Take screenshot
            screenshot_path = os.path.join(self.screenshot_dir, f"{filename}.png")
            driver.save_screenshot(screenshot_path)
            
            logger.info(f"Screenshot saved: {screenshot_path}")
            return screenshot_path
        
        except Exception as e:
            logger.error(f"Error capturing screenshot for {url}: {str(e)}")
            return None
        
        finally:
            if driver:
                driver.quit()
    
    def capture_screenshot_for_site(self, site_id: int, url: str) -> Optional[str]:
        """Capture screenshot for a site"""
        filename = f"site_{site_id}_{int(__import__('time').time())}"
        return self.capture_screenshot(url, filename)


# Global instance
screenshot_service = ScreenshotService()
