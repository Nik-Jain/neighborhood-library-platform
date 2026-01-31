#!/bin/bash
# Database seed script - populates the database with sample data

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Running database seed script...${NC}"

# Change to backend directory
cd "$(dirname "$0")/../backend"

# Run Django seed command
python manage.py seed_database

echo -e "${GREEN}Database seeding completed successfully!${NC}"
