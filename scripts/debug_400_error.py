#!/usr/bin/env python
"""
Debug what the frontend is actually sending
"""
import os
import sys
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_service.config.settings')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
django.setup()

from django.test import Client
from django.test.utils import override_settings

# Test both content types
client = Client()

print("="*60)
print("Testing what might cause 400 error")
print("="*60)

# Test 1: Empty body
print("\n[Test 1] Empty body")
response = client.post('/api/v1/auth/login/', data='', content_type='application/json')
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# Test 2: Invalid JSON
print("\n[Test 2] Invalid JSON")
response = client.post('/api/v1/auth/login/', data='not json', content_type='application/json')
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# Test 3: Missing fields
print("\n[Test 3] Missing email field")
response = client.post('/api/v1/auth/login/', data=json.dumps({'password': 'librarian123'}), content_type='application/json')
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# Test 4: Missing password field
print("\n[Test 4] Missing password field")
response = client.post('/api/v1/auth/login/', data=json.dumps({'email': 'librarian1@library.local'}), content_type='application/json')
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# Test 5: Protobuf with wrong Content-Type
print("\n[Test 5] Sending JSON with protobuf Content-Type")
response = client.post(
    '/api/v1/auth/login/',
    data=json.dumps({'email': 'librarian1@library.local', 'password': 'librarian123'}),
    content_type='application/x-protobuf'
)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# Test 6: Correct protobuf
print("\n[Test 6] Correct protobuf binary")
from library_service.apps.core.proto_generated import library_pb2
login_req = library_pb2.LoginRequest()
login_req.email = 'librarian1@library.local'
login_req.password = 'librarian123'
response = client.post(
    '/api/v1/auth/login/',
    data=login_req.SerializeToString(),
    content_type='application/x-protobuf'
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print("✅ Protobuf works!")
else:
    print(f"Response: {response.content}")

print("\n" + "="*60)
