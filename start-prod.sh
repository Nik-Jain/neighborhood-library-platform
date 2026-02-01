#!/bin/bash
# Production deployment script for Neighborhood Library Platform
# This script validates configuration and deploys with production settings

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
COMPOSE_FILE="docker-compose.prod.yml"
BACKUP_DIR="./backups"

print_banner() {
    echo ""
    echo -e "${BLUE}╔═══════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║      🚀  Production Deployment Script  🚀        ║${NC}"
    echo -e "${BLUE}╚═══════════════════════════════════════════════════╝${NC}"
    echo ""
}

validate_environment() {
    echo -e "${YELLOW}🔒 Validating production environment...${NC}"
    
    if [ ! -f ".env" ]; then
        echo -e "${RED}✗ .env file not found${NC}"
        echo "Please create .env from .env.example and configure it"
        exit 1
    fi
    
    # Source .env
    source .env
    
    # Check critical variables
    ERRORS=0
    
    # Check DEBUG is disabled
    if [ "${DEBUG}" = "True" ]; then
        echo -e "${RED}✗ DEBUG is enabled! Must be False for production${NC}"
        ERRORS=$((ERRORS+1))
    else
        echo -e "${GREEN}✓ DEBUG is disabled${NC}"
    fi
    
    # Check SECRET_KEY is not default
    if [[ "${SECRET_KEY}" == *"insecure"* ]] || [[ "${SECRET_KEY}" == *"change"* ]]; then
        echo -e "${RED}✗ SECRET_KEY is using default/insecure value${NC}"
        ERRORS=$((ERRORS+1))
    else
        echo -e "${GREEN}✓ SECRET_KEY is configured${NC}"
    fi
    
    # Check DB_PASSWORD is not default
    if [ "${DB_PASSWORD}" = "postgres" ]; then
        echo -e "${RED}✗ DB_PASSWORD is using default value${NC}"
        ERRORS=$((ERRORS+1))
    else
        echo -e "${GREEN}✓ DB_PASSWORD is configured${NC}"
    fi
    
    # Check ALLOWED_HOSTS is configured
    if [ -z "${ALLOWED_HOSTS}" ]; then
        echo -e "${RED}✗ ALLOWED_HOSTS is not set${NC}"
        ERRORS=$((ERRORS+1))
    else
        echo -e "${GREEN}✓ ALLOWED_HOSTS is configured${NC}"
    fi
    
    # Check superuser password is not default
    if [ "${DJANGO_SUPERUSER_PASSWORD}" = "admin123" ]; then
        echo -e "${YELLOW}⚠️  DJANGO_SUPERUSER_PASSWORD is using default value${NC}"
        echo -e "${YELLOW}   Please change it after deployment${NC}"
    fi
    
    if [ $ERRORS -gt 0 ]; then
        echo -e "\n${RED}✗ $ERRORS critical error(s) found${NC}"
        echo "Please fix the errors and try again"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Environment validation passed${NC}"
}

backup_existing() {
    if docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
        echo ""
        echo -e "${YELLOW}📦 Backing up existing data...${NC}"
        
        mkdir -p "$BACKUP_DIR"
        TIMESTAMP=$(date +%Y%m%d_%H%M%S)
        
        # Backup database
        echo -e "${YELLOW}Backing up database...${NC}"
        docker-compose exec -T postgres pg_dump -U postgres neighborhood_library > "$BACKUP_DIR/db_backup_$TIMESTAMP.sql" 2>/dev/null || true
        
        if [ -f "$BACKUP_DIR/db_backup_$TIMESTAMP.sql" ]; then
            echo -e "${GREEN}✓ Database backed up to $BACKUP_DIR/db_backup_$TIMESTAMP.sql${NC}"
        fi
    fi
}

deploy_services() {
    echo ""
    echo -e "${YELLOW}🚀 Deploying production services...${NC}"
    
    # Pull latest images if using registry
    echo -e "${YELLOW}Building images...${NC}"
    docker-compose -f "$COMPOSE_FILE" build --no-cache
    
    # Stop existing services
    echo -e "${YELLOW}Stopping existing services...${NC}"
    docker-compose -f "$COMPOSE_FILE" down
    
    # Start services
    echo -e "${YELLOW}Starting services...${NC}"
    docker-compose -f "$COMPOSE_FILE" up -d
    
    echo -e "${GREEN}✓ Services deployed${NC}"
}

wait_for_healthy() {
    echo ""
    echo -e "${YELLOW}⏳ Waiting for services to be healthy...${NC}"
    
    RETRIES=60
    while [ $RETRIES -gt 0 ]; do
        if docker-compose -f "$COMPOSE_FILE" ps | grep -q "unhealthy"; then
            echo -n "."
            RETRIES=$((RETRIES-1))
            sleep 2
        else
            break
        fi
    done
    
    if [ $RETRIES -eq 0 ]; then
        echo -e "\n${RED}✗ Services failed health check${NC}"
        docker-compose -f "$COMPOSE_FILE" ps
        docker-compose -f "$COMPOSE_FILE" logs --tail=50
        exit 1
    fi
    
    echo -e "\n${GREEN}✓ All services are healthy${NC}"
}

verify_deployment() {
    echo ""
    echo -e "${YELLOW}🔍 Verifying deployment...${NC}"
    
    # Check if services are running
    if ! docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
        echo -e "${RED}✗ Services are not running${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Services are running${NC}"
    
    # Check API health
    if curl -sf http://localhost:8000/api/health/ &>/dev/null; then
        echo -e "${GREEN}✓ API is responding${NC}"
    else
        echo -e "${RED}✗ API health check failed${NC}"
        exit 1
    fi
    
    # Check database connection
    if docker-compose -f "$COMPOSE_FILE" exec -T api python manage.py check --database default &>/dev/null; then
        echo -e "${GREEN}✓ Database connection verified${NC}"
    else
        echo -e "${RED}✗ Database connection failed${NC}"
        exit 1
    fi
}

print_summary() {
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║     ✅  Production Deployment Complete!          ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}📍 Service Status:${NC}"
    docker-compose -f "$COMPOSE_FILE" ps
    echo ""
    echo -e "${BLUE}📝 Next Steps:${NC}"
    echo -e "  1. Update DNS records to point to this server"
    echo -e "  2. Configure SSL/TLS certificates"
    echo -e "  3. Set up monitoring and alerts"
    echo -e "  4. Configure automated backups"
    echo -e "  5. Change default superuser password"
    echo ""
    echo -e "${BLUE}🔧 Management Commands:${NC}"
    echo -e "  ${GREEN}View logs:${NC}             docker-compose -f $COMPOSE_FILE logs -f"
    echo -e "  ${GREEN}Check status:${NC}          docker-compose -f $COMPOSE_FILE ps"
    echo -e "  ${GREEN}Restart services:${NC}      docker-compose -f $COMPOSE_FILE restart"
    echo -e "  ${GREEN}Stop services:${NC}         docker-compose -f $COMPOSE_FILE down"
    echo ""
    echo -e "${YELLOW}⚠️  Important Security Reminders:${NC}"
    echo -e "  - Change default admin password immediately"
    echo -e "  - Enable HTTPS with valid SSL certificates"
    echo -e "  - Set up regular database backups"
    echo -e "  - Configure firewall rules"
    echo -e "  - Enable log monitoring"
    echo ""
}

# Main execution
main() {
    print_banner
    
    # Check if validation script exists and run it
    if [ -f "./validate-docker.sh" ]; then
        echo -e "${YELLOW}Running validation script...${NC}"
        ./validate-docker.sh || exit 1
        echo ""
    fi
    
    validate_environment
    backup_existing
    deploy_services
    wait_for_healthy
    verify_deployment
    print_summary
}

# Confirm production deployment
echo -e "${YELLOW}⚠️  This will deploy in PRODUCTION mode${NC}"
echo -e "${YELLOW}Make sure you have reviewed and configured .env properly${NC}"
echo -n "Continue? (yes/no): "
read -r CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Deployment cancelled"
    exit 0
fi

main
