import requests
from flask import Flask, request, redirect, session, jsonify, render_template
import secrets
import os
import urllib.parse

APP_PORT = <Port>  # 替换为实际端口号
REDIRECT_URI = "https://auth.example.com/callback"

AUTHORIZE_URL = "https://openapi.aliyundrive.com/oauth/authorize"
TOKEN_URL = "https://openapi.aliyundrive.com/oauth/access_token" 

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', secrets.token_hex(16))


@app.route('/')
def index():
    # 从环境变量中获取客户端ID和密钥
    client_id = os.environ.get('ALIYUN_CLIENT_ID')
    client_secret = os.environ.get('ALIYUN_CLIENT_SECRET')
    return render_template('index.html', server_configured=(client_id and client_secret))


@app.route('/login')
def login():
    client_id = os.environ.get('ALIYUN_CLIENT_ID')
    client_secret = os.environ.get('ALIYUN_CLIENT_SECRET')
    if not client_id or not client_secret:
        return "错误：服务器尚未配置环境变量 ALIYUN_CLIENT_ID 和 ALIYUN_CLIENT_SECRET。", 500
    session['client_id'] = client_id
    session['client_secret'] = client_secret
    params = {
        'client_id': client_id,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        'scope': 'user:base,file:all:read,file:all:write'
    }
    auth_url = f"{AUTHORIZE_URL}?{urllib.parse.urlencode(params)}"
    return redirect(auth_url)


@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return render_template('result.html', error="授权失败：未能从阿里云盘获取到授权码(code)。")
    client_id = session.get('client_id')
    client_secret = session.get('client_secret')
    if not client_id or not client_secret:
        return render_template('result.html', error="授权会话已过期或凭证丢失，请返回首页重试。")
    token_data = { 'grant_type': 'authorization_code', 'code': code, 'client_id': client_id, 'client_secret': client_secret }
    try:
        response = requests.post(TOKEN_URL, json=token_data, timeout=20)
        response.raise_for_status()
        token_info = response.json()
        refresh_token = token_info.get('refresh_token')
        if not refresh_token:
            return render_template('result.html', error=f"获取refresh_token失败，阿里云返回：{response.text}")
        session.clear()
        return render_template('result.html', refresh_token=refresh_token)
    except requests.exceptions.RequestException as e:
        return render_template('result.html', error=f"网络错误：无法连接到阿里云API服务器。错误详情: {e}")
    except Exception as e:
        return render_template('result.html', error=f"发生未知错误: {e}")


@app.route('/api/token', methods=['POST'])
def api_token():
    req_data = request.json
    if not req_data:
        return jsonify({"code": "InvalidRequest", "message": "Request body must be JSON"}), 400
    
    ali_token_data = {
        'grant_type': req_data.get('grant_type'),
        'code': req_data.get('code'),
        'refresh_token': req_data.get('refresh_token'),
        'client_id': os.environ.get('ALIYUN_CLIENT_ID'),
        'client_secret': os.environ.get('ALIYUN_CLIENT_SECRET'),
    }
    if not ali_token_data['client_id'] or not ali_token_data['client_secret']:
        return jsonify({"code": "ServerError", "message": "Client ID/Secret not configured on auth server"}), 500
    
    try:
        response = requests.post(TOKEN_URL, json=ali_token_data, timeout=20)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        if e.response:
            return jsonify(e.response.json()), e.response.status_code
        else:
            return jsonify({"code": "ConnectionError", "message": str(e)}), 500

# --- 运行应用 ---
if __name__ == '__main__':
    print(f"--- 阿里云盘Token获取服务已启动 ---")
    print(f"手动获取地址: https://auth.example.com")
    print(f"Alist Token API接口: https://auth.example.com/api/token")
    print(f"服务正在监听 http://127.0.0.1:{APP_PORT}")
    if not os.environ.get('ALIYUN_CLIENT_ID') or not os.environ.get('ALIYUN_CLIENT_SECRET'):
        print("\n\033[91m[警告]\033[0m 环境变量 ALIYUN_CLIENT_ID 和 ALIYUN_CLIENT_SECRET 未设置。")
        print("所有功能都将无法工作。请设置环境变量后重启本应用。")
        print("例如: export ALIYUN_CLIENT_ID='xxx' && export ALIYUN_CLIENT_SECRET='yyy'")
    from waitress import serve
    serve(app, host='0.0.0.0', port=APP_PORT)
