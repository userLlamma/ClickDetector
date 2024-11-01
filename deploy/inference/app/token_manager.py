# deploy/inference/app/token_manager.py
from datetime import datetime
from typing import Optional, Dict, List, Any
import pytz
from pydantic import BaseModel, Field
import logging
from pathlib import Path
import yaml
import secrets

logger = logging.getLogger(__name__)

class TokenInfo(BaseModel):
    """Token信息模型"""
    token: str
    expires_at: Optional[datetime] = None
    description: Optional[str] = str
    created_at: datetime = Field(default_factory=lambda: datetime.now(pytz.UTC))
    last_used_at: Optional[datetime] = None
    usage_count: int = 0
    is_active: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TokenManager:
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化TokenManager
        
        Args:
            config_path: 配置文件路径，如果为None则使用默认路径
        """
        self.tokens: Dict[str, TokenInfo] = {}
        self.config_path = config_path or str(Path(__file__).parent.parent / "configs" / "inference_config.yaml")
        self._load_config()

    def _load_config(self) -> None:
        """从配置文件加载token配置"""
        try:
            with open(self.config_path) as f:
                config = yaml.safe_load(f)

            # 确保配置结构正确
            if not isinstance(config, dict) or "api" not in config:
                raise ValueError("Invalid config structure: missing 'api' section")

            api_config = config["api"]

            # 处理tokens部分
            if "tokens" in api_config:
                for token_data in api_config["tokens"]:
                    try:
                        token = token_data["token"]
                        expires_at = None
                        if "expires_at" in token_data:
                            expires_at = datetime.fromisoformat(token_data["expires_at"])
                            expires_at = expires_at.replace(tzinfo=pytz.UTC)

                        self.tokens[token] = TokenInfo(
                            token=token,
                            expires_at=expires_at,
                            description=token_data.get("description"),
                            metadata=token_data.get("metadata", {})
                        )
                    except Exception as e:
                        logger.error(f"Error loading token configuration: {e}")
                        continue

            # 处理默认token（向后兼容）
            if "default_token" in api_config:
                default_token = api_config["default_token"]
                if default_token not in self.tokens:
                    self.tokens[default_token] = TokenInfo(
                        token=default_token,
                        description="Default Token"
                    )

        except Exception as e:
            logger.error(f"Failed to load token configuration: {e}")
            raise

    def verify_token(self, token: str) -> bool:
        """
        验证token是否有效
        
        Args:
            token: 要验证的token
            
        Returns:
            bool: token是否有效
        """
        if token not in self.tokens:
            return False

        token_info = self.tokens[token]
        
        # 检查token是否被禁用
        if not token_info.is_active:
            return False

        # 检查是否过期
        if token_info.expires_at is not None:
            current_time = datetime.now(pytz.UTC)
            if current_time > token_info.expires_at:
                return False

        # 更新使用信息
        self._update_token_usage(token)
        return True

    def _update_token_usage(self, token: str) -> None:
        """更新token使用信息"""
        if token in self.tokens:
            token_info = self.tokens[token]
            token_info.last_used_at = datetime.now(pytz.UTC)
            token_info.usage_count += 1

    def get_token_info(self, token: str) -> Optional[TokenInfo]:
        """获取token详细信息"""
        return self.tokens.get(token)

    def list_active_tokens(self) -> List[TokenInfo]:
        """列出所有当前有效的token"""
        current_time = datetime.now(pytz.UTC)
        return [
            token_info for token_info in self.tokens.values()
            if token_info.is_active and (
                token_info.expires_at is None or 
                current_time <= token_info.expires_at
            )
        ]

    def disable_token(self, token: str) -> bool:
        """禁用指定token"""
        if token in self.tokens:
            self.tokens[token].is_active = False
            return True
        return False

    def enable_token(self, token: str) -> bool:
        """启用指定token"""
        if token in self.tokens:
            self.tokens[token].is_active = True
            return True
        return False

    @staticmethod
    def generate_token(prefix: str = "test") -> str:
        """生成新的安全token"""
        random_part = secrets.token_urlsafe(16)
        return f"{prefix}_{random_part}"

    def add_token(
        self,
        token: Optional[str] = None,
        description: Optional[str] = None,
        expires_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> TokenInfo:
        """
        添加新token
        
        Args:
            token: 可选，指定token值，如果为None则自动生成
            description: token描述
            expires_at: 过期时间
            metadata: 额外元数据
            
        Returns:
            TokenInfo: 新创建的token信息
        """
        if token is None:
            token = self.generate_token()

        if token in self.tokens:
            raise ValueError(f"Token {token} already exists")

        token_info = TokenInfo(
            token=token,
            description=description,
            expires_at=expires_at.replace(tzinfo=pytz.UTC) if expires_at else None,
            metadata=metadata or {}
        )
        
        self.tokens[token] = token_info
        return token_info

    def remove_token(self, token: str) -> bool:
        """
        删除指定token
        
        Args:
            token: 要删除的token
            
        Returns:
            bool: 是否成功删除
        """
        if token in self.tokens:
            del self.tokens[token]
            return True
        return False

    def get_token_status(self) -> Dict[str, List[TokenInfo]]:
        """
        获取所有token的状态分类
        
        Returns:
            Dict包含active、expiring_soon和expired的token列表
        """
        current_time = datetime.now(pytz.UTC)
        active = []
        expiring_soon = []
        expired = []

        for token_info in self.tokens.values():
            if not token_info.is_active:
                expired.append(token_info)
                continue

            if token_info.expires_at is None:
                active.append(token_info)
                continue

            time_to_expire = token_info.expires_at - current_time
            if time_to_expire.total_seconds() <= 0:
                expired.append(token_info)
            elif time_to_expire.days <= 7:
                expiring_soon.append(token_info)
            else:
                active.append(token_info)

        return {
            "active": active,
            "expiring_soon": expiring_soon,
            "expired": expired
        }

    def cleanup_expired_tokens(self) -> int:
        """
        清理所有过期的token
        
        Returns:
            int: 清理的token数量
        """
        current_time = datetime.now(pytz.UTC)
        expired_tokens = [
            token for token, info in self.tokens.items()
            if info.expires_at is not None and current_time > info.expires_at
        ]
        
        for token in expired_tokens:
            del self.tokens[token]
            
        return len(expired_tokens)

    def extend_token_expiry(self, token: str, days: int) -> bool:
        """
        延长token的有效期
        
        Args:
            token: 要延长的token
            days: 延长的天数
            
        Returns:
            bool: 是否成功延长
        """
        if token not in self.tokens:
            return False

        token_info = self.tokens[token]
        current_time = datetime.now(pytz.UTC)
        
        if token_info.expires_at is None:
            # 如果是永久token，不需要延长
            return True
            
        # 从当前时间或原过期时间中取较大值作为基准
        base_time = max(current_time, token_info.expires_at)
        token_info.expires_at = base_time + timedelta(days=days)
        return True