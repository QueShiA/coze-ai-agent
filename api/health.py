"""
健康检查端点
"""

from http.server import BaseHTTPRequestHandler
import json
import time
import os


class handler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        """处理健康检查请求"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            'status': 'healthy',
            'timestamp': time.time(),
            'bot_id': os.getenv('BOT_ID', '7529840362341515291')[:10] + '...',
            'api_base': 'https://api.coze.cn'
        }
        
        self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        """处理 CORS 预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
