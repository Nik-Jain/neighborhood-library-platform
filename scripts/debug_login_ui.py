#!/usr/bin/env python
"""
Comprehensive login debugging script.
Tests JSON, Protobuf, and Frontend scenarios.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_service.config.settings')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
django.setup()

import requests
import json
from django.contrib.auth.models import User
from library_service.apps.core.models import Member, APIToken
from library_service.apps.core.proto_generated import library_pb2
from google.protobuf.json_format import MessageToDict
import base64

BASE_URL = 'http://localhost:8000'
LOGIN_URL = f'{BASE_URL}/api/v1/auth/login/'

def test_librarian_exists():
    """Test if librarian account exists in database"""
    print("\n" + "="*60)
    print("1️⃣  CHECKING DATABASE")
    print("="*60)
    
    member = Member.objects.filter(email='librarian1@library.local').first()
    user = User.objects.filter(username=' ').first()
    
    if member:
        print(f"✅ Member found: {member.full_name}")
        print(f"   Email: {member.email}")
        print(f"   Status: {member.membership_status}")
        print(f"   Password valid: {member.check_password('librarian123')}")
    else:
        print("❌ Member NOT found")
    
    if user:
        print(f"✅ User found: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Password valid: {user.check_password('librarian123')}")
        print(f"   Groups: {list(user.groups.values_list('name', flat=True))}")
    else:
        print("❌ User NOT found")
    
    return member, user

def test_json_login():
    """Test JSON login"""
    print("\n" + "="*60)
    print("2️⃣  TESTING JSON LOGIN")
    print("="*60)
    
    payload = {
        'email': 'librarian1@library.local',
        'password': 'librarian123'
    }
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    print(f"URL: {LOGIN_URL}")
    print(f"Payload: {json.dumps(payload)}")
    print(f"Headers: {json.dumps(headers)}")
    
    try:
        response = requests.post(LOGIN_URL, json=payload, headers=headers, timeout=5)
        print(f"\nStatus: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Body: {response.text[:500]}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ JSON Login successful!")
            print(f"   Token: {data.get('token', 'N/A')[:50]}...")
            print(f"   Member: {data.get('member', {}).get('full_name', 'N/A')}")
            return True
        else:
            print(f"\n❌ JSON Login failed (Status {response.status_code})")
            if response.text:
                try:
                    print(f"   Error: {json.dumps(response.json(), indent=2)}")
                except:
                    print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Request error: {e}")
        return False

def test_protobuf_login():
    """Test Protobuf login"""
    print("\n" + "="*60)
    print("3️⃣  TESTING PROTOBUF LOGIN")
    print("="*60)
    
    # Create LoginRequest
    login_req = library_pb2.LoginRequest()
    login_req.email = 'librarian1@library.local'
    login_req.password = 'librarian123'
    
    binary_payload = login_req.SerializeToString()
    
    headers = {
        'Content-Type': 'application/x-protobuf',
        'Accept': 'application/x-protobuf'
    }
    
    print(f"URL: {LOGIN_URL}")
    print(f"Request message: LoginRequest(email='librarian1@library.local', password='librarian123')")
    print(f"Binary size: {len(binary_payload)} bytes")
    print(f"Headers: {json.dumps(headers)}")
    
    try:
        response = requests.post(LOGIN_URL, data=binary_payload, headers=headers, timeout=5)
        print(f"\nStatus: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Body size: {len(response.content)} bytes")
        
        if response.status_code == 200:
            # Try to decode response
            login_resp = library_pb2.LoginResponse()
            login_resp.ParseFromString(response.content)
            
            print(f"\n✅ Protobuf Login successful!")
            print(f"   Token: {login_resp.token[:50]}...")
            print(f"   Member: {login_resp.member.full_name}")
            return True
        else:
            print(f"\n❌ Protobuf Login failed (Status {response.status_code})")
            print(f"   Body: {response.text[:500]}")
            return False
    except Exception as e:
        print(f"❌ Request error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_frontend_scenarios():
    """Test frontend-specific scenarios"""
    print("\n" + "="*60)
    print("4️⃣  TESTING FRONTEND SCENARIOS")
    print("="*60)
    
    # Test 1: Frontend with JSON (most common)
    print("\n[A] Frontend sending JSON (default)")
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0',
    }
    
    payload = {'email': 'librarian1@library.local', 'password': 'librarian123'}
    
    try:
        response = requests.post(LOGIN_URL, json=payload, headers=headers, timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Frontend JSON login works")
        else:
            print(f"❌ Status {response.status_code}: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Frontend with Protobuf interceptor
    print("\n[B] Frontend with Protobuf interceptor")
    login_req = library_pb2.LoginRequest()
    login_req.email = 'librarian1@library.local'
    login_req.password = 'librarian123'
    
    headers = {
        'Content-Type': 'application/x-protobuf',
        'Accept': 'application/x-protobuf',
        'User-Agent': 'Mozilla/5.0',
    }
    
    try:
        response = requests.post(LOGIN_URL, data=login_req.SerializeToString(), headers=headers, timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Frontend Protobuf login works")
        else:
            print(f"❌ Status {response.status_code}: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Error: {e}")

def check_settings():
    """Check Django settings for protobuf configuration"""
    print("\n" + "="*60)
    print("5️⃣  CHECKING DJANGO SETTINGS")
    print("="*60)
    
    from django.conf import settings
    
    # Check REST framework configuration
    drf_settings = getattr(settings, 'REST_FRAMEWORK', {})
    
    print(f"\nDRF DEFAULT_RENDERER_CLASSES:")
    renderers = drf_settings.get('DEFAULT_RENDERER_CLASSES', [])
    for r in renderers:
        print(f"  - {r}")
    
    print(f"\nDRF DEFAULT_PARSER_CLASSES:")
    parsers = drf_settings.get('DEFAULT_PARSER_CLASSES', [])
    for p in parsers:
        print(f"  - {p}")
    
    # Check if protobuf classes are present
    has_protobuf_renderer = any('Protobuf' in str(r) for r in renderers)
    has_protobuf_parser = any('Protobuf' in str(p) for p in parsers)
    
    print(f"\n✅ Protobuf Renderer: {has_protobuf_renderer}")
    print(f"✅ Protobuf Parser: {has_protobuf_parser}")
    
    return has_protobuf_renderer and has_protobuf_parser

if __name__ == '__main__':
    print("\n" + "🔍 "*(20))
    print("COMPREHENSIVE LOGIN DEBUGGING")
    print("🔍 "*(20))
    
    # Run all tests
    check_settings()
    test_librarian_exists()
    json_ok = test_json_login()
    proto_ok = test_protobuf_login()
    test_frontend_scenarios()
    
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    print(f"JSON Login: {'✅ OK' if json_ok else '❌ FAILED'}")
    print(f"Protobuf Login: {'✅ OK' if proto_ok else '❌ FAILED'}")
    print("="*60)
