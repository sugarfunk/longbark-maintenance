# LongBark Hosting Management & SEO Tool - Setup Guide

This guide will walk you through setting up the LongBark Hosting Management & SEO Tool on your infrastructure.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Configuration](#configuration)
4. [Starting the Application](#starting-the-application)
5. [Creating the Admin User](#creating-the-admin-user)
6. [Accessing the Application](#accessing-the-application)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

Before you begin, ensure you have the following installed on your server:

- **Docker** (version 20.10 or higher)
- **Docker Compose** (version 2.0 or higher)
- At least **2GB RAM** available
- At least **10GB disk space**

### Optional Prerequisites

- **NTFY server** for notifications (can use public ntfy.sh)
- **Invoice Ninja** instance for billing integration
- **Google Search Console** API credentials for GSC integration

## Initial Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd longbark-maintenance
```

### 2. Create Environment File

Copy the example environment file and customize it:

```bash
cp .env.example .env
```

### 3. Edit Environment Variables

Open the `.env` file and configure the following **critical** settings:

#### Database Configuration
```bash
POSTGRES_PASSWORD=<strong-random-password>
```

#### Application Security
```bash
SECRET_KEY=<generate-a-long-random-string-here>
```

Generate a secure secret key:
```bash
openssl rand -hex 32
```

#### Admin User
```bash
FIRST_SUPERUSER=admin@yourdomain.com
FIRST_SUPERUSER_PASSWORD=<strong-password>
```

#### Email Configuration (for alerts)
```bash
SMTP_HOST=smtp.your-provider.com
SMTP_PORT=587
SMTP_USER=your-email@domain.com
SMTP_PASSWORD=<your-smtp-password>
EMAILS_FROM_EMAIL=notifications@yourdomain.com
```

#### NTFY Configuration
```bash
NTFY_ENABLED=True
NTFY_SERVER_URL=https://your-ntfy-server.com  # or https://ntfy.sh
NTFY_DEFAULT_TOPIC=longbark-alerts
```

See [NTFY.md](NTFY.md) for detailed NTFY setup.

#### Invoice Ninja Configuration (Optional)
```bash
INVOICE_NINJA_ENABLED=True
INVOICE_NINJA_URL=https://your-invoice-ninja.com
INVOICE_NINJA_API_TOKEN=<your-api-token>
```

See [INVOICE_NINJA.md](INVOICE_NINJA.md) for detailed Invoice Ninja setup.

## Configuration

### CORS Origins

If you're running the frontend on a different domain, update the CORS origins:

```bash
BACKEND_CORS_ORIGINS=["http://localhost:3000","https://yourdomain.com"]
```

### Monitoring Intervals

Adjust monitoring intervals to suit your needs:

```bash
DEFAULT_CHECK_INTERVAL=300  # 5 minutes (in seconds)
SSL_WARNING_DAYS=30  # Days before SSL expiry to alert
PERFORMANCE_THRESHOLD=3000  # Max load time in milliseconds
```

## Starting the Application

### 1. Build and Start All Services

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database
- Redis (for Celery)
- FastAPI backend
- Celery worker
- Celery beat (scheduler)
- React frontend
- Nginx (reverse proxy)

### 2. Check Service Status

```bash
docker-compose ps
```

All services should show as "Up" or "running".

### 3. View Logs

To view logs from all services:
```bash
docker-compose logs -f
```

To view logs from a specific service:
```bash
docker-compose logs -f backend
docker-compose logs -f celery_worker
```

## Creating the Admin User

After the database is initialized, create the admin user:

```bash
docker-compose exec backend python -m app.scripts.create_admin
```

You should see:
```
Admin user created successfully: admin@yourdomain.com
Password: <your-password>

Please change the password after first login!
```

## Accessing the Application

### Web Dashboard

Open your browser and navigate to:
```
http://localhost:3000
```

Or if using nginx on port 80:
```
http://your-server-ip
```

### API Documentation

Access the interactive API documentation:
```
http://localhost:8000/docs
```

### Login

Use the admin credentials you configured in the `.env` file:
- Email: `admin@yourdomain.com`
- Password: `<your-password>`

## Post-Installation Steps

### 1. Add Your First Site

1. Log in to the dashboard
2. Click "Add Site" button
3. Fill in the site details:
   - Name: A friendly name for the site
   - URL: Full URL including https://
   - Platform: Select WordPress if applicable
   - Enable checks you want to run
4. Click "Save"

### 2. Test Notifications

Test your NTFY integration:

```bash
docker-compose exec backend python -c "
from app.services.ntfy_service import ntfy_service
import asyncio
asyncio.run(ntfy_service.test_notification())
"
```

### 3. Add Clients (Optional)

If you're using Invoice Ninja integration:
1. Go to the "Clients" page
2. Add a client
3. Link the client to their Invoice Ninja record
4. Assign sites to the client

### 4. Configure Site-Specific Settings

For each site, you can configure:
- **Check interval**: How often to monitor the site
- **Alert email**: Where to send alerts for this site
- **NTFY topic**: Custom NTFY topic for this site
- **WordPress credentials**: For deeper WordPress monitoring

## Tailscale Integration

If you're using Tailscale networking:

### 1. Install Tailscale on the Host

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

### 2. Update Environment Variables

Set the backend URL to use your Tailscale hostname:

```bash
BACKEND_URL=http://<your-tailscale-hostname>:8000
FRONTEND_URL=http://<your-tailscale-hostname>:3000
```

### 3. Configure NTFY with Tailscale

If running NTFY on your Tailscale network:

```bash
NTFY_SERVER_URL=http://<ntfy-tailscale-hostname>
```

## Reverse Proxy Setup (Production)

For production deployment, use a reverse proxy like Nginx or Caddy.

### Example Nginx Configuration

```nginx
server {
    listen 80;
    server_name longbark.yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### SSL with Let's Encrypt

```bash
sudo certbot --nginx -d longbark.yourdomain.com
```

## Troubleshooting

### Database Connection Errors

If you see database connection errors:

1. Check if PostgreSQL is running:
   ```bash
   docker-compose ps db
   ```

2. Check PostgreSQL logs:
   ```bash
   docker-compose logs db
   ```

3. Ensure the database URL is correct in `.env`

### Celery Worker Not Running Tasks

1. Check if Redis is running:
   ```bash
   docker-compose ps redis
   ```

2. Check Celery worker logs:
   ```bash
   docker-compose logs celery_worker
   ```

3. Restart the worker:
   ```bash
   docker-compose restart celery_worker
   ```

### Frontend Can't Connect to Backend

1. Check CORS configuration in `.env`
2. Ensure backend is accessible from the frontend container
3. Check browser console for CORS errors
4. Verify `REACT_APP_API_URL` in frontend environment

### Monitoring Checks Not Running

1. Check Celery beat is running:
   ```bash
   docker-compose ps celery_beat
   ```

2. Check for errors in Celery beat logs:
   ```bash
   docker-compose logs celery_beat
   ```

3. Manually trigger a check for debugging:
   ```bash
   docker-compose exec backend python -c "
   from app.tasks.monitoring_tasks import check_site
   check_site.delay(1)  # Replace 1 with your site ID
   "
   ```

### Permission Errors

If you encounter permission errors with volumes:

```bash
sudo chown -R 999:999 postgres_data
sudo chown -R $USER:$USER screenshots reports
```

## Backup and Restore

### Backup Database

```bash
docker-compose exec db pg_dump -U longbark longbark > backup.sql
```

### Restore Database

```bash
docker-compose exec -T db psql -U longbark longbark < backup.sql
```

### Backup Volumes

```bash
docker run --rm -v longbark_postgres_data:/data -v $(pwd):/backup ubuntu tar czf /backup/postgres_backup.tar.gz /data
```

## Updating the Application

### Pull Latest Changes

```bash
git pull origin main
```

### Rebuild and Restart

```bash
docker-compose down
docker-compose build
docker-compose up -d
```

### Run Database Migrations

```bash
docker-compose exec backend alembic upgrade head
```

## Next Steps

- Read the [User Guide](USER_GUIDE.md) to learn how to use the application
- Set up [NTFY Integration](NTFY.md) for notifications
- Configure [Invoice Ninja Integration](INVOICE_NINJA.md) for billing
- Review the [API Documentation](API.md) for API usage

## Support

For issues and questions:
- Check the [Troubleshooting](#troubleshooting) section
- Review logs: `docker-compose logs`
- Open an issue on GitHub
