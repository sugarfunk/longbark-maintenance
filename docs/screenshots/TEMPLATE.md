# Screenshot Template

When adding screenshots to the README, use this format:

## Example Usage in README.md

```markdown
### Dashboard Overview
![Dashboard](docs/screenshots/02-dashboard.png)
*Main dashboard showing site health statistics, uptime graphs, and recent alerts. The dashboard provides an at-a-glance view of all monitored sites with color-coded health indicators.*

**Key Features Shown:**
- Site health status cards
- Recent alerts feed
- Uptime percentage graphs
- Quick action buttons
```

## Screenshot Guidelines

### Image Requirements
- **Format**: PNG (preferred) or JPG
- **Resolution**: Minimum 1280x720, recommended 1920x1080
- **File Size**: Keep under 500KB (use compression tools if needed)
- **Quality**: Clear, readable text; no blur or pixelation

### Naming Convention
Use numbered prefixes for logical ordering:
- `01-login.png` - Login page
- `02-dashboard.png` - Main dashboard
- `03-sites-list.png` - Sites overview
- `04-site-detail.png` - Individual site monitoring
- `05-wordpress-updates.png` - WordPress update tracking
- `06-seo-analytics.png` - SEO tracking and analytics
- `07-alerts.png` - Alerts and notifications
- `08-clients.png` - Client management
- `09-reports.png` - Report generation
- `10-settings.png` - Settings and configuration

### Content Guidelines

**Do Include:**
- Representative data (use demo/test data, not real client information)
- All UI elements clearly visible
- Consistent theme/styling across screenshots
- Tooltips or hover states when they demonstrate features

**Don't Include:**
- Real client data or sensitive information
- Personal information (emails, phone numbers, addresses)
- API keys, tokens, or credentials
- Internal IP addresses or server details

### Screenshot Workflow

1. **Prepare Demo Data**
   ```bash
   # Use the demo data script (if available)
   docker-compose exec backend python -m app.scripts.load_demo_data
   ```

2. **Set Browser Window Size**
   - Use consistent window size for all screenshots
   - Recommended: 1920x1080 for desktop views
   - For responsive views: 375x667 (mobile), 768x1024 (tablet)

3. **Capture Screenshot**
   - Use browser's built-in screenshot tool (F12 → Ctrl+Shift+P → "Capture screenshot")
   - Or use command-line tools:
   ```bash
   # Using Playwright
   npx playwright screenshot http://localhost:3000 docs/screenshots/02-dashboard.png --viewport-size=1920,1080
   ```

4. **Optimize Image**
   ```bash
   # Using ImageOptim, TinyPNG, or similar tools
   # Command line example with pngquant:
   pngquant --quality=65-80 docs/screenshots/02-dashboard.png
   ```

5. **Add to README**
   - Update the Screenshots section with your image
   - Include descriptive alt text
   - Add a caption explaining what the screenshot shows

### Example Screenshots Section

Here's how the README Screenshots section should look with actual images:

```markdown
## 📸 Screenshots

### Dashboard Overview
![Dashboard](docs/screenshots/02-dashboard.png)
*Main dashboard displaying site health metrics, uptime statistics, and recent alerts*

### Site Monitoring Detail
![Site Detail](docs/screenshots/04-site-detail.png)
*Comprehensive monitoring view with uptime graphs, performance metrics, SSL status, and broken link detection*

### WordPress Management
![WordPress Updates](docs/screenshots/05-wordpress-updates.png)
*Track WordPress core, plugin, and theme updates across all client sites*

### SEO Analytics
![SEO Dashboard](docs/screenshots/06-seo-analytics.png)
*Keyword rankings, search console integration, and SEO health scores*

### Alert Management
![Alerts](docs/screenshots/07-alerts.png)
*Real-time alert feed with severity levels and notification history*

### Client Portal
![Client Management](docs/screenshots/08-clients.png)
*Client dashboard with site grouping and performance overviews*
```

## Quality Checklist

Before submitting screenshots, verify:

- [ ] No sensitive or real client data visible
- [ ] Images are properly compressed (< 500KB each)
- [ ] Text is readable at normal viewing size
- [ ] Screenshots show the latest UI design
- [ ] Consistent browser chrome/theme across images
- [ ] Images demonstrate key features clearly
- [ ] Filenames follow naming convention
- [ ] Alt text is descriptive and meaningful
- [ ] Captions explain what users are seeing

## Tools & Resources

### Screenshot Tools
- **Browser DevTools**: Built into Chrome, Firefox, Edge
- **Playwright**: `npm install -D @playwright/test`
- **Puppeteer**: `npm install puppeteer`
- **Firefox Screenshot**: Built-in feature
- **ShareX**: Windows screenshot tool
- **Flameshot**: Linux screenshot tool
- **CleanShot X**: macOS screenshot tool

### Image Optimization
- **TinyPNG**: https://tinypng.com/
- **ImageOptim**: https://imageoptim.com/
- **pngquant**: Command-line PNG compressor
- **SVGO**: SVG optimizer

### Demo Data Generators
- **Faker.js**: Generate realistic demo data
- **Mockaroo**: Create custom datasets
- **JSON Generator**: API for test data
