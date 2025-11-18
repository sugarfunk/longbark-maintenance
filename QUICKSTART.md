# LongBark - Quick Start Guide

Get up and running with LongBark in 5 minutes!

## Prerequisites

- Docker and Docker Compose installed
- At least 2GB RAM available

## 1. Configure Environment

```bash
# Edit .env file (already created from .env.example)
nano .env
```

**Minimum required changes:**

```bash
# Change these!
POSTGRES_PASSWORD=your_strong_password_here
SECRET_KEY=your_secret_key_here
FIRST_SUPERUSER=your-email@domain.com
FIRST_SUPERUSER_PASSWORD=your_admin_password
```

**Optional but recommended:**

```bash
# Email alerts
SMTP_HOST=smtp.your-provider.com
SMTP_USER=your-email@domain.com
SMTP_PASSWORD=your_smtp_password

# NTFY notifications
NTFY_ENABLED=True
NTFY_DEFAULT_TOPIC=longbark-yourcompany-alerts
```

## 2. Start LongBark

```bash
# Start all services
docker-compose up -d

# Check status (all should be "Up")
docker-compose ps

# View logs
docker-compose logs -f
```

Wait for all services to start (30-60 seconds).

## 3. Create Admin User

```bash
docker-compose exec backend python -m app.scripts.create_admin
```

You should see:
```
Admin user created successfully: your-email@domain.com
```

## 4. Access the Dashboard

Open your browser:
```
http://localhost:3000
```

Login with your admin credentials.

## 5. Add Your First Site

1. Click **"+ Add Site"** button
2. Fill in:
   - **Name**: "My First Site"
   - **URL**: `https://example.com` (use a real site you want to monitor)
   - **Platform**: Select WordPress if applicable
3. Enable monitoring checks:
   - ✅ Uptime Monitoring
   - ✅ SSL Certificate
   - ✅ Performance
4. Click **"Save"**

## 6. Trigger a Manual Check

1. Click on your site
2. Click **"Check Now"** button
3. Wait 10-30 seconds
4. Refresh the page to see results

## 7. View Results

Navigate through the tabs:
- **Overview**: Current status
- **Uptime**: Response time chart
- **Performance**: Load time metrics
- **SEO**: SEO analysis

## What's Next?

### Set Up Notifications

**NTFY (Recommended):**
1. Install NTFY app on your phone
2. Subscribe to your topic: `longbark-yourcompany-alerts`
3. Test: `docker-compose exec backend python -c "from app.services.ntfy_service import ntfy_service; import asyncio; asyncio.run(ntfy_service.test_notification())"`

**Email:**
- Already configured if you set SMTP settings in step 1

### Add More Sites

- Click **"Sites"** → **"+ Add Site"**
- Add all your client sites
- Configure check intervals per site

### Set Up Clients (Optional)

1. Go to **"Clients"** page
2. Add your clients
3. Link sites to clients
4. Optional: Configure Invoice Ninja integration

### Configure WordPress Monitoring

For WordPress sites:
1. Edit site
2. Enable **"WordPress Checks"**
3. Provide WordPress admin credentials (optional, for deeper monitoring)

### Explore the Dashboard

- **Dashboard**: Overview of all sites
- **Alerts**: View and manage alerts
- **Reports**: Generate client reports

## Common Issues

### "Database connection failed"

Wait 30 seconds for PostgreSQL to fully start, then restart backend:
```bash
docker-compose restart backend
```

### "Can't access dashboard"

Check if all services are running:
```bash
docker-compose ps
```

If frontend is not running:
```bash
docker-compose logs frontend
docker-compose restart frontend
```

### "Monitoring checks not running"

Check Celery services:
```bash
docker-compose ps celery_worker celery_beat
docker-compose logs celery_worker
```

Restart if needed:
```bash
docker-compose restart celery_worker celery_beat
```

### Frontend can't connect to backend

Check CORS settings in `.env`:
```bash
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
```

## Resources

- **Full Documentation**: [docs/SETUP.md](docs/SETUP.md)
- **User Guide**: [docs/USER_GUIDE.md](docs/USER_GUIDE.md)
- **NTFY Setup**: [docs/NTFY.md](docs/NTFY.md)
- **Invoice Ninja**: [docs/INVOICE_NINJA.md](docs/INVOICE_NINJA.md)
- **Configuration**: [docs/CONFIGURATION.md](docs/CONFIGURATION.md)
- **API Docs**: http://localhost:8000/docs

## Quick Commands

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f celery_worker

# Restart a service
docker-compose restart backend

# Stop everything
docker-compose down

# Stop and remove volumes (fresh start)
docker-compose down -v

# Update and rebuild
git pull
docker-compose down
docker-compose build
docker-compose up -d
```

## Default Credentials

- **Dashboard**: Your configured email and password
- **API Docs**: http://localhost:8000/docs (no auth required for docs)

## Monitoring Intervals

Default check interval: 5 minutes

You can change this per-site or globally in `.env`:
```bash
DEFAULT_CHECK_INTERVAL=300  # seconds
```

## Support

For detailed guides and troubleshooting, see the [docs](docs/) directory.

---

**You're all set!** 🎉

LongBark is now monitoring your sites. You'll receive alerts via NTFY and email when issues are detected.
