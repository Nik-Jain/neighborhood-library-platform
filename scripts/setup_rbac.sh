#!/bin/bash
# Script to run RBAC migrations, bootstrap, and tests

set -e

echo "========================================="
echo "RBAC Implementation - Setup & Test"
echo "========================================="
echo ""

# Check if running in Docker
if [ -f /.dockerenv ]; then
    echo "Running in Docker container..."
    PYTHON_CMD="python"
else
    echo "Running locally, checking for Docker..."
    if docker-compose ps | grep -q "library_api"; then
        echo "Using Docker Compose..."
        PYTHON_CMD="docker-compose exec -T api python"
    else
        echo "Docker not running. Please start with: docker-compose up -d"
        echo "Or run this script inside the container."
        exit 1
    fi
fi

echo ""
echo "Step 1: Creating migrations for APIToken model..."
$PYTHON_CMD manage.py makemigrations

echo ""
echo "Step 2: Running migrations..."
$PYTHON_CMD manage.py migrate

echo ""
echo "Step 3: Bootstrapping RBAC roles and admin user..."
$PYTHON_CMD manage.py bootstrap_roles --username admin --email admin@library.local --password admin123

echo ""
echo "Step 4: Running RBAC permission tests..."
$PYTHON_CMD manage.py test library_service.apps.core.tests_permissions -v 2

echo ""
echo "Step 5: Running RBAC integration tests..."
$PYTHON_CMD manage.py test library_service.apps.core.tests_rbac_integration -v 2

echo ""
echo "========================================="
echo "RBAC Implementation Complete!"
echo "========================================="
echo ""
echo "Summary:"
echo "  - APIToken model created"
echo "  - Groups created: ADMIN, LIBRARIAN, MEMBER"
echo "  - Admin user created with ADMIN role"
echo "  - All existing Members synced to Users with MEMBER role"
echo "  - Permissions applied to viewsets"
echo "  - Tests passed"
echo ""
echo "Next steps:"
echo "  1. Test authentication: POST http://localhost:8000/api/v1/auth/login/"
echo "  2. Use returned token: Authorization: Token <your-token>"
echo "  3. Test role-based endpoints"
echo ""
