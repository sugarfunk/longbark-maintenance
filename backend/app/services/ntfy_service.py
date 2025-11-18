"""NTFY notification service with native support for per-alert-type topics"""
import aiohttp
import logging
from typing import Optional, Dict, Any
from app.core.config import settings
from app.models.alert import AlertType

logger = logging.getLogger(__name__)


class NTFYService:
    """Service for sending notifications via NTFY"""
    
    def __init__(self):
        self.enabled = settings.NTFY_ENABLED
        self.server_url = settings.NTFY_SERVER_URL.rstrip('/')
        self.default_topic = settings.NTFY_DEFAULT_TOPIC
        self.priority = settings.NTFY_PRIORITY
        
        # Per-alert-type topic mapping
        self.topic_map = {
            AlertType.UPTIME: settings.NTFY_TOPIC_UPTIME or self.default_topic,
            AlertType.SSL: settings.NTFY_TOPIC_SSL or self.default_topic,
            AlertType.PERFORMANCE: settings.NTFY_TOPIC_PERFORMANCE or self.default_topic,
            AlertType.SEO: settings.NTFY_TOPIC_SEO or self.default_topic,
            AlertType.WORDPRESS: settings.NTFY_TOPIC_WORDPRESS or self.default_topic,
            AlertType.BROKEN_LINKS: self.default_topic,
            AlertType.KEYWORD: settings.NTFY_TOPIC_SEO or self.default_topic,
        }
    
    async def send_notification(
        self,
        title: str,
        message: str,
        alert_type: Optional[AlertType] = None,
        topic: Optional[str] = None,
        priority: Optional[str] = None,
        tags: Optional[list] = None,
        actions: Optional[list] = None,
        click_url: Optional[str] = None,
    ) -> bool:
        """
        Send a notification to NTFY
        
        Args:
            title: Notification title
            message: Notification message
            alert_type: Type of alert (determines topic if topic not specified)
            topic: Override topic (if not provided, uses alert_type mapping)
            priority: Notification priority (min, low, default, high, urgent)
            tags: List of emoji tags (e.g., ['warning', 'alert'])
            actions: List of action buttons
            click_url: URL to open when notification is clicked
            
        Returns:
            bool: True if notification sent successfully
        """
        if not self.enabled:
            logger.info("NTFY is disabled, skipping notification")
            return False
        
        # Determine topic
        if topic:
            target_topic = topic
        elif alert_type:
            target_topic = self.topic_map.get(alert_type, self.default_topic)
        else:
            target_topic = self.default_topic
        
        # Build notification payload
        headers = {
            "Title": title,
            "Priority": priority or self.priority,
        }
        
        if tags:
            headers["Tags"] = ",".join(tags)
        
        if click_url:
            headers["Click"] = click_url
        
        if actions:
            # NTFY actions format: action=view, label=Open, url=https://...
            action_strings = []
            for action in actions:
                action_str = f"action={action.get('action', 'view')}"
                if 'label' in action:
                    action_str += f", label={action['label']}"
                if 'url' in action:
                    action_str += f", url={action['url']}"
                action_strings.append(action_str)
            headers["Actions"] = "; ".join(action_strings)
        
        # Send notification
        url = f"{self.server_url}/{target_topic}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    data=message.encode('utf-8'),
                    headers=headers
                ) as response:
                    if response.status == 200:
                        logger.info(f"NTFY notification sent to topic '{target_topic}': {title}")
                        return True
                    else:
                        logger.error(
                            f"Failed to send NTFY notification: {response.status} - {await response.text()}"
                        )
                        return False
        except Exception as e:
            logger.error(f"Error sending NTFY notification: {str(e)}")
            return False
    
    async def send_alert(
        self,
        site_name: str,
        alert_type: AlertType,
        severity: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        site_url: Optional[str] = None,
    ) -> bool:
        """
        Send an alert notification with appropriate formatting
        
        Args:
            site_name: Name of the site
            alert_type: Type of alert
            severity: Alert severity (info, warning, error, critical)
            message: Alert message
            details: Additional details
            site_url: URL of the site
            
        Returns:
            bool: True if notification sent successfully
        """
        # Map severity to emoji tags
        severity_tags = {
            "info": ["information_source"],
            "warning": ["warning"],
            "error": ["x"],
            "critical": ["rotating_light", "x"],
        }
        
        # Map alert type to emoji
        alert_type_tags = {
            AlertType.UPTIME: ["globe_with_meridians"],
            AlertType.SSL: ["lock"],
            AlertType.PERFORMANCE: ["chart_with_downwards_trend"],
            AlertType.BROKEN_LINKS: ["broken_heart"],
            AlertType.WORDPRESS: ["gear"],
            AlertType.SEO: ["mag"],
            AlertType.KEYWORD: ["mag_right"],
        }
        
        tags = severity_tags.get(severity, [])
        tags.extend(alert_type_tags.get(alert_type, []))
        
        # Build title
        title = f"{site_name} - {alert_type.value.title()} Alert"
        
        # Build message with details
        full_message = message
        if details:
            full_message += "\n\nDetails:\n"
            for key, value in details.items():
                full_message += f"• {key}: {value}\n"
        
        # Add action button if site URL provided
        actions = []
        if site_url:
            actions.append({
                "action": "view",
                "label": "View Site",
                "url": site_url
            })
        
        # Add dashboard link
        dashboard_url = f"{settings.FRONTEND_URL}/sites"
        actions.append({
            "action": "view",
            "label": "Open Dashboard",
            "url": dashboard_url
        })
        
        return await self.send_notification(
            title=title,
            message=full_message,
            alert_type=alert_type,
            tags=tags,
            actions=actions,
            click_url=site_url or dashboard_url,
        )
    
    async def test_notification(self, topic: Optional[str] = None) -> bool:
        """Send a test notification"""
        return await self.send_notification(
            title="LongBark Test Notification",
            message="This is a test notification from LongBark Hosting Manager.",
            topic=topic,
            tags=["white_check_mark"],
        )


# Global instance
ntfy_service = NTFYService()
