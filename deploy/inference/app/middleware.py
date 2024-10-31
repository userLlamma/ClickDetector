# deploy/inference/app/middleware.py
from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse
from ..app.dependencies import config

async def verify_token(request: Request, call_next):
    if request.url.path == "/demo" and request.method == "GET":
        # 允许直接访问demo页面
        return await call_next(request)
        
    token = request.headers.get("Authorization") or request.query_params.get("token")
    if not token or token not in config["api"]["allowed_tokens"]:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return await call_next(request)