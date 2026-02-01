#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

API_URL="http://localhost:8000/api/v1"

echo -e "${YELLOW}=== Testing Authentication Endpoints ===${NC}\n"

# Test 1: Signup
echo -e "${YELLOW}[Test 1] Signup${NC}"
SIGNUP_RESPONSE=$(curl -s -X POST "$API_URL/auth/signup/" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!"
  }')

echo "$SIGNUP_RESPONSE" | grep -q "token" && echo -e "${GREEN}✓ Signup endpoint works${NC}" || echo -e "${RED}✗ Signup endpoint failed${NC}"
echo "Response: $SIGNUP_RESPONSE\n"

# Test 2: Login
echo -e "${YELLOW}[Test 2] Login${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@example.com",
    "password": "SecurePass123!"
  }')

TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"token":"[^"]*' | cut -d'"' -f4)
echo "$LOGIN_RESPONSE" | grep -q "token" && echo -e "${GREEN}✓ Login endpoint works${NC}" || echo -e "${RED}✗ Login endpoint failed${NC}"
echo "Response: $LOGIN_RESPONSE\n"

# Test 3: Check Current User
if [ ! -z "$TOKEN" ]; then
  echo -e "${YELLOW}[Test 3] Get Current User${NC}"
  CURRENT_USER=$(curl -s -X GET "$API_URL/auth/user/" \
    -H "Authorization: Token $TOKEN")
  
  echo "$CURRENT_USER" | grep -q "authenticated" && echo -e "${GREEN}✓ Current user endpoint works${NC}" || echo -e "${RED}✗ Current user endpoint failed${NC}"
  echo "Response: $CURRENT_USER\n"
fi

# Test 4: Test with admin credentials
echo -e "${YELLOW}[Test 4] Login with Admin Credentials${NC}"
ADMIN_LOGIN=$(curl -s -X POST "$API_URL/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@library.local",
    "password": "admin123"
  }')

echo "$ADMIN_LOGIN" | grep -q "token" && echo -e "${GREEN}✓ Admin login works${NC}" || echo -e "${RED}✗ Admin login failed${NC}"
echo "Response: $ADMIN_LOGIN\n"

echo -e "${GREEN}=== Authentication Tests Complete ===${NC}"
