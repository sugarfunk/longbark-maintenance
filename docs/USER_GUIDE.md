# LongBark Hosting Management & SEO Tool - User Guide

This guide covers how to use LongBark to monitor your hosting clients' sites and generate SEO reports.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Dashboard Overview](#dashboard-overview)
3. [Managing Sites](#managing-sites)
4. [Monitoring Types](#monitoring-types)
5. [Alerts and Notifications](#alerts-and-notifications)
6. [Client Management](#client-management)
7. [Reports](#reports)
8. [Best Practices](#best-practices)

## Getting Started

### First Login

1. Navigate to your LongBark installation (e.g., `http://localhost:3000`)
2. Enter your admin credentials
3. You'll be redirected to the dashboard

### Navigation

The main navigation menu includes:

- **Dashboard**: Overview of all sites and alerts
- **Sites**: Manage and monitor your sites
- **Alerts**: View and manage all alerts
- **Clients**: Manage clients (if using client management)
- **Reports**: Generate client reports

## Dashboard Overview

The dashboard provides a quick overview of your monitoring system:

### Key Metrics Cards

- **Total Sites**: Number of sites being monitored
- **Active Alerts**: Current unresolved alerts
- **Average Uptime**: Overall uptime across all sites
- **Avg Response Time**: Average page load time

### Sites Status

Visual representation of all sites with color indicators:

- 🟢 **Green**: Site is healthy, all checks passing
- 🟡 **Yellow**: Site has warnings (e.g., SSL expiring soon, slow performance)
- 🔴 **Red**: Site has critical issues (e.g., down, SSL expired)

### Recent Alerts

Shows the 10 most recent alerts across all sites. Click on an alert to:
- View full details
- Acknowledge the alert
- Go to the affected site

## Managing Sites

### Adding a New Site

1. Click **Sites** in the navigation menu
2. Click the **"+ Add Site"** button
3. Fill in the site details:

#### Basic Information

- **Name**: Friendly name for the site (e.g., "Client ABC Website")
- **URL**: Full URL including `https://` (e.g., `https://example.com`)
- **Platform**: Select platform type
  - **WordPress**: If it's a WordPress site
  - **Custom**: Custom-built site
  - **Static**: Static HTML site
  - **Other**: Other platforms
- **Status**: 
  - **Active**: Site will be monitored
  - **Paused**: Monitoring temporarily disabled
  - **Inactive**: Site not monitored

#### Monitoring Configuration

Enable the checks you want to run:

- ☑️ **Uptime Monitoring**: Check if site is online
- ☑️ **SSL Certificate**: Monitor SSL expiration
- ☑️ **Performance**: Track page load times
- ☑️ **Broken Links**: Find broken links on the site
- ☑️ **WordPress Checks**: Monitor WP core, plugins, themes (WordPress only)
- ☑️ **SEO Monitoring**: Check SEO health

**Check Interval**: How often to check the site (in seconds)
- Default: 300 (5 minutes)
- Minimum: 60 (1 minute)
- Maximum: 86400 (24 hours)

#### Alert Configuration

- **Alert Email**: Email address for alert notifications
- **NTFY Topic**: Custom NTFY topic for this site (optional)
- **Alert Threshold**: Number of consecutive failures before alerting

#### WordPress Configuration (if applicable)

- **Admin URL**: WordPress admin URL (e.g., `https://example.com/wp-admin`)
- **Username**: WordPress admin username (for API access)
- **Password**: WordPress admin password (stored encrypted)
- **API URL**: WordPress REST API URL (usually auto-detected)

#### Client Assignment

- **Client**: Select a client to link this site (optional)
- **Invoice Ninja Client ID**: If using Invoice Ninja integration

4. Click **"Save"** to create the site

### Viewing Site Details

Click on any site to view its detail page with tabs:

#### Overview Tab

- Current status and statistics
- Last check timestamp
- Quick actions (trigger check, edit, delete)

#### Uptime Tab

- 30-day uptime chart
- Uptime percentage
- Response time trend
- Recent downtime incidents

#### Performance Tab

- Page load time chart
- Performance score trend
- Resource counts (CSS, JS, images)
- Page size over time

#### SEO Tab

- SEO score
- Title and meta description analysis
- Header tag analysis
- Image alt text statistics
- Technical SEO checklist
- Recent SEO issues

#### Alerts Tab

- All alerts specific to this site
- Filter by status and severity
- Acknowledge or resolve alerts

### Editing a Site

1. Go to site detail page
2. Click **"Edit Site"** button
3. Modify any settings
4. Click **"Save Changes"**

### Deleting a Site

1. Go to site detail page
2. Click **"Delete Site"** button
3. Confirm deletion (this cannot be undone!)

All monitoring data for the site will be permanently deleted.

### Triggering Manual Checks

To immediately check a site without waiting for scheduled check:

1. Go to site detail page
2. Click **"Check Now"** button
3. Wait for checks to complete (usually 10-30 seconds)
4. Refresh page to see updated results

## Monitoring Types

### Uptime Monitoring

**What it checks:**
- Site accessibility (HTTP status codes)
- Response time
- Redirects
- Server headers

**Alert conditions:**
- Site returns non-200 status code
- Site times out (>30 seconds)
- Connection errors

**Frequency:** Every check interval

### SSL Certificate Monitoring

**What it checks:**
- Certificate validity
- Expiration date
- Certificate issuer
- Certificate chain
- SSL/TLS configuration

**Alert conditions:**
- Certificate expired
- Certificate expiring soon (< 30 days)
- Invalid certificate
- SSL errors

**Frequency:** Every check interval

### Performance Monitoring

**What it checks:**
- Total page load time
- Time to first byte (TTFB)
- DOM load time
- Page size
- Number of requests
- Resource types (CSS, JS, images)

**Alert conditions:**
- Load time exceeds threshold (default: 3000ms)
- Performance score drops below threshold

**Frequency:** Every check interval

**Note:** Performance checks use a headless browser and are more resource-intensive.

### Broken Links Monitoring

**What it checks:**
- All links on the homepage
- Internal links (same domain)
- External links (other domains)
- HTTP status for each link

**Alert conditions:**
- Broken links found (404, 500, etc.)
- Links timing out

**Frequency:** Less frequent (recommend 1-2 times per day)

**Note:** This check can take longer for pages with many links.

### WordPress Monitoring

**What it checks:**
- WordPress core version
- Available updates (core, plugins, themes)
- Installed plugins list
- Security vulnerabilities
- PHP version
- Common security issues

**Alert conditions:**
- WordPress core update available
- Plugin updates available
- Theme updates available
- Security issues detected

**Frequency:** Every check interval

**Requirements:** WordPress REST API accessible, or admin credentials provided.

### SEO Monitoring

**What it checks:**
- Title tag (length, presence)
- Meta description (length, presence)
- H1 tags (count, content)
- Header hierarchy (H2, H3, etc.)
- Image alt tags
- Word count
- Internal/external link ratio
- Robots.txt presence
- XML sitemap presence
- Mobile-friendliness (viewport tag)
- Schema.org markup
- Open Graph tags
- Twitter Card tags

**Alert conditions:**
- SEO score below 50/100
- Missing critical elements (title, meta description)
- Multiple H1 tags
- Many images without alt tags

**Frequency:** Daily recommended (less critical than uptime)

## Alerts and Notifications

### Alert Lifecycle

1. **Open**: Issue detected, alert created, notifications sent
2. **Acknowledged**: User has seen the alert, notifications stop
3. **Resolved**: Issue fixed, alert closed

### Alert Severities

- 🔴 **Critical**: Immediate attention required (site down, SSL expired)
- 🟠 **Error**: Serious issue requiring attention
- 🟡 **Warning**: Non-critical issue to investigate
- 🔵 **Info**: Informational (updates available, etc.)

### Viewing Alerts

Go to **Alerts** page to see all alerts with filters:

- **Status**: Open, Acknowledged, Resolved
- **Severity**: Critical, Error, Warning, Info
- **Type**: Uptime, SSL, Performance, Broken Links, WordPress, SEO
- **Site**: Filter by specific site

### Managing Alerts

**Acknowledge an Alert:**
1. Click on alert or select checkbox
2. Click **"Acknowledge"** button
3. Alert status changes to "Acknowledged"
4. No more notifications sent for this alert

**Resolve an Alert:**
1. Fix the underlying issue
2. Click on alert
3. Click **"Resolve"** button
4. Optionally add resolution notes
5. Alert status changes to "Resolved"

**Bulk Actions:**
- Select multiple alerts using checkboxes
- Use bulk action buttons (Acknowledge All, Resolve All)

### Notification Channels

#### Email Notifications

Sent to:
- Site-specific alert email (if configured)
- Admin email
- Client email (if client linked)

Includes:
- Alert details
- Site information
- Link to dashboard

#### NTFY Notifications

Real-time push notifications to your devices:
- Instant delivery
- Custom topics per alert type
- Action buttons (view site, open dashboard)
- Works on mobile and desktop

See [NTFY.md](NTFY.md) for setup instructions.

### Alert Thresholds

Configure how many failures trigger an alert:

- **Threshold = 1**: Alert on first failure (default)
- **Threshold = 2**: Alert after 2 consecutive failures
- **Threshold = 3**: Alert after 3 consecutive failures

Higher thresholds reduce false positives but may delay notifications.

## Client Management

### Adding Clients

1. Go to **Clients** page
2. Click **"+ Add Client"** button
3. Fill in client information:
   - Name
   - Email
   - Phone
   - Company
   - Address
   - Invoice Ninja ID (if applicable)
4. Click **"Save"**

### Viewing Client Details

Click on a client to see:

- Client information
- All sites for this client
- Aggregate statistics
- Links to Invoice Ninja (if integrated)

### Linking Sites to Clients

When creating or editing a site:
1. Select **Client** from dropdown
2. Save the site

The site will now appear on the client's detail page.

### Client Portal (Optional)

Enable portal access for clients:

1. Edit client
2. Enable **"Portal Access"**
3. Set portal username and password
4. Click **"Save"**

Clients can then log in to view:
- Their sites' status
- Monitoring reports
- Alert history
- Link to their Invoice Ninja billing

## Reports

### Generating Site Reports

1. Go to site detail page
2. Click **"Reports"** tab (or button)
3. Select date range (default: last 30 days)
4. Choose format:
   - **JSON**: For API/programmatic access
   - **HTML**: View in browser, print-friendly
   - **PDF**: Download for client delivery

### Report Contents

Reports include:

#### Executive Summary
- Uptime percentage
- Average response time
- Number of incidents
- Overall health score

#### Uptime Analysis
- Uptime chart
- Downtime incidents
- Response time trend

#### Performance Metrics
- Load time analysis
- Performance score trend
- Resource optimization suggestions

#### SEO Summary
- SEO score
- Key SEO metrics
- Issues found
- Recommendations

#### Security Status
- SSL certificate status
- Security score (if WordPress)
- Vulnerabilities found

### Scheduled Reports

(Coming soon)

Set up automatic weekly or monthly reports:
1. Configure report schedule
2. Select recipients
3. Reports sent automatically via email

## Best Practices

### Site Monitoring

1. **Start with essentials**: Enable uptime and SSL monitoring first
2. **Adjust check intervals**: 
   - Critical sites: 1-5 minutes
   - Normal sites: 5-15 minutes
   - SEO/broken links: Daily
3. **Use alert thresholds**: Set to 2-3 to avoid false positives
4. **Organize with clients**: Link sites to clients for better organization

### Alert Management

1. **Acknowledge alerts promptly**: Prevents duplicate notifications
2. **Add resolution notes**: Document how issues were fixed
3. **Review alert patterns**: Identify recurring issues
4. **Set up NTFY**: For instant mobile notifications
5. **Use custom topics**: Route different alerts to different channels

### Performance Optimization

1. **Monitor trends**: Look for performance degradation over time
2. **Check after changes**: Monitor closely after site updates
3. **Optimize resources**: Review resource counts for optimization opportunities
4. **Set realistic thresholds**: Adjust based on site complexity

### SEO Monitoring

1. **Fix critical issues first**: Title, meta description, H1 tags
2. **Monitor competitors**: Track keyword rankings vs. competitors
3. **Regular audits**: Review SEO reports monthly
4. **Track improvements**: Monitor SEO score trends
5. **Share with clients**: Include in monthly reports

### Client Communication

1. **Proactive updates**: Notify clients before issues become critical
2. **Regular reports**: Send monthly performance reports
3. **Portal access**: Give clients self-service access
4. **Invoice integration**: Link to billing for transparency
5. **Set expectations**: Communicate what you monitor and why

### Security

1. **Strong passwords**: Use strong, unique passwords
2. **Regular updates**: Keep WordPress sites updated
3. **Monitor SSL**: Don't let certificates expire
4. **Security scans**: Enable WordPress security checks
5. **Access control**: Limit who has access to the dashboard

### System Maintenance

1. **Review logs regularly**: Check for errors or issues
2. **Clean old data**: Old monitoring data is automatically cleaned after 90 days
3. **Backup database**: Regular backups of monitoring data
4. **Update LongBark**: Keep the application updated
5. **Monitor resource usage**: Ensure server has adequate resources

## Keyboard Shortcuts

(Coming soon)

- `Ctrl/Cmd + K`: Quick search
- `A`: Acknowledge selected alert
- `R`: Resolve selected alert
- `N`: Add new site
- `?`: Show help

## Getting Help

- **Documentation**: Check docs folder for detailed guides
- **API Docs**: Visit `/docs` on your backend server
- **Logs**: Review Docker logs for troubleshooting
- **GitHub Issues**: Report bugs or request features

## Tips and Tricks

1. **Bulk operations**: Use checkboxes for bulk alert management
2. **Filtering**: Use filters to focus on specific issues
3. **Bookmarks**: Bookmark frequently viewed sites
4. **Custom topics**: Use different NTFY topics for different priority levels
5. **Client view**: Switch to client view to see all sites per client
6. **Dark mode**: (Coming soon) Enable dark mode for night monitoring
7. **Mobile app**: Access dashboard from mobile browser
8. **API integration**: Use API for custom integrations with n8n, etc.

## Common Workflows

### Morning Site Check

1. Open dashboard
2. Review any red or yellow indicators
3. Check recent alerts
4. Acknowledge any overnight alerts
5. Investigate and resolve critical issues

### Adding New Client Site

1. Add client (if not exists)
2. Add site, link to client
3. Enable appropriate monitoring
4. Set alert email/NTFY topic
5. Trigger manual check to verify
6. Monitor for first 24 hours

### Monthly Client Reporting

1. Navigate to client page
2. For each site, generate report
3. Review metrics and trends
4. Identify areas for improvement
5. Send reports to client
6. Schedule any needed maintenance

### Incident Response

1. Receive alert (NTFY/email)
2. Acknowledge alert
3. Investigate issue (check site, logs)
4. Fix issue or escalate
5. Verify site is back up
6. Resolve alert with notes
7. Document in ticket system

## Troubleshooting

### Site Not Being Monitored

1. Check site status is "Active"
2. Verify monitoring checks are enabled
3. Check last checked timestamp
4. Review Celery worker logs
5. Trigger manual check

### Not Receiving Alerts

1. Verify alert email is configured
2. Check spam folder
3. Test NTFY integration
4. Review alert threshold settings
5. Check alert history for the site

### Performance Issues

1. Review check intervals (too frequent?)
2. Disable unnecessary checks
3. Check server resources
4. Review Docker logs for errors
5. Scale up if needed

### Data Not Showing

1. Refresh the page
2. Check date range filters
3. Verify monitoring is enabled
4. Trigger manual check
5. Check API connectivity

For more help, consult the [Setup Guide](SETUP.md) or [troubleshooting section](SETUP.md#troubleshooting).
