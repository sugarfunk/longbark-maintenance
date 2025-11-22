# Screenshots Guide

This directory contains screenshots showcasing the LongBark Hosting Management application.

## Taking Screenshots

To capture screenshots for the README:

1. **Start the application:**
   ```bash
   docker-compose up -d
   ```

2. **Wait for services to be ready:**
   ```bash
   # Check if services are running
   docker-compose ps

   # Wait for backend to be healthy
   curl http://localhost:8000/api/v1/health
   ```

3. **Create admin user:**
   ```bash
   docker-compose exec backend python -m app.scripts.create_admin
   ```

4. **Open the application:**
   - Frontend: http://localhost:3000
   - Login with admin credentials

5. **Capture screenshots:**
   - Login page
   - Dashboard with stats and charts
   - Sites list view
   - Site detail page with monitoring data
   - Alerts page
   - Clients management page

## Screenshot Specifications

- **Format:** PNG
- **Resolution:** 1920x1080 (or browser window at reasonable size)
- **File naming convention:**
  - `01-login.png` - Login page
  - `02-dashboard.png` - Main dashboard
  - `03-sites-list.png` - Sites overview
  - `04-site-detail.png` - Individual site monitoring
  - `05-alerts.png` - Alerts and notifications
  - `06-clients.png` - Client management

## Using Screenshots in README

After capturing screenshots, add them to the main README.md:

```markdown
## Screenshots

### Dashboard
![Dashboard](docs/screenshots/02-dashboard.png)
*Overview of all monitored sites with health status and key metrics*

### Site Monitoring
![Site Detail](docs/screenshots/04-site-detail.png)
*Detailed monitoring view showing uptime, performance, and SEO metrics*
```

## Tools for Screenshots

### Browser Screenshots
- Chrome DevTools (F12 → Ctrl+Shift+P → "Capture screenshot")
- Firefox Screenshot tool
- Browser extensions like "Awesome Screenshot"

### Command Line
```bash
# Using Playwright
npx playwright screenshot http://localhost:3000 docs/screenshots/dashboard.png

# Using Puppeteer
node -e "const puppeteer = require('puppeteer'); (async () => { const browser = await puppeteer.launch(); const page = await browser.newPage(); await page.setViewport({width: 1920, height: 1080}); await page.goto('http://localhost:3000'); await page.screenshot({path: 'docs/screenshots/dashboard.png'}); await browser.close(); })();"
```

## What to Capture

### 1. Login Page
- Clean login form
- Branding
- Focus on UX/UI

### 2. Dashboard
- Site health overview cards
- Status indicators
- Charts and graphs
- Recent alerts

### 3. Sites List
- Table view of all sites
- Health status indicators
- Quick actions

### 4. Site Detail
- Comprehensive monitoring data
- Uptime graphs
- Performance metrics
- SSL certificate status
- SEO scores

### 5. Alerts Page
- Active alerts
- Alert history
- Severity indicators

### 6. Client Management
- Client list
- Site associations
- Contact information
