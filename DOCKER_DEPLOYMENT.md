# HiLabs Docker Deployment Guide

## 🚀 Quick Start

### Prerequisites
- Docker installed (version 20.10 or higher)
- Docker Compose installed (version 1.29 or higher)
- At least 4GB of available RAM
- 10GB of free disk space

### One-Command Deployment

```bash
# Clone the repository (if not already done)
git clone https://github.com/yourusername/HiLabs-AIQuest.git
cd HiLabs-AIQuest

# Build and start all services
docker-compose up -d --build

# Check if services are running
docker-compose ps
```

Your application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📁 Project Structure

```
HiLabs-AIQuest/
├── Backend/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── api.py
│   ├── requirements.txt
│   └── ...
├── hilabs-dash/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── nginx.conf
│   ├── package.json
│   └── ...
├── docker-compose.yml         # Production configuration
├── docker-compose.dev.yml     # Development configuration
└── .env.example              # Environment variables template
```

## 🔧 Configuration

### Environment Variables

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` to customize your deployment:
```env
BACKEND_PORT=8000
FRONTEND_PORT=3000
REACT_APP_API_URL=http://localhost:8000
```

## 🏗️ Build Commands

### Production Build
```bash
# Build and start in production mode
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

### Development Build
```bash
# Use development configuration with hot-reload
docker-compose -f docker-compose.dev.yml up --build

# Run in background
docker-compose -f docker-compose.dev.yml up -d --build
```

## 🔍 Service Management

### Check Service Status
```bash
# View running containers
docker-compose ps

# Check service health
docker-compose exec backend curl http://localhost:8000/health
docker-compose exec frontend wget -qO- http://localhost:80
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Access Container Shell
```bash
# Backend shell
docker-compose exec backend bash

# Frontend shell
docker-compose exec frontend sh
```

## 📊 Data Persistence

Data is persisted in Docker volumes:
- `uploads/` - Uploaded contract files
- `results/` - Processing results
- `debug/` - Debug information

### Backup Data
```bash
# Create backup directory
mkdir -p backups

# Backup uploads
docker run --rm -v hilabs-aiquest_uploads:/data -v $(pwd)/backups:/backup alpine tar czf /backup/uploads_$(date +%Y%m%d).tar.gz -C /data .

# Backup results
docker run --rm -v hilabs-aiquest_results:/data -v $(pwd)/backups:/backup alpine tar czf /backup/results_$(date +%Y%m%d).tar.gz -C /data .
```

### Restore Data
```bash
# Restore uploads
docker run --rm -v hilabs-aiquest_uploads:/data -v $(pwd)/backups:/backup alpine tar xzf /backup/uploads_YYYYMMDD.tar.gz -C /data

# Restore results  
docker run --rm -v hilabs-aiquest_results:/data -v $(pwd)/backups:/backup alpine tar xzf /backup/results_YYYYMMDD.tar.gz -C /data
```

## 🚨 Troubleshooting

### Common Issues and Solutions

#### 1. Port Already in Use
```bash
# Error: bind: address already in use
# Solution: Change ports in .env or docker-compose.yml
BACKEND_PORT=8001
FRONTEND_PORT=3001
```

#### 2. Out of Memory
```bash
# Increase Docker memory limit
# Docker Desktop: Settings > Resources > Memory
# Recommended: 4GB minimum
```

#### 3. Build Failures
```bash
# Clean rebuild
docker-compose down -v
docker system prune -af
docker-compose up --build
```

#### 4. Tesseract OCR Issues
```bash
# Verify Tesseract is installed in container
docker-compose exec backend tesseract --version

# Check environment variable
docker-compose exec backend env | grep TESSERACT
```

#### 5. Network Connectivity Issues
```bash
# Recreate network
docker network rm hilabs-network
docker-compose up -d
```

## 🔐 Security Considerations

1. **Environment Variables**: Never commit `.env` files with sensitive data
2. **Ports**: Consider using a reverse proxy (nginx/traefik) for production
3. **HTTPS**: Add SSL certificates for production deployment
4. **File Uploads**: Configure maximum file sizes in environment variables

## 📈 Scaling

### Horizontal Scaling
```yaml
# In docker-compose.yml, add replicas
services:
  backend:
    deploy:
      replicas: 3
```

### Resource Limits
```yaml
# Add to service definition
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
```

## 🐛 Debugging

### Enable Debug Mode
```bash
# Set in .env
DEBUG=true

# Or in docker-compose
environment:
  - DEBUG=true
```

### Interactive Debugging
```bash
# Run container with shell
docker-compose run --rm backend bash

# Test API endpoints
docker-compose exec backend python -c "from api import app; print(app.routes)"
```

## 🚀 Deployment to Cloud

### AWS ECS
```bash
# Build and push to ECR
docker build -t hilabs-backend ./Backend
docker tag hilabs-backend:latest $ECR_URI/hilabs-backend:latest
docker push $ECR_URI/hilabs-backend:latest
```

### Docker Hub
```bash
# Tag and push
docker tag hilabs-backend:latest yourusername/hilabs-backend:latest
docker push yourusername/hilabs-backend:latest
```

### Kubernetes
```yaml
# Create deployment from docker-compose
kompose convert -f docker-compose.yml
kubectl apply -f .
```

## 📝 Maintenance

### Regular Updates
```bash
# Pull latest changes
git pull origin main

# Rebuild containers
docker-compose down
docker-compose up -d --build
```

### Clean Up
```bash
# Remove unused images
docker image prune -af

# Remove unused volumes
docker volume prune -f

# Complete cleanup
docker system prune -af --volumes
```

## 🆘 Support

For issues or questions:
1. Check container logs: `docker-compose logs`
2. Verify service health: `docker-compose ps`
3. Review this documentation
4. Open an issue on GitHub

## ✅ Health Checks

Both services include health checks:
- **Backend**: http://localhost:8000/health
- **Frontend**: http://localhost:3000

Monitor with:
```bash
# Continuous health monitoring
watch -n 5 'docker-compose ps'
```

## 📊 Performance Optimization

1. **Build Cache**: Use `.dockerignore` to exclude unnecessary files
2. **Layer Caching**: Order Dockerfile commands from least to most frequently changed
3. **Multi-stage Builds**: Frontend uses multi-stage build for smaller image
4. **Volume Mounts**: Use for development, avoid in production for better performance

---

## Quick Reference Commands

```bash
# Start all services
docker-compose up -d --build

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Restart a service
docker-compose restart backend

# Execute command in container
docker-compose exec backend python manage.py migrate

# Clean everything
docker-compose down -v && docker system prune -af
```

**Note**: For production deployment, always use the production `docker-compose.yml` and ensure proper security measures are in place.
