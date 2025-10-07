#!/bin/bash

set -e

echo "🚀 MediaRouter Setup"
echo "===================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo "Please install Docker from https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    echo "Please install Docker Compose from https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✓${NC} Docker is installed"

# Create .env file if it doesn't exist
if [ ! -f backend/.env ]; then
    echo -e "${BLUE}Creating backend/.env file...${NC}"
    cp backend/.env.example backend/.env

    # Generate random encryption key
    ENCRYPTION_KEY=$(openssl rand -hex 32)
    SECRET_KEY=$(openssl rand -hex 32)

    # Update .env with generated keys
    sed -i.bak "s/your-secret-encryption-key-here-change-this/$ENCRYPTION_KEY/g" backend/.env
    sed -i.bak "s/your-secret-key-here-change-this/$SECRET_KEY/g" backend/.env
    rm backend/.env.bak

    echo -e "${GREEN}✓${NC} Created backend/.env with secure keys"
fi

# Create storage directories
echo -e "${BLUE}Creating storage directories...${NC}"
mkdir -p storage/videos storage/temp
echo -e "${GREEN}✓${NC} Storage directories created"

# Pull and start containers
echo -e "${BLUE}Pulling pre-built Docker images...${NC}"
docker compose pull

echo -e "${BLUE}Starting services...${NC}"
docker compose up -d

echo ""
echo -e "${GREEN}✅ MediaRouter is starting!${NC}"
echo ""
echo "Backend API: http://localhost:3001"
echo "Frontend UI: http://localhost:3000"
echo "API Docs: http://localhost:3001/docs"
echo ""
echo "Waiting for services to be ready..."

# Wait for backend to be ready
for i in {1..30}; do
    if curl -s http://localhost:3001/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Backend is ready!"
        break
    fi
    sleep 1
done

# Wait for frontend to be ready
for i in {1..30}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Frontend is ready!"
        break
    fi
    sleep 1
done

echo ""
echo -e "${GREEN}🎉 Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Open http://localhost:3000 in your browser"
echo "2. Go to Settings and add your API keys"
echo "3. Start generating videos in the Playground!"
echo ""
echo "To stop: docker compose down"
echo "To view logs: docker compose logs -f"
