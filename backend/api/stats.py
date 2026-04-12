from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "total_chunks": 0,
            "unique_laws": 0,
            "status": "Running",
            "ai_model": "Gemini 1.5 Flash"
        }
        
        self.wfile.write(json.dumps(response).encode())