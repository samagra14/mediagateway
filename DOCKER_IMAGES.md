# Docker Images Guide

## Quick Start with Pre-built Images

MediaRouter provides pre-built Docker images for instant deployment with zero build time.

### One-Line Setup

```bash
curl -sSL https://raw.githubusercontent.com/samagra14/mediarouter/main/setup.sh | bash
```

Or clone and run:

```bash
git clone https://github.com/samagra14/mediarouter.git
cd mediarouter
./setup.sh
```

The setup script automatically:
1. Pulls pre-built images from GitHub Container Registry
2. Generates encryption keys
3. Creates storage directories
4. Starts all services

**Time to value: ~30 seconds** (just image pull time, no builds!)

## Available Images

### Production Images (GitHub Container Registry)

```bash
# Latest stable release
ghcr.io/samagra14/mediarouter-backend:latest
ghcr.io/samagra14/mediarouter-frontend:latest

# Specific version
ghcr.io/samagra14/mediarouter-backend:v1.0.0
ghcr.io/samagra14/mediarouter-frontend:v1.0.0

# Main branch (bleeding edge)
ghcr.io/samagra14/mediarouter-backend:main
ghcr.io/samagra14/mediarouter-frontend:main
```

### Platform Support

All images support multiple architectures:
- **linux/amd64** - Intel/AMD processors
- **linux/arm64** - Apple Silicon (M1/M2/M3), ARM servers

Docker automatically pulls the correct architecture for your system.

## Usage

### Using Pre-built Images (Default)

The default `docker-compose.yml` uses pre-built images:

```bash
# Pull latest images
docker compose pull

# Start services
docker compose up -d

# Update to latest
docker compose pull && docker compose up -d
```

### Building Locally (Development)

If you want to build from source:

```bash
# Use local development compose file
docker compose -f docker-compose.local.yml up --build

# Or modify docker-compose.yml:
# Uncomment the "build:" lines
# Comment out the "image:" lines
docker compose build
docker compose up -d
```

## Image Tags

### Tagging Strategy

- `latest` - Latest stable release from main branch
- `v1.0.0` - Specific semantic version (created from git tags)
- `v1.0` - Major.minor version (tracks latest patch)
- `v1` - Major version (tracks latest minor/patch)
- `main` - Latest commit to main branch (may be unstable)

### Using Specific Versions

Edit `docker-compose.yml` to pin versions:

```yaml
services:
  backend:
    image: ghcr.io/samagra14/mediarouter-backend:v1.0.0
    # ...

  frontend:
    image: ghcr.io/samagra14/mediarouter-frontend:v1.0.0
    # ...
```

## Building and Publishing (Maintainers)

### Automatic Builds

GitHub Actions automatically builds and publishes images:

**Triggers:**
- Push to `main` branch → builds `latest` and `main` tags
- Create git tag `v*` → builds version tags (`v1.0.0`, `v1.0`, `v1`)
- Pull requests → builds but doesn't push (validation only)

### Manual Build and Push

```bash
# Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Build and push backend
cd backend
docker buildx build --platform linux/amd64,linux/arm64 \
  -t ghcr.io/samagra14/mediarouter-backend:latest \
  --push .

# Build and push frontend
cd frontend
docker buildx build --platform linux/amd64,linux/arm64 \
  -t ghcr.io/samagra14/mediarouter-frontend:latest \
  --push .
```

### Creating a Release

1. Update version in relevant files
2. Commit changes
3. Create and push git tag:

```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

4. GitHub Actions automatically builds and publishes versioned images

## Image Details

### Backend Image

**Base:** `python:3.11-slim`

**Size:** ~350MB (compressed)

**Contents:**
- FastAPI application
- Python dependencies
- SQLite database support
- HTTPX for async HTTP requests

**Exposed Ports:**
- `3001` - HTTP API

### Frontend Image

**Base:** `node:20-alpine` (build stage) + `nginx:alpine` (runtime)

**Size:** ~50MB (compressed)

**Contents:**
- Static React build
- Nginx web server
- Production-optimized

**Exposed Ports:**
- `3000` - HTTP web interface

## Configuration

### Environment Variables

Set via `backend/.env` or docker-compose environment:

```yaml
environment:
  - DATABASE_URL=sqlite:////app/storage/db.sqlite
  - STORAGE_PATH=/app/storage/videos
  - PORT=3001
  - CORS_ORIGINS=http://localhost:3000
```

### Volume Mounts

```yaml
volumes:
  - ./storage:/app/storage              # Video and database storage
  - ./backend/.env:/app/.env            # Environment config
```

## Troubleshooting

### Image Pull Fails

```bash
# Check connectivity
docker pull ghcr.io/samagra14/mediarouter-backend:latest

# If private, login first
echo $GITHUB_TOKEN | docker login ghcr.io -u samagra14 --password-stdin
```

### Wrong Architecture

```bash
# Check your platform
docker version | grep "OS/Arch"

# Force specific platform (not recommended)
docker pull --platform linux/amd64 ghcr.io/samagra14/mediarouter-backend:latest
```

### Image Updates Not Pulling

```bash
# Force pull latest
docker compose pull --ignore-pull-failures

# Remove old images
docker compose down
docker image prune -a

# Fresh start
docker compose pull
docker compose up -d
```

### Build Cache Issues (Local Builds)

```bash
# Clear build cache
docker builder prune -a

# Build without cache
docker compose -f docker-compose.local.yml build --no-cache
```

## Performance

### First Run

- **With pre-built images:** ~30s (image pull only)
- **Building from source:** ~5-10min (full build)

### Subsequent Starts

- **Start time:** ~5-10s (containers already exist)
- **Update time:** ~20s (pull new images)

### Image Sizes

| Component | Compressed | Uncompressed |
|-----------|-----------|--------------|
| Backend | ~350 MB | ~800 MB |
| Frontend | ~50 MB | ~150 MB |
| **Total** | **~400 MB** | **~950 MB** |

## Security

### Image Scanning

Images are automatically scanned for vulnerabilities:
- GitHub Advanced Security (if enabled)
- Regular base image updates
- Minimal dependencies

### Using Private Images

Make images private in GitHub:

1. Go to package settings
2. Change visibility to private
3. Users need GitHub token to pull:

```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
docker compose pull
```

## Advanced Usage

### Multi-stage Builds

Both Dockerfiles use multi-stage builds for optimization:

**Backend:**
```dockerfile
FROM python:3.11-slim
# Single stage (already minimal)
```

**Frontend:**
```dockerfile
FROM node:20-alpine AS builder  # Build stage
FROM nginx:alpine               # Runtime stage (smaller)
```

### Custom Base Images

To use custom base images, fork and modify:

```dockerfile
# backend/Dockerfile
FROM your-custom-python:3.11
# ...
```

Then build locally:
```bash
docker compose -f docker-compose.local.yml build
```

## Support

For issues with Docker images:
- Check logs: `docker compose logs`
- Report issues: https://github.com/samagra14/mediarouter/issues
- Include: OS, Docker version, error messages

## Related Documentation

- [README.md](README.md) - Main project documentation
- [CLAUDE.md](CLAUDE.md) - Development guide
- [.github/workflows/docker-build.yml](.github/workflows/docker-build.yml) - CI/CD workflow
