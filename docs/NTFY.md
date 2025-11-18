# NTFY Integration Guide

LongBark has native NTFY integration for real-time notifications about site issues and alerts.

## What is NTFY?

NTFY (pronounced "notify") is a simple HTTP-based pub-sub notification service. You can send notifications to your phone, desktop, or other devices without requiring app-specific tokens or accounts.

Learn more: https://ntfy.sh

## Configuration

### Basic Setup

Edit your `.env` file:

```bash
# Enable NTFY notifications
NTFY_ENABLED=True

# NTFY server URL (use ntfy.sh or your self-hosted instance)
NTFY_SERVER_URL=https://ntfy.sh

# Default topic for all notifications
NTFY_DEFAULT_TOPIC=longbark-alerts

# Notification priority (min, low, default, high, urgent)
NTFY_PRIORITY=default
```

### Per-Alert-Type Topics

You can configure different topics for different types of alerts:

```bash
# Uptime alerts (site down/up)
NTFY_TOPIC_UPTIME=longbark-uptime

# SSL certificate alerts
NTFY_TOPIC_SSL=longbark-ssl

# Performance alerts (slow loading)
NTFY_TOPIC_PERFORMANCE=longbark-performance

# SEO alerts
NTFY_TOPIC_SEO=longbark-seo

# WordPress updates and security
NTFY_TOPIC_WORDPRESS=longbark-wordpress
```

If a specific topic is not configured, alerts will use `NTFY_DEFAULT_TOPIC`.

## Using Public NTFY Server (ntfy.sh)

The easiest way to get started is using the public ntfy.sh server:

### 1. Choose Unique Topics

Pick unique topic names to avoid conflicts. Good pattern:

```bash
NTFY_DEFAULT_TOPIC=longbark-yourcompany-alerts
NTFY_TOPIC_UPTIME=longbark-yourcompany-uptime
NTFY_TOPIC_SSL=longbark-yourcompany-ssl
```

### 2. Subscribe to Topics

#### On Your Phone

1. Install NTFY app:
   - Android: [Google Play](https://play.google.com/store/apps/details?id=io.heckel.ntfy)
   - iOS: [App Store](https://apps.apple.com/us/app/ntfy/id1625396347)

2. Open the app and tap "+"

3. Enter your topic name: `longbark-yourcompany-alerts`

4. Repeat for each topic you want to monitor

#### On Your Desktop

1. Visit https://ntfy.sh
2. Enter your topic name in the subscription box
3. Bookmark the page

#### Via CLI

```bash
# Subscribe to topic
ntfy subscribe longbark-yourcompany-alerts

# Or use curl
curl -s ntfy.sh/longbark-yourcompany-alerts/json
```

### 3. Test Notifications

Test your NTFY setup:

```bash
docker-compose exec backend python -c "
from app.services.ntfy_service import ntfy_service
import asyncio
asyncio.run(ntfy_service.test_notification('longbark-yourcompany-alerts'))
"
```

You should receive a test notification on all subscribed devices.

## Self-Hosting NTFY

For production use, consider self-hosting NTFY on your infrastructure.

### Using Docker

```bash
# Run NTFY server
docker run -d \
  --name ntfy \
  -p 8080:80 \
  -v /var/cache/ntfy:/var/cache/ntfy \
  binwiederhier/ntfy \
  serve
```

### With Tailscale

If using Tailscale networking:

```bash
# Update your .env file
NTFY_SERVER_URL=http://<ntfy-tailscale-hostname>:8080
```

### NTFY Server Configuration

Create `/etc/ntfy/server.yml`:

```yaml
base-url: https://ntfy.yourdomain.com
listen-http: :80

# Optional: Add authentication
auth-file: /var/lib/ntfy/user.db
auth-default-access: deny-all

# Optional: Rate limiting
visitor-request-limit-burst: 60
visitor-request-limit-replenish: 5s
```

### Secure with HTTPS

Use reverse proxy (Nginx/Caddy) with Let's Encrypt:

```nginx
server {
    listen 443 ssl http2;
    server_name ntfy.yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/ntfy.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ntfy.yourdomain.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        
        # For WebSocket support
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## Per-Site Custom Topics

You can configure custom NTFY topics for individual sites:

1. Go to Site Settings
2. Set "NTFY Topic" field
3. Alerts for this site will be sent to the custom topic

This is useful for:
- Client-specific notifications
- Different notification channels per site
- Routing alerts to different team members

## Notification Features

### Priority Levels

NTFY supports priority levels that affect how notifications are delivered:

- `min` - No sound, no vibration, no banner
- `low` - No sound, no vibration, banner only
- `default` - Sound, vibration, banner (default)
- `high` - Sound, vibration, banner, can override Do Not Disturb
- `urgent` - Same as high, with urgent visual indication

LongBark automatically sets priority based on alert severity:
- **Critical** alerts: `urgent`
- **Error** alerts: `high`
- **Warning** alerts: `default`
- **Info** alerts: `low`

### Rich Notifications

LongBark sends rich notifications with:

- **Title**: Site name and alert type
- **Message**: Detailed alert information
- **Tags**: Emoji icons for visual identification
- **Actions**: Quick action buttons (view site, open dashboard)
- **Click URL**: Direct link to site or dashboard

### Example Notification

```
🔴 example.com - Uptime Alert
Site is down
Status code: 500

[View Site] [Open Dashboard]
```

## Notification Workflow

### 1. Alert Detection

When LongBark detects an issue:
1. Issue is checked against alert threshold
2. Alert is created in database
3. Alert is queued for notification

### 2. NTFY Notification

Alert is sent to NTFY with:
- Appropriate topic (per-alert-type or custom)
- Severity-based priority
- Relevant emoji tags
- Action buttons

### 3. Alert Lifecycle

- **Open**: New alert created, notification sent
- **Acknowledged**: User acknowledges, no more notifications
- **Resolved**: Issue fixed, resolution notification sent

## Troubleshooting

### Not Receiving Notifications

1. **Check NTFY is enabled**:
   ```bash
   docker-compose exec backend env | grep NTFY_ENABLED
   ```

2. **Verify topic subscription**:
   - Confirm you're subscribed to the correct topic
   - Check for typos in topic name

3. **Test NTFY directly**:
   ```bash
   curl -d "Test message" ntfy.sh/your-topic
   ```

4. **Check Celery worker logs**:
   ```bash
   docker-compose logs celery_worker | grep ntfy
   ```

### Notifications Delayed

NTFY notifications should be instant. If delayed:

1. **Check network connectivity** to NTFY server
2. **Check NTFY server status** (if self-hosted)
3. **Review Celery worker performance**

### Wrong Topic Receiving Notifications

1. **Check environment variables**:
   ```bash
   docker-compose exec backend env | grep NTFY_TOPIC
   ```

2. **Verify site-specific topic** in site settings

3. **Check alert type** matches expected topic

## Best Practices

### Topic Organization

Use a hierarchical naming scheme:

```bash
# Production alerts
NTFY_TOPIC_UPTIME=longbark-prod-uptime
NTFY_TOPIC_SSL=longbark-prod-ssl

# Development/staging
NTFY_TOPIC_UPTIME=longbark-dev-uptime
```

### Separate Critical Alerts

Create separate subscriptions for critical alerts:

```bash
# Critical alerts to phone with sound
NTFY_TOPIC_UPTIME=longbark-critical

# Less urgent to desktop only
NTFY_TOPIC_SEO=longbark-info
```

### Team Notifications

Use different topics for different team members:

```bash
# DevOps team
NTFY_TOPIC_UPTIME=longbark-devops
NTFY_TOPIC_PERFORMANCE=longbark-devops

# SEO team
NTFY_TOPIC_SEO=longbark-seo-team
```

### Privacy Considerations

If using public ntfy.sh:
- Choose unique, non-guessable topic names
- Don't include sensitive information in alert messages
- Consider self-hosting for production use

## Integration with n8n

You can further automate with n8n workflows:

1. Subscribe to NTFY topics in n8n
2. Trigger workflows based on alerts
3. Send to Slack, Discord, SMS, etc.
4. Create tickets in issue tracking systems

Example n8n workflow:
```
NTFY Trigger → Filter (severity=critical) → Create PagerDuty Incident
```

## Advanced Configuration

### Custom Alert Messages

Modify alert messages in code:

```python
# app/tasks/monitoring_tasks.py
await ntfy_service.send_alert(
    site_name=site.name,
    alert_type=AlertType.UPTIME,
    severity="critical",
    message="Custom message here",
    details={"key": "value"},
    site_url=site.url,
)
```

### Webhook Integration

NTFY supports webhooks for received messages. You can use this for:
- Acknowledging alerts via NTFY
- Two-way communication
- Integration with other tools

## Resources

- NTFY Documentation: https://docs.ntfy.sh
- NTFY GitHub: https://github.com/binwiederhier/ntfy
- NTFY App Stores: https://ntfy.sh/docs/subscribe/phone/
- Self-Hosting Guide: https://docs.ntfy.sh/install/
