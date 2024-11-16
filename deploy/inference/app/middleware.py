# deploy/inference/app/middleware.py
from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse
from ..app.dependencies import config
from ..utils.logging import request_ip

async def verify_token(request: Request, call_next):
    if request.url.path == "/demo" and request.method == "GET":
        # 允许直接访问demo页面
        return await call_next(request)
        
    token = request.headers.get("Authorization") or request.query_params.get("token")
    if not token or token not in config["api"]["allowed_tokens"]:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return await call_next(request)

async def client_ip_middleware(request: Request, call_next):
    """
    中间件: 获取并设置客户端真实IP
    处理以下场景:
    1. CDN场景 (CloudFront/其他CDN)
    2. 直接访问场景
    3. 反向代理场景
    """
    def get_real_ip() -> str:
        # 1. 优先检查CDN专用头
        if 'CF-Connecting-IP' in request.headers:  # Cloudflare
            return request.headers['CF-Connecting-IP'].strip()
        
        # 2. 检查X-Forwarded-For
        if 'X-Forwarded-For' in request.headers:
            ips = [ip.strip() for ip in request.headers['X-Forwarded-For'].split(',')]
            if ips:
                return ips[0]  # 取最左侧IP (最原始客户端IP)
        
        # 3. 检查X-Real-IP
        if 'X-Real-IP' in request.headers:
            return request.headers['X-Real-IP'].strip()
        
        # 4. 降级到直连IP
        return request.client.host

    client_ip = get_real_ip()
    request_ip.set(client_ip)
    response = await call_next(request)
    return response