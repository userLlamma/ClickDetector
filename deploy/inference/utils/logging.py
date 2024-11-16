# inference/app/utils/logging.py
from contextvars import ContextVar
from uvicorn.logging import AccessFormatter
from typing import Dict, Optional

# 定义线程本地存储的 ContextVar
_request_ip: ContextVar[str] = ContextVar("request_ip", default=None)

class RequestIP:
    """线程安全的工具类，用于存储和获取请求的客户端 IP"""
    
    @staticmethod
    def set(ip: str):
        """设置请求 IP"""
        _request_ip.set(ip)

    @staticmethod
    def get() -> str:
        """获取请求 IP"""
        return _request_ip.get() or "unknown"

# 全局实例
request_ip = RequestIP()

class CustomAccessFormatter(AccessFormatter):
    def get_client_addr(self, scope) -> str:
        """
        获取客户端真实IP
        优先级：
        1. CF-Connecting-IP (Cloudflare)
        2. X-Forwarded-For 最左侧IP
        3. X-Real-IP
        4. 直连IP
        """
        headers = dict(scope.get('headers', []))
        
        def get_header_value(header_name: str) -> Optional[str]:
            """安全地获取请求头的值"""
            value = headers.get(header_name.lower().encode(), b'').decode()
            return value.strip() if value else None

        # 1. 检查 Cloudflare 的IP
        cf_ip = get_header_value('CF-Connecting-IP')
        if cf_ip:
            return cf_ip

        # 2. 检查 X-Forwarded-For
        x_forwarded_for = get_header_value('X-Forwarded-For')
        if x_forwarded_for:
            # 取最左侧IP（客户端IP）
            return x_forwarded_for.split(',')[0].strip()

        # 3. 检查 X-Real-IP
        x_real_ip = get_header_value('X-Real-IP')
        if x_real_ip:
            return x_real_ip

        # 4. 降级到直连IP
        return super().get_client_addr(scope)

    def format(self, record):
        """确保使用上下文中存储的IP（如果存在）"""
        if hasattr(record, 'scope'):
            # 优先使用中间件设置的IP
            context_ip = request_ip.get()
            if context_ip and context_ip != "unknown":
                record.client_addr = context_ip
            else:
                # 降级到自己解析IP
                record.client_addr = self.get_client_addr(record.scope)
        return super().format(record)