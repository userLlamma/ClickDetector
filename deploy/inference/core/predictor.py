import torch
import numpy as np
from typing import Dict, Any, Union, Optional
from pathlib import Path
import os
import logging
from src.models.model import ClickClassifier

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClickPredictor:
    def __init__(self, model_path: str, config: Dict[str, Any]):
        """
        初始化点击声音预测器
        Args:
            model_path: 模型文件路径（支持相对或绝对路径）
            config: 配置字典
        """
        self.config = config
        self._setup_device()
        self._setup_model_path(model_path)
        self._setup_parameters()
        self._load_and_prepare_model()

    def _setup_device(self) -> None:
        """配置计算设备"""
        device_name = self.config.get('model', {}).get('device', 'cuda' if torch.cuda.is_available() else 'cpu')
        self.device = torch.device(device_name)
        logger.info(f"Using device: {self.device}")

    def _setup_model_path(self, model_path: str) -> None:
        """设置模型路径"""
        current_dir = Path(__file__).parent.parent.parent.parent
        self.model_path = Path(model_path) if os.path.isabs(model_path) else current_dir / model_path
        logger.info(f"Model path: {self.model_path}")
        
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found: {self.model_path}")

    def _setup_parameters(self) -> None:
        """设置模型参数"""
        model_config = self.config.get('model', {})
        self.threshold = model_config.get('threshold', 0.5)
        self.label_map = self.config.get('postprocess', {}).get('label_map', {0: 'non_click', 1: 'click'})
        
        # 设置线程数
        num_threads = model_config.get('num_threads', None)
        if num_threads is not None:
            torch.set_num_threads(num_threads)
            logger.info(f"Set number of threads to {num_threads}")

    def _load_and_prepare_model(self) -> None:
        """加载和准备模型"""
        try:
            self.model = self._load_model()
            self.model.to(self.device)
            self.model.eval()
            logger.info("Model loaded and prepared successfully")
        except Exception as e:
            raise RuntimeError(f"Failed to load model: {str(e)}")

    def _load_model(self) -> torch.nn.Module:
        """
        加载模型
        Returns:
            加载的模型对象
        """
        try:
            # 尝试加载TorchScript模型
            return torch.jit.load(self.model_path)
        except Exception as e:
            logger.info(f"Failed to load as TorchScript model, trying regular model: {str(e)}")
            
            # 加载常规模型
            model = ClickClassifier()
            state_dict = torch.load(self.model_path, map_location='cpu')
            
            # 处理可能的'model.'前缀
            if any(k.startswith('model.') for k in state_dict.keys()):
                state_dict = {k.replace('model.', ''): v for k, v in state_dict.items()}
            
            model.load_state_dict(state_dict)
            return model

    @torch.no_grad()
    def predict(self, input_tensor: torch.Tensor) -> Dict[str, Any]:
        """
        使用模型进行预测
        Args:
            input_tensor: 预处理后的输入张量 [B, C, H, W]
        Returns:
            包含分类结果和置信度的字典
        """
        try:
            # 确保输入在正确的设备上
            input_tensor = input_tensor.to(self.device)
            
            # 模型推理
            output = self.model(input_tensor)
            probs = torch.softmax(output, dim=1)
            
            # 获取预测结果
            click_prob = probs[0, 1].item()
            predicted_class = int(click_prob >= self.threshold)
            
            return {
                "prediction": {
                    "class_id": predicted_class,
                    "class_name": self.label_map[predicted_class],
                    "score": click_prob,
                    "probabilities": {
                        self.label_map[0]: probs[0, 0].item(),
                        self.label_map[1]: click_prob
                    }
                }
            }
            
        except Exception as e:
            raise RuntimeError(f"Prediction failed: {str(e)}")

    def warmup(self, shape: Optional[tuple] = None) -> None:
        """
        模型预热
        Args:
            shape: 输入形状，默认使用配置中的shape
        """
        try:
            if shape is None:
                shape = self.config['model']['input_shape']
            
            dummy_input = torch.randn(shape, device=self.device)
            self.predict(dummy_input)
            logger.info("Model warmup completed successfully")
        except Exception as e:
            logger.warning(f"Model warmup failed: {str(e)}")