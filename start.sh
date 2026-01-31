#!/bin/bash
# Quick start script for development

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}🚀 Starting Neighborhood Library Platform${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Docker Compose is not installed. Please install it first.${NC}"
    exit 1
fi

# Create .env if not exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file from example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ .env created${NC}"
fi

# Build and start services
echo -e "${YELLOW}Building and starting services...${NC}"
docker-compose up -d

# Wait for database
echo -e "${YELLOW}Waiting for database to be ready...${NC}"
sleep 10

# Run migrations
echo -e "${YELLOW}Running migrations...${NC}"
docker-compose exec -T api python manage.py migrate

# Create superuser (non-interactive for demo)
echo -e "${YELLOW}Creating superuser...${NC}"
docker-compose exec -T api python manage.py createsuperuser --no-input \
    --username admin --email admin@library.local 2>/dev/null || true

# Update password
docker-compose exec -T api python manage.py shell << END
from django.contrib.auth.models import User
user = User.objects.filter(username='admin').first()
if user:
    user.set_password('admin123')
    user.save()
    print("Admin password set to: admin123")
END

# Seed database
echo -e "${YELLOW}Seeding database with sample data...${NC}"
docker-compose exec -T api python manage.py seed_database

echo ""
echo -e "${GREEN}✓ Setup completed successfully!${NC}"
echo ""
echo -e "${YELLOW}Access points:${NC}"
echo -e "  ${GREEN}Frontend:${NC}       http://localhost:3000"
echo -e "  ${GREEN}API:${NC}            http://localhost:8000/api/v1"
echo -e "  ${GREEN}API Docs:${NC}       http://localhost:8000/api/docs/"
echo -e "  ${GREEN}Admin Panel:${NC}    http://localhost:8000/admin/"
echo ""
echo -e "${YELLOW}Default credentials:${NC}"
echo -e "  Username: ${GREEN}admin${NC}"
echo -e "  Password: ${GREEN}admin123${NC}"
echo ""
echo -e "${YELLOW}Useful commands:${NC}"
echo -e "  View logs:         ${GREEN}docker-compose logs -f api${NC}"
echo -e "  Stop services:     ${GREEN}docker-compose down${NC}"
echo -e "  Reset database:    ${GREEN}docker-compose down -v && docker-compose up -d${NC}"
echo ""
