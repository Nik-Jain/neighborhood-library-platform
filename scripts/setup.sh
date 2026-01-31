#!/bin/bash
# Setup script for development environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Setting up Neighborhood Library Platform...${NC}"

# Check Python version
echo -e "${YELLOW}Checking Python version...${NC}"
python3 --version

# Create virtual environment
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Create .env file from example
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file from example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}Please update .env file with your configuration${NC}"
fi

# Create log directory
mkdir -p logs

# Run migrations
echo -e "${YELLOW}Running migrations...${NC}"
cd backend
python manage.py migrate

# Create superuser
echo -e "${YELLOW}Creating superuser...${NC}"
python manage.py createsuperuser --noinput || true

echo -e "${GREEN}Setup completed successfully!${NC}"
echo -e "${YELLOW}To start the development server, run:${NC}"
echo -e "${GREEN}cd backend && python manage.py runserver${NC}"
