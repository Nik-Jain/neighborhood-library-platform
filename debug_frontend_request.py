#!/usr/bin/env python
"""
Debug what the frontend is ACTUALLY sending when it tries protobuf
"""
import os
import sys
import django
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_service.config.settings')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
django.setup()

# Create a mock server to capture raw requests
class RequestCaptureHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        print(f"\n{'='*60}")
        print("CAPTURED REQUEST")
        print(f"{'='*60}")
        print(f"Method: {self.command}")
        print(f"Path: {self.path}")
        print(f"Headers:")
        for header, value in self.headers.items():
            print(f"  {header}: {value}")
        print(f"\nBody ({len(body)} bytes):")
        print(f"  Hex: {body.hex()}")
        print(f"  Raw: {body[:100]}")
        print(f"  Looks like: ", end="")
        
        # Try to detect format
        if body.startswith(b'{'):
            print("JSON")
        elif body.startswith(b'['):
            print("JSON Array")
        elif len(body) < 20:
            print("Binary (likely protobuf)")
        else:
            print("Unknown")
        
        # Send response
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"ok": true}')
    
    def log_message(self, format, *args):
        pass  # Suppress default logging

def start_mock_server():
    server = HTTPServer(('127.0.0.1', 8888), RequestCaptureHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    return server

if __name__ == '__main__':
    print("Starting mock server on http://127.0.0.1:8888")
    print("Open this URL in browser: http://127.0.0.1:8888/test")
    print("\nOr make a request like:")
    print("  curl -X POST http://127.0.0.1:8888/api/v1/auth/login/ \\")
    print("    -H 'Content-Type: application/x-protobuf' \\")
    print("    --data-binary @data.bin")
    
    server = start_mock_server()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()
