# LongBark Hosting Management - Frontend

A modern React frontend for the LongBark Hosting Management & SEO Tool.

## Features

- **Dashboard**: Overview of all sites, alerts, and key metrics
- **Sites Management**: Monitor and manage all your hosted sites
- **Alerts System**: Track and resolve monitoring alerts
- **Client Management**: Manage clients and their sites
- **Real-time Monitoring**: View uptime, performance, and SEO metrics
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## Tech Stack

- **React 18**: Modern React with hooks
- **Vite**: Fast build tool and dev server
- **Tailwind CSS**: Utility-first CSS framework
- **React Router**: Client-side routing
- **Recharts**: Beautiful charts and graphs
- **Axios**: HTTP client for API calls
- **React Icons**: Icon library
- **date-fns**: Date formatting

## Getting Started

### Prerequisites

- Node.js 18 or higher
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create environment file:
```bash
cp .env.example .env
```

3. Update `.env` with your API URL:
```
VITE_API_URL=http://localhost:8000/api/v1
```

### Development

Run the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

### Build for Production

Build the app:
```bash
npm run build
```

Preview the production build:
```bash
npm run preview
```

## Docker

Build the Docker image:
```bash
docker build -t longbark-frontend .
```

Run the container:
```bash
docker run -p 80:80 longbark-frontend
```

## Project Structure

```
frontend/
├── src/
│   ├── components/      # Reusable UI components
│   ├── contexts/        # React contexts (Auth, etc.)
│   ├── pages/          # Page components
│   ├── services/       # API services
│   ├── App.jsx         # Main app component
│   ├── index.jsx       # Entry point
│   └── index.css       # Global styles
├── public/             # Static assets
├── Dockerfile          # Docker configuration
├── nginx.conf          # Nginx configuration for production
├── package.json        # Dependencies and scripts
└── vite.config.js      # Vite configuration
```

## Default Credentials

- **Username**: admin
- **Password**: admin123

## API Integration

The frontend communicates with the backend API at the URL specified in `VITE_API_URL`. All API calls include JWT authentication tokens stored in localStorage.

## Features Overview

### Dashboard
- Total sites count
- Active alerts count
- Average uptime percentage
- Sites status summary
- Recent alerts

### Sites
- List all sites with search and filters
- View site details with tabs:
  - Overview: Basic site information
  - Uptime: Historical uptime data with charts
  - Performance: Response time metrics
  - SEO: SEO-related metrics
  - Alerts: Site-specific alerts
- Add new sites

### Alerts
- View all alerts with filters (status, severity, type)
- Acknowledge and resolve alerts
- Bulk actions
- Color-coded by severity

### Clients
- List all clients
- View client details
- View sites per client
- Link to Invoice Ninja

## License

MIT
