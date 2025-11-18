# Configuration Guide

Complete reference for configuring LongBark Hosting Management & SEO Tool.

## Environment Variables

All configuration is done through environment variables in the `.env` file.

### Database Configuration

```bash
# PostgreSQL server hostname (use 'db' for Docker Compose)
POSTGRES_SERVER=db

# Database user
POSTGRES_USER=longbark

# Database password (change this!)
POSTGRES_PASSWORD=changeme_strong_password

# Database name
POSTGRES_DB=longbark

# Full database URL (auto-generated from above)
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_SERVER}/${POSTGRES_DB}
```

**Important:** Use a strong, unique password for production!

### Redis Configuration

```bash
# Redis hostname
REDIS_HOST=redis

# Redis port
REDIS_PORT=6379

# Full Redis URL
REDIS_URL=redis://${REDIS_HOST}:${REDIS_PORT}/0
```

### Application Security

```bash
# Secret key for JWT tokens (MUST be changed!)
SECRET_KEY=changeme_very_long_random_secret_key_here

# API version prefix
API_V1_STR=/api/v1

# Application name
PROJECT_NAME=LongBark Hosting Manager

# Allowed CORS origins (comma-separated or JSON array)
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
```

**Generate secure secret key:**
```bash
openssl rand -hex 32
# or
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Admin User

```bash
# First superuser email
FIRST_SUPERUSER=admin@longbark.com

# First superuser password
FIRST_SUPERUSER_PASSWORD=changeme_admin_password
```

These credentials are used to create the initial admin account. Change the password after first login!

### Email Configuration

```bash
# Enable TLS
SMTP_TLS=True

# SMTP server port
SMTP_PORT=587

# SMTP server hostname
SMTP_HOST=smtp.example.com

# SMTP username
SMTP_USER=notifications@longbark.com

# SMTP password
SMTP_PASSWORD=changeme_smtp_password

# From email address
EMAILS_FROM_EMAIL=notifications@longbark.com

# From name
EMAILS_FROM_NAME=LongBark Hosting
```

**Common SMTP Providers:**

#### Gmail
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_TLS=True
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=<app-specific-password>
```

#### SendGrid
```bash
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=<your-sendgrid-api-key>
```

#### Mailgun
```bash
SMTP_HOST=smtp.mailgun.org
SMTP_PORT=587
SMTP_USER=<your-username>@<your-domain>
SMTP_PASSWORD=<your-mailgun-password>
```

### NTFY Configuration

```bash
# Enable NTFY notifications
NTFY_ENABLED=True

# NTFY server URL
NTFY_SERVER_URL=https://ntfy.sh

# Default topic for all notifications
NTFY_DEFAULT_TOPIC=longbark-alerts

# Notification priority (min, low, default, high, urgent)
NTFY_PRIORITY=default

# Per-alert-type topics (optional)
NTFY_TOPIC_UPTIME=longbark-uptime
NTFY_TOPIC_SSL=longbark-ssl
NTFY_TOPIC_PERFORMANCE=longbark-performance
NTFY_TOPIC_SEO=longbark-seo
NTFY_TOPIC_WORDPRESS=longbark-wordpress
```

See [NTFY.md](NTFY.md) for detailed setup.

### Invoice Ninja Configuration

```bash
# Enable Invoice Ninja integration
INVOICE_NINJA_ENABLED=False

# Invoice Ninja URL
INVOICE_NINJA_URL=https://invoice.longbark.com

# API token from Invoice Ninja
INVOICE_NINJA_API_TOKEN=changeme_invoice_ninja_token

# API version (v5 recommended)
INVOICE_NINJA_API_VERSION=v5
```

See [INVOICE_NINJA.md](INVOICE_NINJA.md) for detailed setup.

### Google Search Console (Optional)

```bash
# Enable Google Search Console integration
GSC_ENABLED=False

# Path to Google Cloud credentials JSON file
GSC_CREDENTIALS_FILE=/app/credentials/gsc-credentials.json
```

**Setup:**
1. Create a Google Cloud project
2. Enable Search Console API
3. Create service account
4. Download credentials JSON
5. Mount credentials file in Docker

```yaml
# docker-compose.yml
services:
  backend:
    volumes:
      - ./gsc-credentials.json:/app/credentials/gsc-credentials.json:ro
```

### Monitoring Configuration

```bash
# Default check interval for all sites (seconds)
DEFAULT_CHECK_INTERVAL=300  # 5 minutes

# HTTP request timeout (seconds)
UPTIME_TIMEOUT=30

# Days before SSL expiry to send warning
SSL_WARNING_DAYS=30

# Maximum acceptable page load time (milliseconds)
PERFORMANCE_THRESHOLD=3000

# Maximum concurrent threads for broken link checking
BROKEN_LINK_MAX_THREADS=10
```

**Recommended intervals by site importance:**

| Site Type | Interval | Reasoning |
|-----------|----------|-----------|
| Critical production | 60s | Immediate detection |
| Important client sites | 300s (5min) | Balance detection/resources |
| Standard sites | 900s (15min) | Adequate monitoring |
| Development/staging | 3600s (1hr) | Less critical |
| SEO-only | 86400s (1day) | SEO changes slowly |

### Screenshot Configuration

```bash
# Enable screenshot capture
SCREENSHOT_ENABLED=True

# Screenshot width in pixels
SCREENSHOT_WIDTH=1920

# Screenshot height in pixels
SCREENSHOT_HEIGHT=1080
```

Screenshots are saved to `/app/screenshots` volume.

### Report Configuration

```bash
# Logo URL for reports
REPORT_LOGO_URL=https://longbark.com/logo.png

# Company name in reports
REPORT_COMPANY_NAME=LongBark Hosting

# Support email in reports
REPORT_SUPPORT_EMAIL=support@longbark.com
```

### Application URLs

```bash
# Frontend URL (for CORS and links)
FRONTEND_URL=http://localhost:3000

# Backend URL (for API calls)
BACKEND_URL=http://localhost:8000
```

**Production example:**
```bash
FRONTEND_URL=https://longbark.yourdomain.com
BACKEND_URL=https://api.longbark.yourdomain.com
```

## Docker Compose Configuration

### Port Mapping

```yaml
services:
  db:
    ports:
      - "5432:5432"  # PostgreSQL (can be removed if not accessing externally)
  
  redis:
    ports:
      - "6379:6379"  # Redis (can be removed if not accessing externally)
  
  backend:
    ports:
      - "8000:8000"  # FastAPI backend
  
  frontend:
    ports:
      - "3000:3000"  # React frontend (development)
  
  nginx:
    ports:
      - "80:80"      # Nginx reverse proxy
      - "443:443"    # HTTPS (if configured)
```

### Volume Configuration

```yaml
volumes:
  postgres_data:        # Database data (persistent)
  screenshots:          # Website screenshots
  reports:              # Generated reports
```

**Backup volumes:**
```bash
docker run --rm -v longbark_postgres_data:/data -v $(pwd):/backup ubuntu tar czf /backup/postgres_backup.tar.gz /data
```

### Resource Limits

For production, add resource limits:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
  
  celery_worker:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
```

### Environment-Specific Configurations

#### Development
```yaml
services:
  backend:
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - ./backend:/app  # Hot reload
```

#### Production
```yaml
services:
  backend:
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
    restart: unless-stopped
```

## Celery Configuration

### Worker Configuration

```python
# backend/app/tasks/celery_app.py

# Task execution limits
task_time_limit=30 * 60        # 30 minutes hard limit
task_soft_time_limit=25 * 60   # 25 minutes soft limit

# Concurrency
worker_concurrency=4            # Number of worker processes
worker_prefetch_multiplier=1   # Tasks to prefetch per worker
```

### Beat Schedule Configuration

```python
# Check interval for all sites
"check-all-sites-every-5-minutes": {
    "task": "app.tasks.monitoring_tasks.check_all_sites",
    "schedule": 300.0,  # Every 5 minutes
},

# Daily cleanup
"cleanup-old-data-daily": {
    "task": "app.tasks.monitoring_tasks.cleanup_old_data",
    "schedule": crontab(hour=2, minute=0),  # 2 AM daily
},
```

**Customize check frequency:**
- Edit `celery_app.py`
- Change `schedule` value (in seconds)
- Restart celery_beat service

### Monitoring Celery

```bash
# View Celery worker status
docker-compose exec celery_worker celery -A app.tasks.celery_app inspect active

# View scheduled tasks
docker-compose exec celery_beat celery -A app.tasks.celery_app inspect scheduled

# View registered tasks
docker-compose exec celery_worker celery -A app.tasks.celery_app inspect registered
```

## Frontend Configuration

### Environment Variables

Create `frontend/.env`:

```bash
# API URL
VITE_API_URL=http://localhost:8000/api/v1

# App title
VITE_APP_TITLE=LongBark Hosting Manager

# Enable debug mode
VITE_DEBUG=false
```

### Build Configuration

```javascript
// frontend/vite.config.js
export default defineConfig({
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

## Nginx Configuration

### Basic Configuration

```nginx
# nginx/nginx.conf
server {
    listen 80;
    server_name _;

    # Frontend
    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Backend API
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # API docs
    location /docs {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
    }

    # Static files
    location /screenshots {
        alias /usr/share/nginx/html/screenshots;
        autoindex off;
    }

    location /reports {
        alias /usr/share/nginx/html/reports;
        autoindex off;
    }
}
```

### HTTPS Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name longbark.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/longbark.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/longbark.yourdomain.com/privkey.pem;

    # SSL security settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    # ... rest of configuration
}

# HTTP redirect
server {
    listen 80;
    server_name longbark.yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

## Performance Tuning

### Database Performance

```sql
-- Increase connection pool
-- backend/app/core/database.py
engine = create_engine(
    str(settings.DATABASE_URL),
    pool_size=20,           # Increase from 10
    max_overflow=40,        # Increase from 20
    pool_pre_ping=True
)
```

### Redis Performance

```yaml
services:
  redis:
    command: redis-server --maxmemory 512mb --maxmemory-policy allkeys-lru
```

### Celery Performance

```bash
# Increase worker concurrency
docker-compose exec celery_worker celery -A app.tasks.celery_app worker --concurrency=8
```

## Security Hardening

### 1. Change Default Passwords

```bash
# Generate strong passwords
openssl rand -base64 32

# Update in .env
POSTGRES_PASSWORD=<strong-password>
FIRST_SUPERUSER_PASSWORD=<strong-password>
```

### 2. Restrict Network Access

```yaml
services:
  db:
    # Don't expose to host
    # ports:
    #   - "5432:5432"
    networks:
      - backend
```

### 3. Use Secrets Management

For production, use Docker secrets or external secret management:

```yaml
services:
  backend:
    secrets:
      - db_password
      - secret_key

secrets:
  db_password:
    external: true
  secret_key:
    external: true
```

### 4. Enable SSL/TLS

Always use HTTPS in production with valid certificates.

### 5. Regular Updates

```bash
# Update Docker images
docker-compose pull
docker-compose up -d
```

## Logging Configuration

### Application Logs

```python
# backend/app/core/config.py
LOGGING_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### Docker Logs

```bash
# View logs
docker-compose logs -f backend

# Limit log size
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## Backup Configuration

### Automated Backups

Add to cron:

```bash
# Daily database backup at 3 AM
0 3 * * * docker-compose exec -T db pg_dump -U longbark longbark > /backups/longbark_$(date +\%Y\%m\%d).sql
```

### Backup Script

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Database
docker-compose exec -T db pg_dump -U longbark longbark > "$BACKUP_DIR/db_$DATE.sql"

# Volumes
docker run --rm -v longbark_postgres_data:/data -v $BACKUP_DIR:/backup ubuntu tar czf /backup/volumes_$DATE.tar.gz /data

# Keep only last 30 days
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

## Monitoring LongBark Itself

### Health Checks

```yaml
services:
  backend:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Prometheus Metrics (Optional)

Add metrics endpoint for monitoring LongBark's performance.

## Troubleshooting Configuration Issues

### Verify Configuration

```bash
# Check environment variables are loaded
docker-compose exec backend env | grep -E "POSTGRES|REDIS|NTFY"

# Test database connection
docker-compose exec backend python -c "from app.core.database import engine; print(engine.url)"

# Test Redis connection
docker-compose exec backend python -c "from app.core.config import settings; print(settings.REDIS_URL)"
```

### Configuration Validation

```bash
# Validate docker-compose.yml
docker-compose config

# Check for syntax errors
docker-compose config --quiet && echo "Configuration is valid"
```

## Advanced Configuration

See specific guides for advanced topics:
- [NTFY Integration](NTFY.md)
- [Invoice Ninja Integration](INVOICE_NINJA.md)
- [Custom Monitoring Rules](#) (coming soon)
- [API Authentication](#) (coming soon)

## Configuration Checklist

Before going to production:

- [ ] Changed `SECRET_KEY`
- [ ] Changed `POSTGRES_PASSWORD`
- [ ] Changed `FIRST_SUPERUSER_PASSWORD`
- [ ] Configured SMTP for email alerts
- [ ] Set up NTFY for notifications
- [ ] Configured SSL/HTTPS
- [ ] Set appropriate check intervals
- [ ] Configured backups
- [ ] Set resource limits
- [ ] Enabled health checks
- [ ] Tested all integrations
- [ ] Reviewed security settings
- [ ] Configured monitoring for LongBark itself
