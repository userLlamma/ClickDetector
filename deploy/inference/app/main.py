# deploy/inference/app/main.py
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from datetime import datetime, timedelta
import pytz

from .dependencies import predictor, config
from .routers import predict
from .token_manager import TokenManager

# 创建FastAPI应用
app = FastAPI(
    title="Click Classification API",
    description="API for click sound classification",
    version="1.0.0"
)

# 初始化token管理器
token_manager = TokenManager()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

async def verify_token(x_api_token: Optional[str] = Header(None)):
    """Token验证依赖"""
    if x_api_token is None:
        raise HTTPException(
            status_code=401,
            detail="Missing API token"
        )
    
    if not token_manager.verify_token(x_api_token):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )
    return x_api_token

# 包含路由，添加token验证
app.include_router(
    predict.router,
    dependencies=[Depends(verify_token)]  # 为所有预测接口添加token验证
)

# Token管理接口
@app.post("/admin/tokens", tags=["admin"])
async def create_token(
    description: str,
    days: Optional[int] = 30,
    x_admin_token: str = Header(...),  # 管理员token
):
    """创建新的API token"""
    # 验证管理员token
    if x_admin_token != config.admin_token:
        raise HTTPException(
            status_code=401,
            detail="Invalid admin token"
        )
    
    token_info = token_manager.add_token(
        description=description,
        expires_at=datetime.now(pytz.UTC) + timedelta(days=days) if days else None
    )
    return token_info

@app.get("/admin/tokens", tags=["admin"])
async def list_tokens(x_admin_token: str = Header(...)):
    """列出所有token状态"""
    if x_admin_token != config.admin_token:
        raise HTTPException(
            status_code=401,
            detail="Invalid admin token"
        )
    return token_manager.get_token_status()

@app.delete("/admin/tokens/{token}", tags=["admin"])
async def revoke_token(
    token: str,
    x_admin_token: str = Header(...)
):
    """撤销指定token"""
    if x_admin_token != config.admin_token:
        raise HTTPException(
            status_code=401,
            detail="Invalid admin token"
        )
    
    if token_manager.disable_token(token):
        return {"message": f"Token {token} has been revoked"}
    raise HTTPException(
        status_code=404,
        detail="Token not found"
    )

@app.put("/admin/tokens/{token}/extend", tags=["admin"])
async def extend_token(
    token: str,
    days: int,
    x_admin_token: str = Header(...)
):
    """延长token有效期"""
    if x_admin_token != config.admin_token:
        raise HTTPException(
            status_code=401,
            detail="Invalid admin token"
        )
    
    if token_manager.extend_token_expiry(token, days):
        return {"message": f"Token {token} extended by {days} days"}
    raise HTTPException(
        status_code=404,
        detail="Token not found"
    )

@app.on_event("startup")
async def startup_event():
    """启动时预热模型"""
    predictor.warmup()

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy"}

# Token验证接口
@app.get("/verify-token")
async def verify_token_endpoint(token: str = Depends(verify_token)):
    """验证token有效性"""
    token_info = token_manager.get_token_info(token)
    if token_info:
        return {
            "valid": True,
            "expires_at": token_info.expires_at,
            "description": token_info.description
        }
    return {"valid": False}