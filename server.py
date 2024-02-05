import http.server
import socketserver

# Set the port you want to use
PORT = 8000

# Create a basic HTTP server with a custom handler
Handler = http.server.SimpleHTTPRequestHandler

# Use a socket server to listen on the specified port
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving at port {PORT}")

    # Start the server, it will run until you stop the script
    httpd.serve_forever()
