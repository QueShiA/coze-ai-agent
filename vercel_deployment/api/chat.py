"""
Coze 智能体 API - Vercel Serverless 版本
"""

from flask import Flask, request, jsonify
import requests
import json
import time
import os

app = Flask(__name__)

# 从环境变量读取配置
COZE_API_TOKEN = os.getenv('COZE_API_TOKEN', 'pat_noXbOTkJd7dYRN7P3kzoX7VzMhlcgO5mO9VlMWHDQDvn0rRPkeWv8jCl9YIfNlWB')
BOT_ID = os.getenv('BOT_ID', '7529840362341515291')
API_BASE = "https://api.coze.cn"

CHAT_API = f"{API_BASE}/v3/chat"
RETRIEVE_API = f"{API_BASE}/v3/chat/retrieve"
MESSAGE_LIST_API = f"{API_BASE}/v3/chat/message/list"


def handle_chat(user_message, user_id):
    """处理对话逻辑"""
    
    headers = {
        'Authorization': f'Bearer {COZE_API_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    # 发起对话
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
    
    response = requests.post(CHAT_API, headers=headers, json=payload, timeout=30)
    
    if response.status_code != 200:
        return {
            'error': f'发起对话失败: {response.status_code}',
            'details': response.text
        }, response.status_code
    
    result = response.json()
    
    if result.get('code') != 0:
        return {
            'error': result.get('msg', '未知错误'),
            'details': result
        }, 400
    
    data_obj = result.get('data', {})
    conversation_id = data_obj.get('conversation_id')
    chat_id = data_obj.get('id')
    
    if not conversation_id or not chat_id:
        return {
            'error': '无法获取对话ID',
            'details': result
        }, 400
    
    # 轮询等待完成
    max_attempts = 60
    attempt = 0
    
    while attempt < max_attempts:
        time.sleep(1)
        attempt += 1
        
        retrieve_url = f"{RETRIEVE_API}?conversation_id={conversation_id}&chat_id={chat_id}"
        status_response = requests.get(retrieve_url, headers=headers, timeout=10)
        
        if status_response.status_code == 200:
            status_data = status_response.json()
            
            if status_data.get('code') != 0:
                continue
            
            status_obj = status_data.get('data', {})
            status = status_obj.get('status')
            
            if status == 'completed':
                break
            elif status == 'failed':
                error = status_obj.get('last_error', {})
                return {
                    'error': '智能体对话失败',
                    'details': error
                }, 500
    
    if attempt >= max_attempts:
        return {'error': '等待回复超时'}, 504
    
    # 获取消息列表
    message_url = f"{MESSAGE_LIST_API}?conversation_id={conversation_id}&chat_id={chat_id}"
    message_response = requests.get(message_url, headers=headers, timeout=10)
    
    if message_response.status_code != 200:
        return {
            'error': f'获取消息失败: {message_response.status_code}',
            'details': message_response.text
        }, message_response.status_code
    
    message_result = message_response.json()
    
    if message_result.get('code') != 0:
        return {
            'error': message_result.get('msg'),
            'details': message_result
        }, 400
    
    return {
        'success': True,
        'data': message_result.get('data', message_result),
        'conversation_id': conversation_id,
        'chat_id': chat_id
    }, 200


@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    """对话端点"""
    
    # 处理 CORS 预检请求
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    try:
        data = request.json
        user_message = data.get('message', '')
        user_id = data.get('user_id', 'default_user')
        
        if not user_message:
            response = jsonify({'error': '消息不能为空'})
            response.status_code = 400
        else:
            result, status_code = handle_chat(user_message, user_id)
            response = jsonify(result)
            response.status_code = status_code
        
        # 添加 CORS 头
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response
        
    except Exception as e:
        response = jsonify({'error': f'服务器错误: {str(e)}'})
        response.status_code = 500
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response


@app.route('/api/health', methods=['GET'])
def health():
    """健康检查"""
    response = jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'bot_id': BOT_ID[:10] + '...',
        'api_base': API_BASE
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


# Vercel 需要这个导出
def handler(request, context):
    """Vercel Serverless 函数入口"""
    return app(request.environ, context)


if __name__ == '__main__':
    # 本地开发
    app.run(host='0.0.0.0', port=5000, debug=True)
