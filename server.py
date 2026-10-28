"""
QuantPulse AI - Quantitative Stock Market Assistant
Lightweight Zero-Dependency Local Server
"""

import http.server
import socketserver
import webbrowser
import os
import sys

PORT = 3000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        # Enable CORS and disable aggressive caching for smooth demo iterations
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

def main():
    os.chdir(DIRECTORY)
    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        url = f"http://localhost:{PORT}/index.html"
        print("=" * 65)
        print("⚡ QuantPulse AI - Stock Market Sense Platform Server Started")
        print(f"📡 Serving dashboard at: {url}")
        print("📈 Open this URL in your browser or double click index.html")
        print("⌨️  Press Ctrl+C to stop the server")
        print("=" * 65)
        
        try:
            webbrowser.open(url)
        except Exception:
            pass

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down QuantPulse AI server. Good luck with your presentation!")
            httpd.server_close()

if __name__ == '__main__':
    main()
