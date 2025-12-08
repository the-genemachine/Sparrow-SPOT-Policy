#!/usr/bin/env python3
"""
Investigation Results Server
Simple HTTP server for browsing investigation index.html files
Serves from the parent directory where investigation folders are stored
"""

import os
import sys
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import webbrowser


def main():
    """Start HTTP server for investigation results"""
    
    # Get port from argument or use default
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    
    # Get directory to serve - defaults to current directory
    serve_dir = sys.argv[2] if len(sys.argv) > 2 else os.getcwd()
    serve_path = Path(serve_dir)
    
    if not serve_path.exists():
        print(f"❌ Directory not found: {serve_path}")
        sys.exit(1)
    
    # Change to serve directory
    os.chdir(serve_path)
    
    # Create and start server
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    
    url = f"http://localhost:{port}"
    print(f"""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║   📋 Investigation Results Server                         ║
║   Sparrow SPOT Scale™ v8.6.1                              ║
║                                                            ║
║   🌐 Server: {url:<36} ║
║   📁 Serving: {str(serve_path)[-32:]:<36} ║
║                                                            ║
║   Available investigations:                               ║
""")
    
    # List investigation folders
    for item in sorted(serve_path.iterdir()):
        if item.is_dir() and (item / 'index.html').exists():
            print(f"║     • {item.name:<49} ║")
    
    print(f"""║                                                            ║
║   Press Ctrl+C to stop the server                         ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
""")
    
    # Try to open browser
    try:
        webbrowser.open(url)
    except:
        print(f"⚠️  Could not open browser. Visit: {url}")
    
    # Start server
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n✋ Server stopped.")
        sys.exit(0)


if __name__ == '__main__':
    main()
