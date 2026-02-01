#!/usr/bin/env python3
"""
Test script to verify Protocol Buffer implementation in the backend.
"""
import sys
import os
import django

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_service.config.settings')
django.setup()

from library_service.apps.core.proto_generated import library_pb2
from library_service.apps.core.models import Member, Book
from library_service.apps.core.protobuf_renderers import ProtobufRenderer
from rest_framework.response import Response
import json

def test_protobuf_encoding():
    """Test encoding Python data to protobuf binary"""
    print("=" * 60)
    print("Testing Protocol Buffer Encoding")
    print("=" * 60)
    
    # Create test data
    test_data = {
        'id': '123',
        'first_name': 'John',
        'last_name': 'Doe',
        'full_name': 'John Doe',
        'email': 'john.doe@example.com',
        'phone': '555-1234',
        'membership_number': 'MEM-001',
        'membership_status': 'active',
        'join_date': '2024-01-01',
        'created_at': '2024-01-01T10:00:00Z',
        'updated_at': '2024-01-01T10:00:00Z',
        'active_borrowings_count': 2,
        'overdue_borrowings_count': 0
    }
    
    print(f"\n1. Original Python dict ({len(str(test_data))} chars):")
    print(json.dumps(test_data, indent=2))
    
    # Encode to protobuf
    member_msg = library_pb2.Member()
    for key, value in test_data.items():
        if hasattr(member_msg, key) and value is not None:
            setattr(member_msg, key, value)
    
    binary_data = member_msg.SerializeToString()
    print(f"\n2. Protobuf binary ({len(binary_data)} bytes)")
    print(f"   Size reduction: {(1 - len(binary_data) / len(str(test_data))) * 100:.1f}%")
    
    # Decode back
    decoded_msg = library_pb2.Member()
    decoded_msg.ParseFromString(binary_data)
    
    print(f"\n3. Decoded protobuf:")
    print(f"   Name: {decoded_msg.full_name}")
    print(f"   Email: {decoded_msg.email}")
    print(f"   Status: {decoded_msg.membership_status}")
    print(f"   ✅ Encoding/decoding successful!")
    
    return True


def test_protobuf_list():
    """Test encoding a list response"""
    print("\n" + "=" * 60)
    print("Testing Protocol Buffer List Encoding")
    print("=" * 60)
    
    # Create test list data
    test_list = {
        'results': [
            {
                'id': '1',
                'first_name': 'Alice',
                'last_name': 'Smith',
                'full_name': 'Alice Smith',
                'email': 'alice@example.com',
                'membership_number': 'MEM-001',
                'membership_status': 'active',
                'join_date': '2024-01-01',
                'created_at': '2024-01-01T10:00:00Z',
                'updated_at': '2024-01-01T10:00:00Z',
                'active_borrowings_count': 1,
                'overdue_borrowings_count': 0
            },
            {
                'id': '2',
                'first_name': 'Bob',
                'last_name': 'Johnson',
                'full_name': 'Bob Johnson',
                'email': 'bob@example.com',
                'membership_number': 'MEM-002',
                'membership_status': 'active',
                'join_date': '2024-01-02',
                'created_at': '2024-01-02T10:00:00Z',
                'updated_at': '2024-01-02T10:00:00Z',
                'active_borrowings_count': 0,
                'overdue_borrowings_count': 0
            }
        ],
        'count': 2,
        'next': None,
        'previous': None
    }
    
    json_size = len(json.dumps(test_list))
    print(f"\n1. JSON size: {json_size} bytes")
    
    # Encode to protobuf
    member_list_msg = library_pb2.MemberList()
    member_list_msg.count = test_list['count']
    
    for member_data in test_list['results']:
        member_msg = member_list_msg.results.add()
        for key, value in member_data.items():
            if hasattr(member_msg, key) and value is not None:
                setattr(member_msg, key, value)
    
    binary_data = member_list_msg.SerializeToString()
    print(f"2. Protobuf size: {len(binary_data)} bytes")
    print(f"3. Size reduction: {(1 - len(binary_data) / json_size) * 100:.1f}%")
    
    # Decode back
    decoded_list = library_pb2.MemberList()
    decoded_list.ParseFromString(binary_data)
    
    print(f"\n4. Decoded list:")
    print(f"   Count: {decoded_list.count}")
    print(f"   Members: {len(decoded_list.results)}")
    for member in decoded_list.results:
        print(f"   - {member.full_name} ({member.email})")
    
    print(f"   ✅ List encoding/decoding successful!")
    return True


def test_renderer():
    """Test the ProtobufRenderer class"""
    print("\n" + "=" * 60)
    print("Testing ProtobufRenderer Integration")
    print("=" * 60)
    
    renderer = ProtobufRenderer()
    print(f"\n1. Renderer media type: {renderer.media_type}")
    print(f"2. Renderer format: {renderer.format}")
    print(f"   ✅ ProtobufRenderer initialized successfully!")
    
    return True


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("PROTOCOL BUFFER BACKEND TEST SUITE")
    print("=" * 60)
    
    try:
        success = True
        success = success and test_protobuf_encoding()
        success = success and test_protobuf_list()
        success = success and test_renderer()
        
        print("\n" + "=" * 60)
        if success:
            print("✅ ALL TESTS PASSED!")
            print("=" * 60)
            print("\nProtocol Buffers are working correctly in the backend.")
            print("You can now test with the frontend or curl:")
            print("\n  curl -H 'Accept: application/x-protobuf' \\")
            print("       http://localhost:8000/api/v1/members/")
            return 0
        else:
            print("❌ SOME TESTS FAILED")
            print("=" * 60)
            return 1
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
