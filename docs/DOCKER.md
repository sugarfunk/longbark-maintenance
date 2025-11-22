# Docker Deployment Guide

## Using Pre-built Images from GitHub Container Registry

LongBark Hosting Management automatically builds and publishes Docker images to GitHub Container Registry (GHCR) on every commit to the main branch and on version tags.

### Available Images

- **Frontend**: `ghcr.io/sugarfunk/longbark-maintenance-frontend:latest`
- **Backend**: `ghcr.io/sugarfunk/longbark-maintenance-backend:latest`

### Pulling Images

#### Public Repository
If the repository is public, you can pull images directly:

```bash
docker pull ghcr.io/sugarfunk/longbark-maintenance-frontend:latest
docker pull ghcr.io/sugarfunk/longbark-maintenance-backend:latest
```

#### Private Repository
If the repository is private, you need to authenticate first:

```bash
# Create a GitHub Personal Access Token with `read:packages` permission
# Then login to GHCR
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Pull the images
docker pull ghcr.io/sugarfunk/longbark-maintenance-frontend:latest
docker pull ghcr.io/sugarfunk/longbark-maintenance-backend:latest
```

### Quick Start with Pre-built Images

1. **Clone the repository** (or just download the docker-compose.production.yml file):
```bash
git clone https://github.com/sugarfunk/longbark-maintenance.git
cd longbark-maintenance
```

2. **Configure environment variables**:
```bash
cp .env.example .env
# Edit .env with your settings
```

3. **Start the application** using pre-built images:
```bash
docker-compose -f docker-compose.production.yml up -d
```

4. **Create an admin user**:
```bash
docker-compose -f docker-compose.production.yml exec backend python -m app.scripts.create_admin
```

5. **Access the application**:
- Dashboard: http://localhost
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Using Specific Versions

Images are tagged with multiple formats:

- `latest` - Latest build from main branch
- `main` - Latest build from main branch
- `v1.0.0` - Semantic version tags
- `sha-abc123` - Specific commit SHA

Examples:
```bash
# Use a specific version
docker pull ghcr.io/sugarfunk/longbark-maintenance-frontend:v1.0.0

# Use a specific commit
docker pull ghcr.io/sugarfunk/longbark-maintenance-backend:sha-abc123
```

Update the image tags in `docker-compose.production.yml`:
```yaml
services:
  backend:
    image: ghcr.io/sugarfunk/longbark-maintenance-backend:v1.0.0
  frontend:
    image: ghcr.io/sugarfunk/longbark-maintenance-frontend:v1.0.0
```

### Building Images Locally

If you prefer to build images locally (for development):

```bash
# Development mode with live reload
docker-compose up -d

# Build and run
docker-compose up --build -d
```

### Image Platforms

The GitHub Actions workflow builds multi-platform images for:
- `linux/amd64` (x86_64)
- `linux/arm64` (ARM64, Apple Silicon)

Docker will automatically pull the correct image for your platform.

### Updating to Latest Version

```bash
# Pull latest images
docker-compose -f docker-compose.production.yml pull

# Restart services with new images
docker-compose -f docker-compose.production.yml up -d
```

### Troubleshooting

#### Authentication Issues
If you get authentication errors when pulling images:

1. Ensure your GitHub token has `read:packages` permission
2. Login to GHCR: `echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin`
3. For organization repositories, ensure you have appropriate access

#### Image Not Found
If the image doesn't exist yet:

1. Check the [Actions tab](https://github.com/sugarfunk/longbark-maintenance/actions) to see if builds are running
2. Builds are triggered on push to main or on tags
3. First time setup may require manually triggering the workflow

#### Permission Denied
If you see "permission denied" errors:

1. Ensure the repository's Actions have permission to write packages
2. Go to Settings → Actions → General → Workflow permissions
3. Enable "Read and write permissions"

### CI/CD Workflow

The workflow (`.github/workflows/docker-build.yml`) automatically:

1. Builds images on every push to main
2. Builds images on pull requests (but doesn't push them)
3. Tags images with version on git tags (e.g., `v1.0.0`)
4. Uses Docker layer caching to speed up builds
5. Builds multi-platform images (amd64, arm64)

### Manual Workflow Trigger

You can manually trigger the build workflow:

1. Go to Actions tab in GitHub
2. Select "Build and Push Docker Images"
3. Click "Run workflow"
4. Select the branch and click "Run workflow"
