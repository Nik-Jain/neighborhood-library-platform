#!/bin/bash
# Database initialization script

# This script initializes the PostgreSQL database with necessary tables and initial data

set -e

echo "Creating database and user..."

# Create extensions
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE EXTENSION IF NOT EXISTS uuid-ossp;
EOSQL

echo "Database initialized successfully!"
