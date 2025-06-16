#!/usr/bin/env python3
"""
Simple HTTP server to serve the HTML client
This avoids CORS issues when opening HTML files directly
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

# Change to the project directory
project_dir = Path(__file__).parent
os.chdir(project_dir)

PORT = 8080
DIRECTORY = "src/client"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def main():
    print(f"Starting HTTP server on port {PORT}")
    print(f"Serving files from: {DIRECTORY}")
    print(f"HTML Client available at: http://localhost:{PORT}/NewGUIforClient.html")
    print("Press Ctrl+C to stop")
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped")

if __name__ == "__main__":
    main()
