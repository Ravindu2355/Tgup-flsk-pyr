import http.server
import socketserver

PORT = 8000

class MyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # Send response status code
        self.send_response(200)

        # Send headers
        self.send_header("Content-type", "text/html")
        self.end_headers()

        # Write the message
        self.wfile.write(b"Hello, World!")

# Set up the server
with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()

