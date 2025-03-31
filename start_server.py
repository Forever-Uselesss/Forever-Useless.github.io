# This script starts a simple HTTP server that serves files from the current directory.

import http.server
import socketserver

# Define the port you want to use
PORT = 8080

# Define the handler to serve files
Handler = http.server.SimpleHTTPRequestHandler

# Start the server
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving at http://localhost:{PORT}")
    httpd.serve_forever()
