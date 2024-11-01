import logging
from pathlib import Path
import yaml
import os
from typing import Dict, Any
from ..core.predictor import ClickPredictor
from ..core.preprocess import AudioPreprocessor
from .token_manager import TokenManager

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class Config:
    def __init__(self, config_dict: Dict[str, Any]):
        logger.debug(f"Initializing Config with raw config: {config_dict}")
        
        self.raw_config = config_dict
        
        # Model配置
        self.model_config = config_dict.get('model', {})
        logger.debug(f"Model config: {self.model_config}")
        
        self.model_path = self.model_config.get('path')
        logger.debug(f"Model path: {self.model_path}")
        
        # API配置
        self.api_config = config_dict.get('api', {})
        logger.debug(f"API config: {self.api_config}")
        
        # Admin token
        self.admin_token = os.getenv(
            'ADMIN_TOKEN',
            self.api_config.get('admin_token', 'default-admin-token')
        )
        logger.debug(f"Admin token configured: {'yes' if self.admin_token else 'no'}")
        
        # Token配置
        self.tokens_config = self.api_config.get('tokens', [])
        
        # 添加字典式访问支持
        self.config_dict = config_dict
        
    def __getitem__(self, key):
        """支持字典式访问"""
        return self.config_dict[key]
    
    def get(self, key, default=None):
        """添加get方法支持"""
        return self.config_dict.get(key, default)
        
    def get_raw_config(self) -> Dict[str, Any]:
        return self.raw_config
    
    def get_model_config(self) -> Dict[str, Any]:
        return self.model_config
    
    def get_api_config(self) -> Dict[str, Any]:
        return self.api_config

def get_config_path() -> Path:
    current_file = Path(__file__)
    project_root = current_file.parent.parent.parent.parent
    config_path = project_root / "deploy" / "inference" / "configs" / "inference_config.yaml"
    logger.debug(f"Config path: {config_path}")
    return config_path

def load_yaml_config(config_path: Path) -> Dict[str, Any]:
    logger.debug(f"Loading config from: {config_path}")
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_dict = yaml.safe_load(f)
            logger.debug(f"Loaded config: {config_dict}")
            return config_dict
    except Exception as e:
        logger.error(f"Failed to load config: {e}", exc_info=True)
        raise RuntimeError(f"Failed to load config from {config_path}: {e}")

def get_config() -> Config:
    logger.info("Initializing configuration...")
    try:
        config_path = get_config_path()
        config_dict = load_yaml_config(config_path)
        config = Config(config_dict)
        logger.info("Configuration initialized successfully")
        return config
    except Exception as e:
        logger.error(f"Failed to initialize config: {e}", exc_info=True)
        raise

try:
    logger.info("Starting dependency initialization...")
    
    # 初始化配置
    config = get_config()
    logger.info("Config initialized successfully")

    # 初始化预处理器
    logger.debug("Initializing preprocessor...")
    preprocessor = AudioPreprocessor(config.get_raw_config())
    logger.info("Preprocessor initialized successfully")

    # 初始化预测器
    logger.debug("Initializing predictor...")
    predictor = ClickPredictor(
        model_path=config.model_path,
        config=config.get_raw_config()
    )
    logger.info("Predictor initialized successfully")

    # 初始化token管理器
    logger.debug("Initializing token manager...")
    token_manager = TokenManager(str(get_config_path()))
    logger.info("Token manager initialized successfully")

except Exception as e:
    logger.error(f"Failed to initialize dependencies: {e}", exc_info=True)
    raise

# 导出所有依赖
__all__ = ['config', 'preprocessor', 'predictor', 'token_manager']