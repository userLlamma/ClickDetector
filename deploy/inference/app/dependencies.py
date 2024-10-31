# deploy/inference/app/dependencies.py
from pathlib import Path
import yaml
import os
from typing import Dict, Any
from ..core.predictor import ClickPredictor
from ..core.preprocess import AudioPreprocessor
from .token_manager import TokenManager

class Config:
    def __init__(self, config_dict: Dict[str, Any]):
        self.raw_config = config_dict
        
        # Model配置
        self.model_config = config_dict.get('model', {})
        self.model_path = self.model_config.get('path')
        
        # API配置
        self.api_config = config_dict.get('api', {})
        
        # Admin token - 优先从环境变量获取，否则从配置文件获取
        self.admin_token = os.getenv(
            'ADMIN_TOKEN',
            self.api_config.get('admin_token', 'default-admin-token')
        )
        
        # Token配置
        self.tokens_config = self.api_config.get('tokens', [])
        
        # 其他配置...
        
    def get_raw_config(self) -> Dict[str, Any]:
        """获取原始配置字典"""
        return self.raw_config
    
    def get_model_config(self) -> Dict[str, Any]:
        """获取模型相关配置"""
        return self.model_config
    
    def get_api_config(self) -> Dict[str, Any]:
        """获取API相关配置"""
        return self.api_config

def get_config_path() -> Path:
    """获取配置文件路径"""
    current_file = Path(__file__)
    project_root = current_file.parent.parent.parent.parent
    return project_root / "deploy" / "inference" / "configs" / "inference_config.yaml"

def load_yaml_config(config_path: Path) -> Dict[str, Any]:
    """加载YAML配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        raise RuntimeError(f"Failed to load config from {config_path}: {e}")

def get_config() -> Config:
    """获取配置实例"""
    config_path = get_config_path()
    config_dict = load_yaml_config(config_path)
    return Config(config_dict)

# 初始化配置
config = get_config()

# 初始化预处理器
preprocessor = AudioPreprocessor(config.get_raw_config())

# 初始化预测器
predictor = ClickPredictor(
    model_path=config.model_path,
    config=config.get_raw_config()
)

# 初始化token管理器
token_manager = TokenManager(str(get_config_path()))

# 导出所有依赖
__all__ = ['config', 'preprocessor', 'predictor', 'token_manager']