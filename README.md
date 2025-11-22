# LongBark Hosting Management & SEO Tool

<div align="center">

A comprehensive web hosting management and SEO monitoring platform for managing 60+ client sites.

[![Docker Build](https://github.com/sugarfunk/longbark-maintenance/actions/workflows/docker-build.yml/badge.svg)](https://github.com/sugarfunk/longbark-maintenance/actions/workflows/docker-build.yml)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/react-18-blue.svg)](https://reactjs.org/)

[Features](#features) • [Screenshots](#screenshots) • [Quick Start](#quick-start) • [Documentation](#documentation) • [Architecture](#architecture)

</div>

---

## ✨ Features

### 🔍 **Site Health Monitoring**
- **Uptime Monitoring**: 24/7 availability checks with detailed downtime reporting
- **SSL Certificate Tracking**: Automatic expiry notifications and renewal reminders
- **Broken Links Detection**: Scan and identify broken links across all pages
- **Performance Metrics**: Load time monitoring, Core Web Vitals tracking
- **Response Time Analysis**: Track server response times and identify slow endpoints

### 🔧 **WordPress Monitoring**
- **Update Detection**: Monitor WordPress core, plugins, and themes for available updates
- **Security Checks**: Identify vulnerable plugins and outdated software
- **Version Tracking**: Keep track of all installed plugins and their versions
- **Health Dashboard**: WordPress-specific health indicators

### 📊 **SEO Tracking**
- **Keyword Rankings**: Track search engine rankings for target keywords
- **SEO Health Scores**: Comprehensive SEO analysis and recommendations
- **Backlink Monitoring**: Track incoming links and domain authority
- **Google Search Console Integration**: Pull real-time search performance data
- **Meta Tag Analysis**: Verify proper meta descriptions, titles, and structured data

### 📈 **Client Reports**
- **Automated Report Generation**: PDF and HTML reports with customizable templates
- **Scheduled Delivery**: Automatic email distribution to clients
- **Performance Summaries**: Monthly/weekly statistics and trend analysis
- **Custom Branding**: White-label reports with your company branding

### 🔔 **Alerts & Notifications**
- **Real-time Alerts**: Instant notifications via email and NTFY
- **Customizable Thresholds**: Set your own alert criteria
- **Alert Prioritization**: Critical, warning, and info level alerts
- **Multi-channel Delivery**: Email, NTFY push notifications, webhooks

### 💼 **Client Management**
- **Client Portal**: Self-service dashboard for clients to view their sites
- **Invoice Ninja Integration**: Seamless billing and invoicing workflow
- **Contact Management**: Store client information and communication history
- **Site Grouping**: Organize sites by client for easy management

---

## 📸 Screenshots

> **Note**: Screenshots will be added soon. To contribute screenshots, see [docs/screenshots/README.md](docs/screenshots/README.md).

### Dashboard Overview
*Coming soon: Main dashboard showing site health statistics, recent alerts, and monitoring status*

### Site Monitoring
*Coming soon: Detailed site view with uptime graphs, performance metrics, and SSL status*

### WordPress Updates
*Coming soon: WordPress core, plugin, and theme update tracking*

### SEO Analytics
*Coming soon: Keyword rankings, search console data, and SEO health scores*

### Alerts & Notifications
*Coming soon: Real-time alert feed with severity indicators*

### Client Portal
*Coming soon: Client-facing dashboard with site performance overview*

---

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- NTFY server (optional, for notifications)
- Invoice Ninja instance (optional, for billing integration)

### Installation

#### Option 1: Using Pre-built Images (Recommended for Production)

Pull and run pre-built Docker images from GitHub Container Registry:

```bash
# Clone repository for docker-compose file
git clone https://github.com/sugarfunk/longbark-maintenance.git
cd longbark-maintenance

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Pull and start with pre-built images
docker-compose -f docker-compose.production.yml up -d
```

See [docs/DOCKER.md](docs/DOCKER.md) for detailed Docker deployment instructions.

#### Option 2: Build from Source (Development)

1. Clone the repository:
```bash
git clone https://github.com/sugarfunk/longbark-maintenance.git
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
- 🌐 **Dashboard**: http://localhost:3000 (or http://localhost if using production compose)
- 🔌 **API**: http://localhost:8000
- 📚 **API Docs**: http://localhost:8000/docs

### Initial Setup

1. Create an admin user:
```bash
docker-compose exec backend python -m app.scripts.create_admin
```

2. Login to the dashboard with your admin credentials

3. Add your first site:
   - Click "Add Site" in the dashboard
   - Enter site URL and monitoring preferences
   - Configure notification thresholds

4. (Optional) Configure integrations:
   - NTFY for push notifications
   - Invoice Ninja for billing
   - Google Search Console for SEO data

---

## 🛠 Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Python 3.11 with FastAPI |
| **Frontend** | React 18 with Tailwind CSS |
| **Database** | PostgreSQL 15 |
| **Task Queue** | Celery with Redis |
| **Container** | Docker & Docker Compose |
| **Monitoring** | Celery Beat (scheduled tasks) |
| **Web Server** | Nginx (production) |

---

## 📚 Documentation

- [🔧 Development Guide](docs/DEVELOPMENT.md) - Set up local development environment
- [📦 Docker Deployment Guide](docs/DOCKER.md) - Complete guide for deploying with Docker
- [⚙️ Configuration Guide](docs/CONFIGURATION.md) - Environment variables and settings
- [👤 User Guide](docs/USER_GUIDE.md) - How to use the platform
- [🔔 NTFY Integration](docs/NTFY.md) - Set up push notifications
- [💰 Invoice Ninja Integration](docs/INVOICE_NINJA.md) - Configure billing integration
- [📸 Contributing Screenshots](docs/screenshots/README.md) - Guide for adding screenshots

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    LongBark Platform                         │
└─────────────────────────────────────────────────────────────┘

┌─────────────────┐         ┌─────────────────┐
│  React Frontend │◄────────┤     Nginx       │
│   (Port 3000)   │         │   (Port 80)     │
└────────┬────────┘         └─────────────────┘
         │
         │ REST API
         ▼
┌────────────────────┐      ┌──────────────────┐
│  FastAPI Backend   │◄─────┤  PostgreSQL 15   │
│   (Port 8000)      │      │   (Port 5432)    │
│                    │      └──────────────────┘
│ - REST API         │
│ - Authentication   │      ┌──────────────────┐
│ - Business Logic   │◄─────┤    Redis         │
└────────┬───────────┘      │   (Port 6379)    │
         │                  └──────────────────┘
         │ Task Queue
         ▼
┌─────────────────────┐
│  Celery Workers     │
│                     │
│ - Uptime checks     │
│ - SSL monitoring    │
│ - Performance tests │
│ - SEO analysis      │
│ - Report generation │
└──────────┬──────────┘
           │
           │ Scheduled Tasks
           ▼
┌──────────────────────┐
│   Celery Beat        │
│   (Scheduler)        │
└──────────┬───────────┘
           │
           ▼
┌────────────────────────────────────────┐
│         External Services              │
├────────────────────────────────────────┤
│ • NTFY (Push Notifications)            │
│ • Invoice Ninja (Billing)              │
│ • Google Search Console (SEO Data)     │
│ • Client WordPress Sites               │
│ • SMTP Server (Email Notifications)    │
└────────────────────────────────────────┘
```

### Data Flow

1. **Monitoring Pipeline**:
   - Celery Beat schedules monitoring tasks
   - Celery workers execute checks (uptime, SSL, performance)
   - Results stored in PostgreSQL
   - Alerts triggered for threshold violations

2. **User Interaction**:
   - React frontend communicates with FastAPI backend
   - JWT authentication for secure access
   - Real-time updates via API polling

3. **Notification Flow**:
   - Alerts generated by monitoring workers
   - NTFY server receives push notifications
   - SMTP server sends email alerts
   - Notifications logged in database

---

## 🔧 Configuration

Key environment variables (see `.env.example` for complete list):

```bash
# Database
DATABASE_URL=postgresql://user:password@db:5432/longbark
POSTGRES_USER=longbark
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=longbark

# Redis
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=your_secret_key_here

# SMTP (Email Notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# NTFY (Push Notifications)
NTFY_ENABLED=true
NTFY_SERVER_URL=https://ntfy.sh
NTFY_DEFAULT_TOPIC=longbark-alerts

# Invoice Ninja (Optional)
INVOICE_NINJA_ENABLED=false
INVOICE_NINJA_URL=https://your-instance.invoicing.co
INVOICE_NINJA_API_TOKEN=your_token_here
```

See [docs/CONFIGURATION.md](docs/CONFIGURATION.md) for detailed configuration options.

---

## 🤝 Contributing

This is a proprietary project for LongBark business use. For internal team members:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Adding Screenshots

To add screenshots to the README:

1. Run the application locally
2. Capture screenshots following the guide in [docs/screenshots/README.md](docs/screenshots/README.md)
3. Add images to `docs/screenshots/` directory
4. Update the Screenshots section in this README
5. Submit a pull request

---

## 📝 License

Proprietary - LongBark Business Use Only

Copyright © 2025 LongBark. All rights reserved.

---

## 🆘 Support

For issues, questions, or feature requests:

- Check the [documentation](docs/)
- Review existing [GitHub issues](https://github.com/sugarfunk/longbark-maintenance/issues)
- Contact the development team

---

<div align="center">

**[⬆ back to top](#longbark-hosting-management--seo-tool)**

Made with ❤️ by the LongBark Team

</div>
