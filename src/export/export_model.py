import os
import sys
import yaml
import torch
import logging
import argparse
from typing import Optional, Dict, Any

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ModelExporter:
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        
    @staticmethod
    def _load_config(config_path: str) -> Dict[str, Any]:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config

    def _load_model(self) -> torch.nn.Module:
        try:
            # 导入原始模型定义
            # 使用绝对导入
            from src.models.model import ClickClassifier
            
            # 实例化模型
            model = ClickClassifier()
            
            # 加载权重（统一使用CPU）
            checkpoint = torch.load(
                self.config['paths']['checkpoint_path'],
                map_location='cpu',
                weights_only=True  # 添加这个参数来提高安全性
            )
            
            # 处理权重格式
            if 'model_state_dict' in checkpoint:
                state_dict = checkpoint['model_state_dict']
            elif 'state_dict' in checkpoint:
                state_dict = checkpoint['state_dict']
            else:
                state_dict = checkpoint
                
            model.load_state_dict(state_dict)
            model.eval()
            
            logger.info("Model loaded successfully")
            return model
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise

    def export(self, output_path: Optional[str] = None) -> str:
        try:
            # 加载模型
            model = self._load_model()
            
            # 准备示例输入
            dummy_input = torch.randn(self.config['model']['input_shape'])
            
            # 选择导出格式
            export_format = self.config['export']['format'].lower()
            output_path = output_path or self.config['paths']['output_path']
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 导出模型
            if export_format == 'torchscript':
                self._export_torchscript(model, dummy_input, output_path)
            elif export_format == 'onnx':
                self._export_onnx(model, dummy_input, output_path)
            else:
                raise ValueError(f"Unsupported export format: {export_format}")
            
            # 验证导出的模型
            if self.config['validation']['enabled']:
                self._validate_exported_model(model, output_path, dummy_input)
            
            logger.info(f"Model exported successfully to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Export failed: {str(e)}")
            raise

    def _export_torchscript(self, model: torch.nn.Module, dummy_input: torch.Tensor, output_path: str) -> None:
        try:
            if self.config['export']['trace_method'] == 'trace':
                traced_model = torch.jit.trace(model, dummy_input, check_trace=True)
            else:
                traced_model = torch.jit.script(model)
            
            traced_model.save(output_path)
            
        except Exception as e:
            logger.error(f"TorchScript export failed: {str(e)}")
            raise

    def _export_onnx(self, model: torch.nn.Module, dummy_input: torch.Tensor, output_path: str) -> None:
        try:
            torch.onnx.export(
                model,
                dummy_input,
                output_path,
                input_names=['input'],
                output_names=['output'],
                dynamic_axes=self.config['export'].get('dynamic_axes', None),
                opset_version=self.config['export'].get('opset_version', 11),
                do_constant_folding=True
            )
            
        except Exception as e:
            logger.error(f"ONNX export failed: {str(e)}")
            raise

    def _validate_exported_model(self, original_model: torch.nn.Module, model_path: str, dummy_input: torch.Tensor) -> None:
        try:
            # 获取原始模型输出
            with torch.no_grad():
                original_output = original_model(dummy_input)

            # 加载并验证导出的模型
            if self.config['export']['format'].lower() == 'torchscript':
                exported_model = torch.jit.load(model_path)
                with torch.no_grad():
                    exported_output = exported_model(dummy_input)
                
                # 比较输出
                torch.testing.assert_close(
                    original_output,
                    exported_output,
                    rtol=float(self.config['validation']['rtol']),  # 转换为float
                    atol=float(self.config['validation']['atol'])   # 转换为float
                )
                logger.info("Model validation passed")
                
        except Exception as e:
            logger.error(f"Model validation failed: {str(e)}")
            raise

def main():
    parser = argparse.ArgumentParser(description='Export model')
    parser.add_argument('--config', type=str, required=True, help='Path to config file')
    parser.add_argument('--output', type=str, help='Output path for exported model')
    args = parser.parse_args()

    exporter = ModelExporter(args.config)
    exporter.export(args.output)

if __name__ == '__main__':
    main()