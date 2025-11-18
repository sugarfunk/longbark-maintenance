# LongBark Hosting Management & SEO Tool

A comprehensive web hosting management and SEO monitoring platform for managing 60+ client sites.

## Features

- **Site Health Monitoring**: Uptime, SSL certificates, broken links, performance metrics
- **WordPress Monitoring**: Core/plugin/theme updates, security checks
- **SEO Tracking**: Keyword rankings, SEO health, backlinks, domain authority
- **Client Reports**: PDF/HTML reports for client delivery
- **Integrations**: NTFY notifications, Invoice Ninja billing, Google Search Console
- **Client Portal**: Self-service portal for clients to view their sites
- **Automated Alerts**: Email and NTFY notifications for issues

## Tech Stack

- **Backend**: Python 3.11 with FastAPI
- **Frontend**: React 18 with Tailwind CSS
- **Database**: PostgreSQL 15
- **Task Queue**: Celery with Redis
- **Deployment**: Docker & Docker Compose

## Quick Start

### Prerequisites

- Docker and Docker Compose
- NTFY server (optional, for notifications)
- Invoice Ninja instance (optional, for billing integration)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd longbark-maintenance
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your settings
```

3. Start the application:
```bash
docker-compose up -d
```

4. Access the application:
- Dashboard: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Initial Setup

1. Create an admin user:
```bash
docker-compose exec backend python -m app.scripts.create_admin
```

2. Add your first site via the dashboard or API

## Configuration

See [docs/CONFIGURATION.md](docs/CONFIGURATION.md) for detailed configuration options.

## Documentation

- [Setup Guide](docs/SETUP.md)
- [User Guide](docs/USER_GUIDE.md)
- [API Documentation](docs/API.md)
- [NTFY Integration](docs/NTFY.md)
- [Invoice Ninja Integration](docs/INVOICE_NINJA.md)

## Architecture

```
┌─────────────────┐
│  React Frontend │
│   (Port 3000)   │
└────────┬────────┘
         │
┌────────▼────────┐      ┌──────────────┐
│  FastAPI Backend│◄─────┤ PostgreSQL   │
│   (Port 8000)   │      │   Database   │
└────────┬────────┘      └──────────────┘
         │
┌────────▼────────┐      ┌──────────────┐
│ Celery Workers  │◄─────┤    Redis     │
│ (Monitoring)    │      │  (Broker)    │
└─────────────────┘      └──────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  External Services              │
│  - NTFY (Notifications)         │
│  - Invoice Ninja (Billing)      │
│  - Google Search Console        │
│  - Client Sites                 │
└─────────────────────────────────┘
```

## License

Proprietary - LongBark Business Use Only
