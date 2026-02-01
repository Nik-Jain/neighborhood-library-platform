#!/bin/bash
# Debug Login Issues - Quick Diagnostic Script

set -e

echo "=========================================="
echo "Library Platform Login Troubleshooting"
echo "=========================================="

# Check if Django is set up
echo ""
echo "1️⃣  Checking Django setup..."
cd "$(dirname "$0")/../backend" || exit
python -c "import django; django.setup(); print('✅ Django configured')" 2>/dev/null || {
    echo "❌ Django not properly configured"
    exit 1
}

# Check database connection
echo ""
echo "2️⃣  Checking database connection..."
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_service.config.settings')
django.setup()
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute('SELECT 1')
    print('✅ Database connected')
" || {
    echo "❌ Database connection failed"
    exit 1
}

# Check if librarian account exists
echo ""
echo "3️⃣  Checking librarian account..."
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_service.config.settings')
django.setup()

from library_service.apps.core.models import Member

lib = Member.objects.filter(email='librarian1@library.local').first()
if lib:
    print(f'✅ Librarian account exists')
    print(f'   Email: {lib.email}')
    print(f'   Name: {lib.first_name} {lib.last_name}')
    print(f'   Status: {lib.membership_status}')
    
    # Test password
    pwd_check = lib.check_password('librarian123')
    print(f'   Password check: {\"✅ PASS\" if pwd_check else \"❌ FAIL\"}')
    
    if pwd_check:
        print('✅ Credentials are correct')
    else:
        print('❌ Password does not match')
else:
    print('❌ Librarian account not found')
    print('   Run: python manage.py seed_db')
    exit 1
"

# Check if server is running
echo ""
echo "4️⃣  Checking if server is running..."
if curl -s http://localhost:8000/api/health/ > /dev/null; then
    echo "✅ Server is running on http://localhost:8000"
else
    echo "❌ Server is not running"
    echo "   Start server with: python manage.py runserver"
    exit 1
fi

# Test login endpoint
echo ""
echo "5️⃣  Testing login endpoint..."
response=$(curl -s -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "librarian1@library.local", "password": "librarian123"}')

if echo "$response" | grep -q '"token"'; then
    token=$(echo "$response" | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
    echo "✅ Login successful!"
    echo "   Token: ${token:0:20}..."
else
    echo "❌ Login failed"
    echo "   Response: $response"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ All checks passed!"
echo "=========================================="
echo ""
echo "Your credentials:"
echo "  Email: librarian1@library.local"
echo "  Password: librarian123"
echo "  Token: $token"
echo ""
echo "Use this token in API requests:"
echo "  curl -H 'Authorization: Token $token' http://localhost:8000/api/v1/members/"
