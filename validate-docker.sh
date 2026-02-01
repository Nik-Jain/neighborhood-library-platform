#!/bin/bash
# Docker Configuration Validation Script
# Run this before deploying to ensure all configurations are correct

set -e

echo "🔍 Validating Docker Configuration..."
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ERRORS=0
WARNINGS=0

# Check if Docker is installed
echo "✓ Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker is not installed${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✓ Docker is installed: $(docker --version)${NC}"
fi

# Check if Docker Compose is installed
echo "✓ Checking Docker Compose installation..."
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}✗ Docker Compose is not installed${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✓ Docker Compose is installed: $(docker-compose --version)${NC}"
fi

# Check if .env file exists
echo "✓ Checking .env file..."
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠ .env file not found. Creating from .env.example...${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ .env created from template${NC}"
        echo -e "${YELLOW}⚠ Please update .env with your configuration!${NC}"
        WARNINGS=$((WARNINGS + 1))
    else
        echo -e "${RED}✗ .env.example not found${NC}"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${GREEN}✓ .env file exists${NC}"
fi

# Check required environment variables
echo "✓ Checking required environment variables..."
source .env 2>/dev/null || true

check_var() {
    local var_name=$1
    local var_value=${!var_name}
    local is_secret=$2
    
    if [ -z "$var_value" ]; then
        echo -e "${RED}✗ $var_name is not set${NC}"
        ERRORS=$((ERRORS + 1))
        return 1
    fi
    
    # Check for insecure defaults
    if [ "$is_secret" = "true" ]; then
        case "$var_value" in
            *"insecure"*|*"dev-key"*|*"change"*|*"example"*|"postgres"|"admin123")
                echo -e "${YELLOW}⚠ $var_name uses default/insecure value${NC}"
                WARNINGS=$((WARNINGS + 1))
                ;;
            *)
                echo -e "${GREEN}✓ $var_name is set${NC}"
                ;;
        esac
    else
        echo -e "${GREEN}✓ $var_name is set${NC}"
    fi
}

check_var "SECRET_KEY" "true"
check_var "DB_PASSWORD" "true"
check_var "ALLOWED_HOSTS" "false"

# Check if DEBUG is disabled for production
if [ "${DEBUG:-False}" = "True" ]; then
    echo -e "${YELLOW}⚠ DEBUG is enabled. Disable for production!${NC}"
    WARNINGS=$((WARNINGS + 1))
else
    echo -e "${GREEN}✓ DEBUG is disabled${NC}"
fi

# Validate docker-compose.yml
echo "✓ Validating docker-compose.yml..."
if docker-compose config > /dev/null 2>&1; then
    echo -e "${GREEN}✓ docker-compose.yml is valid${NC}"
else
    echo -e "${RED}✗ docker-compose.yml has errors${NC}"
    docker-compose config
    ERRORS=$((ERRORS + 1))
fi

# Check required files
echo "✓ Checking required files..."
FILES=(
    "Dockerfile"
    "frontend/Dockerfile"
    "requirements.txt"
    "frontend/package.json"
    "nginx.conf"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓ $file exists${NC}"
    else
        echo -e "${RED}✗ $file not found${NC}"
        ERRORS=$((ERRORS + 1))
    fi
done

# Check .dockerignore files
echo "✓ Checking .dockerignore files..."
if [ -f ".dockerignore" ]; then
    echo -e "${GREEN}✓ Root .dockerignore exists${NC}"
else
    echo -e "${YELLOW}⚠ Root .dockerignore not found${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

if [ -f "frontend/.dockerignore" ]; then
    echo -e "${GREEN}✓ Frontend .dockerignore exists${NC}"
else
    echo -e "${YELLOW}⚠ Frontend .dockerignore not found${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# Check port availability
echo "✓ Checking port availability..."
check_port() {
    local port=$1
    local service=$2
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠ Port $port ($service) is already in use${NC}"
        WARNINGS=$((WARNINGS + 1))
    else
        echo -e "${GREEN}✓ Port $port ($service) is available${NC}"
    fi
}

check_port 8000 "API"
check_port 3000 "Frontend"
check_port 5432 "PostgreSQL"
check_port 80 "Nginx"

# Summary
echo ""
echo "=================================="
echo "Validation Summary"
echo "=================================="

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed! Ready to deploy.${NC}"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ $WARNINGS warning(s) found${NC}"
    echo -e "${YELLOW}Review warnings before deploying to production${NC}"
    exit 0
else
    echo -e "${RED}✗ $ERRORS error(s) found${NC}"
    [ $WARNINGS -gt 0 ] && echo -e "${YELLOW}⚠ $WARNINGS warning(s) found${NC}"
    echo -e "${RED}Fix errors before deploying${NC}"
    exit 1
fi
