#!/usr/bin/env python3
"""
Detailed debug of protobuf login with server logs
"""
import os
import sys
import json

# Setup Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_service.config.settings')

import django
django.setup()

from library_service.apps.core.proto_generated import library_pb2
from library_service.apps.core.auth_views import LoginView
from library_service.apps.core.protobuf_renderers import ProtobufParser
from django.test import RequestFactory
from rest_framework.test import APIRequestFactory
import logging

logging.basicConfig(level=logging.DEBUG)

print("\n" + "="*60)
print("PROTOBUF LOGIN DEBUGGING")
print("="*60)

# Create login request message
print("\n1️⃣  Creating protobuf LoginRequest...")
login_request = library_pb2.LoginRequest()
login_request.email = "librarian1@library.local"
login_request.password = "librarian123"

binary_data = login_request.SerializeToString()
print(f"   ✅ LoginRequest created")
print(f"   Size: {len(binary_data)} bytes")
print(f"   Data (hex): {binary_data.hex()[:50]}...")

# Try to parse it back
print("\n2️⃣  Verifying binary data can be parsed...")
test_msg = library_pb2.LoginRequest()
test_msg.ParseFromString(binary_data)
print(f"   ✅ Binary data is valid")
print(f"   Email: {test_msg.email}")
print(f"   Password: {test_msg.password}")

# Test the parser
print("\n3️⃣  Testing ProtobufParser...")
factory = APIRequestFactory()
request = factory.post(
    '/api/v1/auth/login/',
    data=binary_data,
    content_type='application/x-protobuf'
)

parser = ProtobufParser()
parser_context = {
    'request': request,
    'view': LoginView()
}

try:
    parsed_data = parser.parse(request.stream, 'application/x-protobuf', parser_context)
    print(f"   ✅ Parser succeeded")
    print(f"   Parsed data: {parsed_data}")
except Exception as e:
    print(f"   ❌ Parser failed: {e}")
    import traceback
    traceback.print_exc()

# Test the LoginView directly
print("\n4️⃣  Testing LoginView directly...")
try:
    view = LoginView.as_view()
    request = factory.post(
        '/api/v1/auth/login/',
        data=binary_data,
        content_type='application/x-protobuf'
    )
    response = view(request)
    print(f"   Status: {response.status_code}")
    print(f"   Content-Type: {response.get('Content-Type', 'Not set')}")
    if hasattr(response, 'data'):
        print(f"   Data: {response.data}")
    else:
        print(f"   No data attribute")
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
