"""
Coze 智能体 API - Vercel Serverless 版本
修复版：使用 Vercel Python Serverless Functions
"""

from http.server import BaseHTTPRequestHandler
import json
import urllib.request
import urllib.error
import time
import os


class handler(BaseHTTPRequestHandler):
    
    def _set_cors_headers(self):
        """设置 CORS 头"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    def do_OPTIONS(self):
        """处理 CORS 预检请求"""
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()
    
    def do_POST(self):
        """处理 POST 请求"""
        if self.path == '/api/chat':
            self.handle_chat()
        else:
            self.send_error(404, 'Not Found')
    
    def do_GET(self):
        """处理 GET 请求"""
        if self.path == '/api/health':
            self.handle_health()
        else:
            self.send_error(404, 'Not Found')
    
    def handle_health(self):
        """健康检查端点"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self._set_cors_headers()
        self.end_headers()
        
        response = {
            'status': 'healthy',
            'timestamp': time.time(),
            'bot_id': os.getenv('BOT_ID', '7529840362341515291')[:10] + '...',
            'api_base': 'https://api.coze.cn'
        }
        
        self.wfile.write(json.dumps(response).encode())
    
    def handle_chat(self):
        """处理聊天请求"""
        try:
            # 读取请求体
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode())
            
            user_message = data.get('message', '')
            user_id = data.get('user_id', 'default_user')
            
            if not user_message:
                self.send_error_response(400, '消息不能为空')
                return
            
            # 调用 Coze API
            result = self.call_coze_api(user_message, user_id)
            
            # 发送成功响应
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self._set_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
            
        except json.JSONDecodeError:
            self.send_error_response(400, '无效的 JSON 格式')
        except Exception as e:
            self.send_error_response(500, f'服务器错误: {str(e)}')
    
    def send_error_response(self, code, message):
        """发送错误响应"""
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self._set_cors_headers()
        self.end_headers()
        
        error_response = {'error': message}
        self.wfile.write(json.dumps(error_response).encode())
    
    def call_coze_api(self, user_message, user_id):
        """调用 Coze API"""
        # 从环境变量读取配置
        COZE_API_TOKEN = os.getenv('COZE_API_TOKEN', 'pat_noXbOTkJd7dYRN7P3kzoX7VzMhlcgO5mO9VlMWHDQDvn0rRPkeWv8jCl9YIfNlWB')
        BOT_ID = os.getenv('BOT_ID', '7529840362341515291')
        API_BASE = "https://api.coze.cn"
        
        CHAT_API = f"{API_BASE}/v3/chat"
        RETRIEVE_API = f"{API_BASE}/v3/chat/retrieve"
        MESSAGE_LIST_API = f"{API_BASE}/v3/chat/message/list"
        
        headers = {
            'Authorization': f'Bearer {COZE_API_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        # 1. 发起对话
        payload = {
            'bot_id': BOT_ID,
            'user_id': user_id,
            'stream': False,
            'auto_save_history': True,
            'additional_messages': [
                {
                    'role': 'user',
                    'content': user_message,
                    'content_type': 'text'
                }
            ]
        }
        
        req = urllib.request.Request(
            CHAT_API,
            data=json.dumps(payload).encode(),
            headers=headers,
            method='POST'
        )
        
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            raise Exception(f'发起对话失败: {e.code}')
        
        if result.get('code') != 0:
            raise Exception(result.get('msg', '未知错误'))
        
        data_obj = result.get('data', {})
        conversation_id = data_obj.get('conversation_id')
        chat_id = data_obj.get('id')
        
        if not conversation_id or not chat_id:
            raise Exception('无法获取对话ID')
        
        # 2. 轮询等待完成
        max_attempts = 60
        for attempt in range(max_attempts):
            time.sleep(1)
            
            retrieve_url = f"{RETRIEVE_API}?conversation_id={conversation_id}&chat_id={chat_id}"
            req = urllib.request.Request(retrieve_url, headers=headers)
            
            try:
                with urllib.request.urlopen(req, timeout=10) as response:
                    status_data = json.loads(response.read().decode())
            except:
                continue
            
            if status_data.get('code') != 0:
                continue
            
            status_obj = status_data.get('data', {})
            status = status_obj.get('status')
            
            if status == 'completed':
                break
            elif status == 'failed':
                error = status_obj.get('last_error', {})
                raise Exception(f"智能体对话失败: {error}")
        
        if attempt >= max_attempts - 1:
            raise Exception('等待回复超时')
        
        # 3. 获取消息列表
        message_url = f"{MESSAGE_LIST_API}?conversation_id={conversation_id}&chat_id={chat_id}"
        req = urllib.request.Request(message_url, headers=headers)
        
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                message_result = json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            raise Exception(f'获取消息失败: {e.code}')
        
        if message_result.get('code') != 0:
            raise Exception(message_result.get('msg', '获取消息失败'))
        
        return {
            'success': True,
            'data': message_result.get('data', message_result),
            'conversation_id': conversation_id,
            'chat_id': chat_id
        }
