# Development Guide

This guide will help you set up a local development environment for LongBark Hosting Management.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Initial Setup](#initial-setup)
- [Development Workflow](#development-workflow)
- [Project Structure](#project-structure)
- [Running Tests](#running-tests)
- [Database Management](#database-management)
- [API Development](#api-development)
- [Frontend Development](#frontend-development)
- [Debugging](#debugging)
- [Contributing](#contributing)

---

## Prerequisites

Before you begin, ensure you have the following installed:

### Required
- **Docker** (20.10+) and **Docker Compose** (2.0+)
  - [Install Docker Desktop](https://www.docker.com/products/docker-desktop/)
  - Verify: `docker --version && docker-compose --version`

- **Git** (2.30+)
  - Verify: `git --version`

### Optional (for local development without Docker)
- **Python 3.11+**
  - [Install Python](https://www.python.org/downloads/)
  - Verify: `python --version`

- **Node.js 18+** and **npm**
  - [Install Node.js](https://nodejs.org/)
  - Verify: `node --version && npm --version`

- **PostgreSQL 15+**
  - [Install PostgreSQL](https://www.postgresql.org/download/)

- **Redis 7+**
  - [Install Redis](https://redis.io/download/)

---

## Initial Setup

### 1. Clone the Repository

```bash
git clone https://github.com/sugarfunk/longbark-maintenance.git
cd longbark-maintenance
```

### 2. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit the file with your settings
nano .env  # or use your preferred editor
```

**Key environment variables to configure:**

```bash
# Database Configuration
POSTGRES_USER=longbark
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_DB=longbark
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=generate_a_secure_random_key_here
FIRST_SUPERUSER=admin@longbark.com
FIRST_SUPERUSER_PASSWORD=secure_admin_password

# Email Configuration (for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAILS_FROM_EMAIL=noreply@longbark.com

# NTFY Configuration (optional)
NTFY_ENABLED=true
NTFY_SERVER_URL=https://ntfy.sh
NTFY_DEFAULT_TOPIC=longbark-dev-alerts

# Invoice Ninja Configuration (optional)
INVOICE_NINJA_ENABLED=false
INVOICE_NINJA_URL=https://your-instance.invoicing.co
INVOICE_NINJA_API_TOKEN=your_token_here

# Google Search Console (optional)
GSC_ENABLED=false
```

**Generate a secure SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Start the Development Environment

```bash
# Start all services in development mode
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### 4. Create Admin User

```bash
docker-compose exec backend python -m app.scripts.create_admin
```

### 5. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

---

## Development Workflow

### Starting Development

```bash
# Start all services
docker-compose up -d

# Or start specific services
docker-compose up -d db redis backend

# Watch logs
docker-compose logs -f backend frontend
```

### Making Changes

#### Backend Changes (Python/FastAPI)

The backend uses **hot reload** in development mode, so changes to Python files will automatically restart the server.

```bash
# Watch backend logs
docker-compose logs -f backend

# Run backend commands
docker-compose exec backend python -m app.scripts.your_script

# Access Python shell
docker-compose exec backend python
```

#### Frontend Changes (React)

The frontend also uses hot reload via Vite.

```bash
# Watch frontend logs
docker-compose logs -f frontend

# Install new npm packages
docker-compose exec frontend npm install package-name

# Access frontend shell
docker-compose exec frontend sh
```

### Stopping Development

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes database data)
docker-compose down -v

# Stop and remove images
docker-compose down --rmi all
```

---

## Project Structure

```
longbark-maintenance/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── api/               # API routes
│   │   │   └── routes/        # Route handlers
│   │   ├── core/              # Core configuration
│   │   │   ├── config.py      # Settings and environment variables
│   │   │   ├── database.py    # Database connection
│   │   │   └── security.py    # Authentication & security
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # Business logic
│   │   │   ├── uptime_monitor.py
│   │   │   ├── ssl_monitor.py
│   │   │   ├── seo_monitor.py
│   │   │   └── ...
│   │   ├── tasks/             # Celery tasks
│   │   │   ├── celery_app.py
│   │   │   └── monitoring_tasks.py
│   │   ├── scripts/           # Utility scripts
│   │   └── main.py            # FastAPI application
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .dockerignore
│
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/        # Reusable React components
│   │   ├── contexts/          # React contexts
│   │   ├── pages/             # Page components
│   │   ├── services/          # API service layer
│   │   ├── App.jsx            # Main app component
│   │   └── index.jsx          # Entry point
│   ├── public/
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
│
├── docs/                       # Documentation
│   ├── CONFIGURATION.md
│   ├── DEVELOPMENT.md         # This file
│   ├── DOCKER.md
│   ├── USER_GUIDE.md
│   └── screenshots/
│
├── .github/                    # GitHub Actions workflows
│   └── workflows/
│       └── docker-build.yml
│
├── docker-compose.yml          # Development compose file
├── docker-compose.production.yml
├── .env.example
└── README.md
```

---

## Running Tests

### Backend Tests

```bash
# Run all backend tests
docker-compose exec backend pytest

# Run with coverage
docker-compose exec backend pytest --cov=app --cov-report=html

# Run specific test file
docker-compose exec backend pytest app/tests/test_auth.py

# Run specific test
docker-compose exec backend pytest app/tests/test_auth.py::test_login

# View coverage report
open backend/htmlcov/index.html  # macOS
xdg-open backend/htmlcov/index.html  # Linux
```

### Frontend Tests

```bash
# Run frontend tests (if configured)
docker-compose exec frontend npm test

# Run with coverage
docker-compose exec frontend npm test -- --coverage

# Run E2E tests (if configured)
docker-compose exec frontend npm run test:e2e
```

### Linting and Code Quality

```bash
# Backend linting
docker-compose exec backend black app/
docker-compose exec backend flake8 app/
docker-compose exec backend mypy app/

# Frontend linting
docker-compose exec frontend npm run lint
docker-compose exec frontend npm run lint:fix
```

---

## Database Management

### Database Migrations

LongBark uses SQLAlchemy for ORM. Migrations are managed with Alembic (if configured).

```bash
# Create a new migration
docker-compose exec backend alembic revision --autogenerate -m "Add new table"

# Apply migrations
docker-compose exec backend alembic upgrade head

# Rollback migration
docker-compose exec backend alembic downgrade -1

# View migration history
docker-compose exec backend alembic history

# View current revision
docker-compose exec backend alembic current
```

### Database Console

```bash
# Access PostgreSQL console
docker-compose exec db psql -U longbark -d longbark

# Useful PostgreSQL commands:
# \dt              - List tables
# \d table_name    - Describe table
# \q               - Quit
```

### Database Backup and Restore

```bash
# Backup database
docker-compose exec db pg_dump -U longbark longbark > backup.sql

# Restore database
cat backup.sql | docker-compose exec -T db psql -U longbark longbark

# Copy database to another instance
docker-compose exec db pg_dump -U longbark longbark | \
  docker-compose exec -T db psql -U longbark new_database
```

### Resetting the Database

```bash
# WARNING: This will delete all data!
docker-compose down -v
docker-compose up -d db
docker-compose exec backend alembic upgrade head
docker-compose exec backend python -m app.scripts.create_admin
```

---

## API Development

### Creating New API Endpoints

1. **Define the model** (`backend/app/models/`)

```python
# backend/app/models/feature.py
from sqlalchemy import Column, Integer, String, DateTime
from app.core.database import Base

class Feature(Base):
    __tablename__ = "features"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    created_at = Column(DateTime)
```

2. **Define the schema** (`backend/app/schemas/`)

```python
# backend/app/schemas/feature.py
from pydantic import BaseModel
from datetime import datetime

class FeatureBase(BaseModel):
    name: str
    description: str | None = None

class FeatureCreate(FeatureBase):
    pass

class Feature(FeatureBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
```

3. **Create the route** (`backend/app/api/routes/`)

```python
# backend/app/api/routes/features.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.feature import Feature, FeatureCreate
from app.models.feature import Feature as FeatureModel

router = APIRouter()

@router.post("/", response_model=Feature)
def create_feature(feature: FeatureCreate, db: Session = Depends(get_db)):
    db_feature = FeatureModel(**feature.dict())
    db.add(db_feature)
    db.commit()
    db.refresh(db_feature)
    return db_feature

@router.get("/{feature_id}", response_model=Feature)
def get_feature(feature_id: int, db: Session = Depends(get_db)):
    feature = db.query(FeatureModel).filter(FeatureModel.id == feature_id).first()
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")
    return feature
```

4. **Register the router** (`backend/app/main.py`)

```python
from app.api.routes import features

app.include_router(features.router, prefix="/api/v1/features", tags=["features"])
```

### Testing API Endpoints

**Interactive API Documentation:**
- Visit http://localhost:8000/docs
- Try out endpoints directly in the browser

**Using curl:**
```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin@longbark.com", "password": "your_password"}'

# Use the token from login
export TOKEN="your_jwt_token_here"

# Make authenticated request
curl -X GET http://localhost:8000/api/v1/sites \
  -H "Authorization: Bearer $TOKEN"
```

---

## Frontend Development

### Project Structure

```
frontend/src/
├── components/          # Reusable UI components
│   ├── Header.jsx
│   ├── StatCard.jsx
│   ├── SiteCard.jsx
│   └── ...
├── contexts/           # React Context providers
│   └── AuthContext.jsx
├── pages/              # Page components (routes)
│   ├── Dashboard.jsx
│   ├── Sites.jsx
│   ├── SiteDetail.jsx
│   ├── Alerts.jsx
│   └── Login.jsx
├── services/           # API service layer
│   └── api.js
├── App.jsx             # Main app component & routing
├── index.jsx           # Entry point
└── index.css           # Global styles (Tailwind)
```

### Creating New Components

```jsx
// frontend/src/components/MyComponent.jsx
import React from 'react';

export default function MyComponent({ title, data }) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold mb-4">{title}</h2>
      <div className="space-y-2">
        {data.map((item, index) => (
          <div key={index}>{item}</div>
        ))}
      </div>
    </div>
  );
}
```

### Adding New Pages

1. **Create the page component**

```jsx
// frontend/src/pages/NewPage.jsx
import React, { useState, useEffect } from 'react';
import api from '../services/api';
import Header from '../components/Header';

export default function NewPage() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const response = await api.get('/api/v1/endpoint');
      setData(response.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="max-w-7xl mx-auto py-6 px-4">
        <h1 className="text-2xl font-bold mb-6">New Page</h1>
        {/* Your content here */}
      </div>
    </div>
  );
}
```

2. **Add route to App.jsx**

```jsx
// frontend/src/App.jsx
import NewPage from './pages/NewPage';

// Inside <Routes>
<Route path="/new-page" element={<ProtectedRoute><NewPage /></ProtectedRoute>} />
```

### Styling with Tailwind CSS

Tailwind is configured and ready to use:

```jsx
<div className="bg-blue-500 text-white p-4 rounded-lg shadow-md hover:bg-blue-600">
  Styled with Tailwind
</div>
```

Customize Tailwind in `frontend/tailwind.config.js`.

---

## Debugging

### Backend Debugging

**View logs:**
```bash
docker-compose logs -f backend
```

**Interactive debugging with pdb:**
```python
# Add to your Python code
import pdb; pdb.set_trace()

# Then attach to running container
docker attach $(docker-compose ps -q backend)
```

**VS Code debugging:**

Create `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Remote Attach",
      "type": "python",
      "request": "attach",
      "connect": {
        "host": "localhost",
        "port": 5678
      },
      "pathMappings": [
        {
          "localRoot": "${workspaceFolder}/backend",
          "remoteRoot": "/app"
        }
      ]
    }
  ]
}
```

### Frontend Debugging

**Browser DevTools:**
- Chrome/Firefox DevTools (F12)
- React DevTools extension

**Console logging:**
```javascript
console.log('Debug info:', data);
console.error('Error:', error);
```

**Network requests:**
- Open Network tab in DevTools
- Monitor API calls and responses

---

## Contributing

### Git Workflow

1. **Create a feature branch:**
```bash
git checkout -b feature/my-new-feature
```

2. **Make your changes and commit:**
```bash
git add .
git commit -m "Add new feature: description"
```

3. **Push to remote:**
```bash
git push origin feature/my-new-feature
```

4. **Create a Pull Request:**
- Go to GitHub repository
- Click "New Pull Request"
- Select your branch
- Fill in the PR template
- Request review

### Code Style Guidelines

**Python (Backend):**
- Follow [PEP 8](https://pep8.org/)
- Use `black` for formatting: `black app/`
- Use type hints where possible
- Write docstrings for functions

**JavaScript (Frontend):**
- Use ES6+ features
- Use functional components with hooks
- Follow React best practices
- Use meaningful variable names

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Example:**
```
feat(monitoring): Add SSL certificate expiry checking

- Implement SSL certificate monitoring service
- Add expiry date checking and alerting
- Create database model for SSL certificates
- Add API endpoints for SSL data

Closes #123
```

---

## Troubleshooting

### Common Issues

**1. Port already in use**
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 PID

# Or change port in docker-compose.yml
```

**2. Database connection errors**
```bash
# Check if database is running
docker-compose ps db

# Restart database
docker-compose restart db

# Check database logs
docker-compose logs db
```

**3. Frontend not updating**
```bash
# Clear npm cache and rebuild
docker-compose exec frontend npm cache clean --force
docker-compose restart frontend
```

**4. Module not found errors**
```bash
# Backend
docker-compose exec backend pip install -r requirements.txt

# Frontend
docker-compose exec frontend npm install
```

**5. Permission denied errors**
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
```

---

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Celery Documentation](https://docs.celeryq.dev/)

---

## Getting Help

- Check the [User Guide](USER_GUIDE.md)
- Review [Configuration Guide](CONFIGURATION.md)
- Search existing [GitHub Issues](https://github.com/sugarfunk/longbark-maintenance/issues)
- Contact the development team

---

**Happy coding! 🚀**
