from http.server import BaseHTTPRequestHandler
import json
import os
import requests
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests - proxy to Django backend"""
        try:
            # Get the Django API URL from environment
            django_api_url = os.environ.get('DJANGO_API_URL', 'http://localhost:8000')
            
            # Parse the request path
            parsed_path = urlparse(self.path)
            api_path = parsed_path.path
            
            # Forward the request to Django backend
            response = requests.get(f"{django_api_url}{api_path}")
            
            # Set response headers
            self.send_response(response.status_code)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.end_headers()
            
            # Send response
            self.wfile.write(response.content)
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_response = {
                'error': 'Internal server error',
                'message': str(e)
            }
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_POST(self):
        """Handle POST requests - proxy to Django backend"""
        try:
            # Get the Django API URL from environment
            django_api_url = os.environ.get('DJANGO_API_URL', 'http://localhost:8000')
            
            # Parse the request path
            parsed_path = urlparse(self.path)
            api_path = parsed_path.path
            
            # Get request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            # Get content type
            content_type = self.headers.get('Content-Type', 'application/json')
            
            # Forward the request to Django backend
            headers = {'Content-Type': content_type}
            response = requests.post(
                f"{django_api_url}{api_path}",
                data=post_data,
                headers=headers
            )
            
            # Set response headers
            self.send_response(response.status_code)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.end_headers()
            
            # Send response
            self.wfile.write(response.content)
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_response = {
                'error': 'Internal server error',
                'message': str(e)
            }
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        self.wfile.write(b'')
