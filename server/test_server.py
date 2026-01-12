#!/usr/bin/env python3
"""
Simple HTTP server for testing HTML files with the browser.
Usage: python test_server.py [port]
Default port: 8000
"""

import http.server
import socketserver
import sys
import os

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers for local testing
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()
    
    def log_message(self, format, *args):
        # Custom log format
        print(f"[{self.log_date_time_string()}] {format % args}")

def run_server(port=8000):
    handler = MyHTTPRequestHandler
    
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"🌐 테스트 서버가 시작되었습니다!")
        print(f"📡 주소: http://localhost:{port}")
        print(f"📁 제공 디렉토리: {os.getcwd()}")
        print(f"\n종료하려면 Ctrl+C를 누르세요\n")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n서버를 종료합니다.")
            httpd.shutdown()

if __name__ == "__main__":
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"잘못된 포트 번호: {sys.argv[1]}")
            sys.exit(1)
    
    run_server(port)
