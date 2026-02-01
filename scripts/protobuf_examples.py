"""
Example: Using Protocol Buffers with the Library API

This script demonstrates how to make requests using Protocol Buffers
instead of JSON for better performance.
"""

import requests
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_service.config.settings')

import django
django.setup()

from library_service.apps.core.proto_generated import library_pb2

# API Configuration
API_URL = "http://localhost:8000/api/v1"
TOKEN = "your-auth-token-here"  # Replace with actual token

def example_json_request():
    """Standard JSON request (existing behavior)"""
    print("\n" + "="*60)
    print("EXAMPLE 1: JSON Request (Default)")
    print("="*60)
    
    response = requests.get(
        f"{API_URL}/members/",
        headers={
            "Accept": "application/json",
            "Authorization": f"Token {TOKEN}"
        }
    )
    
    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    print(f"Size: {len(response.content)} bytes")
    print(f"Data: {response.json()}")


def example_protobuf_request():
    """Protocol Buffer request (new high-performance option)"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Protocol Buffer Request")
    print("="*60)
    
    response = requests.get(
        f"{API_URL}/members/",
        headers={
            "Accept": "application/x-protobuf",
            "Authorization": f"Token {TOKEN}"
        }
    )
    
    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    print(f"Size: {len(response.content)} bytes")
    
    # Decode protobuf response
    member_list = library_pb2.MemberList()
    member_list.ParseFromString(response.content)
    
    print(f"Count: {member_list.count}")
    print(f"Members:")
    for member in member_list.results:
        print(f"  - {member.full_name} ({member.email})")


def example_protobuf_post():
    """Create a new member using Protocol Buffer"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Protocol Buffer POST Request")
    print("="*60)
    
    # Create member data
    new_member = library_pb2.Member()
    new_member.first_name = "Jane"
    new_member.last_name = "Doe"
    new_member.email = "jane.doe@example.com"
    new_member.phone = "555-9999"
    new_member.membership_status = "active"
    new_member.join_date = "2024-02-01"
    
    # Serialize to binary
    binary_data = new_member.SerializeToString()
    
    response = requests.post(
        f"{API_URL}/members/",
        data=binary_data,
        headers={
            "Content-Type": "application/x-protobuf",
            "Accept": "application/x-protobuf",
            "Authorization": f"Token {TOKEN}"
        }
    )
    
    print(f"Status: {response.status_code}")
    print(f"Size: {len(response.content)} bytes")
    
    # Decode response
    created_member = library_pb2.Member()
    created_member.ParseFromString(response.content)
    
    print(f"Created: {created_member.full_name} (ID: {created_member.id})")


def compare_performance():
    """Compare JSON vs Protobuf performance"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Performance Comparison")
    print("="*60)
    
    import time
    
    # JSON request
    start = time.time()
    json_response = requests.get(
        f"{API_URL}/members/",
        headers={"Accept": "application/json", "Authorization": f"Token {TOKEN}"}
    )
    json_time = (time.time() - start) * 1000  # Convert to ms
    json_size = len(json_response.content)
    
    # Protobuf request
    start = time.time()
    pb_response = requests.get(
        f"{API_URL}/members/",
        headers={"Accept": "application/x-protobuf", "Authorization": f"Token {TOKEN}"}
    )
    pb_time = (time.time() - start) * 1000  # Convert to ms
    pb_size = len(pb_response.content)
    
    print(f"\nJSON:")
    print(f"  Size: {json_size} bytes")
    print(f"  Time: {json_time:.2f}ms")
    
    print(f"\nProtobuf:")
    print(f"  Size: {pb_size} bytes")
    print(f"  Time: {pb_time:.2f}ms")
    
    print(f"\nImprovement:")
    print(f"  Size reduction: {(1 - pb_size/json_size)*100:.1f}%")
    print(f"  Speed improvement: {(1 - pb_time/json_time)*100:.1f}%")


def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("PROTOCOL BUFFERS API EXAMPLES")
    print("="*60)
    print("\nNote: Make sure the backend server is running:")
    print("  cd backend && python manage.py runserver")
    print("\nAnd you have a valid auth token.")
    print("Get token by logging in via API or Django admin.")
    
    try:
        # Uncomment to run examples
        # example_json_request()
        # example_protobuf_request()
        # example_protobuf_post()
        # compare_performance()
        
        print("\n" + "="*60)
        print("Examples ready to run!")
        print("="*60)
        print("\nTo use:")
        print("1. Update TOKEN variable with your auth token")
        print("2. Uncomment the example functions in main()")
        print("3. Run: python scripts/protobuf_examples.py")
        
    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure:")
        print("1. Backend server is running (python manage.py runserver)")
        print("2. You have a valid authentication token")
        print("3. The token is set in the TOKEN variable")


if __name__ == '__main__':
    main()
