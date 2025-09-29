#!/bin/bash

# Docker Deployment Test Script
# This script tests that all Docker services are working correctly

echo "========================================="
echo "HiLabs Docker Deployment Test"
echo "========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
echo "1. Checking Docker installation..."
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓ Docker is installed${NC}"
    docker --version
else
    echo -e "${RED}✗ Docker is not installed${NC}"
    exit 1
fi

echo ""

# Check if Docker Compose is installed
echo "2. Checking Docker Compose installation..."
if command -v docker-compose &> /dev/null; then
    echo -e "${GREEN}✓ Docker Compose is installed${NC}"
    docker-compose --version
else
    echo -e "${RED}✗ Docker Compose is not installed${NC}"
    exit 1
fi

echo ""

# Build Docker images
echo "3. Building Docker images..."
echo "This may take a few minutes on first run..."
docker-compose build --quiet
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Docker images built successfully${NC}"
else
    echo -e "${RED}✗ Failed to build Docker images${NC}"
    exit 1
fi

echo ""

# Start services
echo "4. Starting services..."
docker-compose up -d
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Services started successfully${NC}"
else
    echo -e "${RED}✗ Failed to start services${NC}"
    exit 1
fi

echo ""

# Wait for services to be ready
echo "5. Waiting for services to be ready..."
sleep 10

# Check backend health
echo "6. Checking backend health..."
BACKEND_HEALTH=$(curl -s http://localhost:8000/health 2>/dev/null)
if [[ $BACKEND_HEALTH == *"healthy"* ]]; then
    echo -e "${GREEN}✓ Backend is healthy${NC}"
else
    echo -e "${YELLOW}⚠ Backend health check failed, retrying...${NC}"
    sleep 10
    BACKEND_HEALTH=$(curl -s http://localhost:8000/health 2>/dev/null)
    if [[ $BACKEND_HEALTH == *"healthy"* ]]; then
        echo -e "${GREEN}✓ Backend is healthy (after retry)${NC}"
    else
        echo -e "${RED}✗ Backend is not responding${NC}"
    fi
fi

echo ""

# Check frontend
echo "7. Checking frontend..."
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null)
if [ "$FRONTEND_STATUS" = "200" ]; then
    echo -e "${GREEN}✓ Frontend is accessible${NC}"
else
    echo -e "${YELLOW}⚠ Frontend returned status: $FRONTEND_STATUS${NC}"
fi

echo ""

# Check API documentation
echo "8. Checking API documentation..."
API_DOCS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs 2>/dev/null)
if [ "$API_DOCS" = "200" ]; then
    echo -e "${GREEN}✓ API documentation is accessible${NC}"
else
    echo -e "${YELLOW}⚠ API docs returned status: $API_DOCS${NC}"
fi

echo ""

# Display service status
echo "9. Service Status:"
docker-compose ps

echo ""
echo "========================================="
echo "Deployment Test Complete!"
echo "========================================="
echo ""
echo "Access your application at:"
echo -e "${GREEN}Frontend:${NC} http://localhost:3000"
echo -e "${GREEN}Backend API:${NC} http://localhost:8000"
echo -e "${GREEN}API Docs:${NC} http://localhost:8000/docs"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop services: docker-compose down"
echo ""
