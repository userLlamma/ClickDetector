# token_management.py
from typing import Dict, Optional
import yaml
from datetime import datetime, timedelta

class TokenManagement:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.load_config()

    def load_config(self):
        with open(self.config_path) as f:
            self.config = yaml.safe_load(f)

    def save_config(self):
        with open(self.config_path, 'w') as f:
            yaml.dump(self.config, f)

    def add_token(self, description: str, days: Optional[int] = 30, prefix: str = "test"):
        """添加新token"""
        token, expires_at = generate_token(prefix, days)
        
        new_token = {
            "token": token,
            "description": description,
        }
        if days is not None:
            new_token["expires_at"] = expires_at

        if "tokens" not in self.config["api"]:
            self.config["api"]["tokens"] = []
            
        self.config["api"]["tokens"].append(new_token)
        self.save_config()
        
        return token, expires_at

    def revoke_token(self, token: str):
        """撤销token"""
        self.config["api"]["tokens"] = [
            t for t in self.config["api"]["tokens"]
            if t["token"] != token
        ]
        self.save_config()

# 使用示例
manager = TokenManagement("inference_config.yaml")

# 为客户创建token
client_token, expires = manager.add_token(
    description="Client A Testing",
    days=30,
    prefix="client_a"
)

# 为演示活动创建token
demo_token, expires = manager.add_token(
    description="Tech Conference Demo",
    days=1,
    prefix="demo"
)

# 撤销token
manager.revoke_token(client_token)