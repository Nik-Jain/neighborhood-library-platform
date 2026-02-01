#!/bin/bash
# Quick start script for Neighborhood Library Platform
# This script automates the deployment process for development/demo environments

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'  # No Color

# Configuration
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"
API_PORT="${API_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-3000}"

# Functions
print_banner() {
    echo ""
    echo -e "${BLUE}╔═══════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  🚀  Neighborhood Library Platform Starter  🚀   ║${NC}"
    echo -e "${BLUE}╚═══════════════════════════════════════════════════╝${NC}"
    echo ""
}

check_prerequisites() {
    echo -e "${YELLOW}📋 Checking prerequisites...${NC}"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}✗ Docker is not installed${NC}"
        echo "Please install Docker from: https://docs.docker.com/get-docker/"
        exit 1
    fi
    echo -e "${GREEN}✓ Docker is installed: $(docker --version)${NC}"
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}✗ Docker Compose is not installed${NC}"
        echo "Please install Docker Compose from: https://docs.docker.com/compose/install/"
        exit 1
    fi
    echo -e "${GREEN}✓ Docker Compose is installed: $(docker-compose --version)${NC}"
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        echo -e "${RED}✗ Docker daemon is not running${NC}"
        echo "Please start Docker and try again"
        exit 1
    fi
    echo -e "${GREEN}✓ Docker daemon is running${NC}"
}

setup_environment() {
    echo ""
    echo -e "${YELLOW}⚙️  Setting up environment configuration...${NC}"
    
    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}Creating .env file from example...${NC}"
        cp .env.example .env
        echo -e "${GREEN}✓ .env file created${NC}"
        echo -e "${YELLOW}⚠️  Please review .env file and update values for production use${NC}"
    else
        echo -e "${GREEN}✓ .env file already exists${NC}"
    fi
}

start_services() {
    echo ""
    echo -e "${YELLOW}🐳 Building and starting Docker services...${NC}"
    
    # Stop any existing containers
    docker-compose -f "$COMPOSE_FILE" down 2>/dev/null || true
    
    # Build and start services
    docker-compose -f "$COMPOSE_FILE" up -d --build
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Services started successfully${NC}"
    else
        echo -e "${RED}✗ Failed to start services${NC}"
        exit 1
    fi
}

wait_for_services() {
    echo ""
    echo -e "${YELLOW}⏳ Waiting for services to be healthy...${NC}"
    
    # Wait for PostgreSQL
    echo -e "${YELLOW}Waiting for PostgreSQL...${NC}"
    RETRIES=30
    until docker-compose exec -T postgres pg_isready -U postgres &>/dev/null || [ $RETRIES -eq 0 ]; do
        echo -n "."
        RETRIES=$((RETRIES-1))
        sleep 1
    done
    
    if [ $RETRIES -eq 0 ]; then
        echo -e "\n${RED}✗ PostgreSQL failed to start${NC}"
        docker-compose logs postgres
        exit 1
    fi
    echo -e "\n${GREEN}✓ PostgreSQL is ready${NC}"
    
    # Wait for API
    echo -e "${YELLOW}Waiting for API server...${NC}"
    RETRIES=30
    until curl -sf http://localhost:${API_PORT}/api/health/ &>/dev/null || [ $RETRIES -eq 0 ]; do
        echo -n "."
        RETRIES=$((RETRIES-1))
        sleep 2
    done
    
    if [ $RETRIES -eq 0 ]; then
        echo -e "\n${YELLOW}⚠️  API health check timeout (might still be starting)${NC}"
    else
        echo -e "\n${GREEN}✓ API server is ready${NC}"
    fi
}

setup_database() {
    echo ""
    echo -e "${YELLOW}🗄️  Setting up database...${NC}"
    
    # Run migrations (already done in docker-compose command, but ensure it's complete)
    echo -e "${YELLOW}Running database migrations...${NC}"
    if docker-compose exec -T api python manage.py migrate --noinput; then
        echo -e "${GREEN}✓ Migrations completed${NC}"
    else
        echo -e "${RED}✗ Migrations failed${NC}"
        exit 1
    fi
    
    # Bootstrap roles
    echo -e "${YELLOW}Bootstrapping user roles...${NC}"
    if docker-compose exec -T api python manage.py bootstrap_roles; then
        echo -e "${GREEN}✓ Roles created${NC}"
    else
        echo -e "${YELLOW}⚠️  Roles may already exist${NC}"
    fi
    
    # Create superuser
    echo -e "${YELLOW}Creating superuser account...${NC}"
    docker-compose exec -T api python manage.py shell << 'END' 2>/dev/null || echo -e "${YELLOW}⚠️  Superuser may already exist${NC}"
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    user = User.objects.create_superuser(
        username='admin',
        email='admin@library.local',
        password='admin123',
        first_name='Admin',
        last_name='User'
    )
    print('Superuser created successfully')
else:
    print('Superuser already exists')
END
    
    # Seed database with sample data
    echo -e "${YELLOW}Seeding database with sample data...${NC}"
    if docker-compose exec -T api python manage.py seed_database 2>/dev/null; then
        echo -e "${GREEN}✓ Sample data loaded${NC}"
    else
        echo -e "${YELLOW}⚠️  Sample data may already exist or command unavailable${NC}"
    fi
}

print_summary() {
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║           ✅  Setup Completed Successfully!       ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}📍 Access Points:${NC}"
    echo -e "  ${GREEN}Frontend Application:${NC}  http://localhost:${FRONTEND_PORT}"
    echo -e "  ${GREEN}API Backend:${NC}           http://localhost:${API_PORT}/api/v1"
    echo -e "  ${GREEN}API Documentation:${NC}     http://localhost:${API_PORT}/api/schema/swagger-ui/"
    echo -e "  ${GREEN}Admin Panel:${NC}           http://localhost:${API_PORT}/admin/"
    echo -e "  ${GREEN}API Health:${NC}            http://localhost:${API_PORT}/api/health/"
    echo ""
    echo -e "${BLUE}🔐 Default Credentials:${NC}"
    echo -e "  ${YELLOW}Username:${NC} admin"
    echo -e "  ${YELLOW}Password:${NC} admin123"
    echo -e "  ${RED}⚠️  CHANGE THESE CREDENTIALS IN PRODUCTION!${NC}"
    echo ""
    echo -e "${BLUE}📝 Useful Commands:${NC}"
    echo -e "  ${GREEN}View all logs:${NC}         docker-compose logs -f"
    echo -e "  ${GREEN}View API logs:${NC}         docker-compose logs -f api"
    echo -e "  ${GREEN}Check status:${NC}          docker-compose ps"
    echo -e "  ${GREEN}Stop services:${NC}         docker-compose down"
    echo -e "  ${GREEN}Restart services:${NC}      docker-compose restart"
    echo -e "  ${GREEN}Reset everything:${NC}      docker-compose down -v && ./start.sh"
    echo ""
    echo -e "${BLUE}📚 Documentation:${NC}"
    echo -e "  ${GREEN}README:${NC}                cat README.md"
    echo -e "  ${GREEN}Deployment Guide:${NC}      cat DEPLOYMENT.md"
    echo -e "  ${GREEN}Quick Reference:${NC}       cat QUICK_REFERENCE.md"
    echo ""
}

# Main execution
main() {
    print_banner
    check_prerequisites
    setup_environment
    start_services
    wait_for_services
    setup_database
    print_summary
}

# Run main function
main
