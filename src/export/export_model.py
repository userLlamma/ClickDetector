import os
import sys
import yaml
import torch
import logging
import argparse
from typing import Optional, Dict, Any

# 设置日志格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ModelExporter:
    """模型导出类"""
    
    def __init__(self, config_path: str):
        """
        初始化导出器
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
    @staticmethod
    def _load_config(config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config

    def _load_model(self) -> torch.nn.Module:
        """
        加载训练好的模型
        Returns:
            加载好权重的模型
        """
        try:
            # 导入原始模型定义
            sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            from models.model import ClickClassifier
            
            # 实例化模型
            model = ClickClassifier()
            
            # 加载权重
            checkpoint = torch.load(
                self.config['paths']['checkpoint_path'],
                map_location=self.device
            )
            
            # 处理权重格式
            if 'model_state_dict' in checkpoint:
                state_dict = checkpoint['model_state_dict']
            elif 'state_dict' in checkpoint:
                state_dict = checkpoint['state_dict']
            else:
                state_dict = checkpoint
                
            model.load_state_dict(state_dict)
            model.to(self.device)
            model.eval()
            
            logger.info("Model loaded successfully")
            return model
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise

    def _optimize_model(self, model: torch.nn.Module) -> torch.nn.Module:
        """
        优化模型（可选）
        Args:
            model: 原始模型
        Returns:
            优化后的模型
        """
        if self.config['optimization']['enabled']:
            try:
                # 这里可以添加模型优化的代码
                # 例如: 量化、剪枝等
                logger.info("Model optimization applied")
            except Exception as e:
                logger.warning(f"Model optimization failed: {str(e)}")
        return model

    def export(self, output_path: Optional[str] = None) -> str:
        """
        导出模型
        Args:
            output_path: 可选的输出路径，若不指定则使用配置文件中的路径
        Returns:
            导出模型的路径
        """
        try:
            # 加载模型
            model = self._load_model()
            
            # 优化模型
            model = self._optimize_model(model)
            
            # 准备示例输入
            dummy_input = torch.randn(
                self.config['model']['input_shape']
            ).to(self.device)
            
            # 选择导出格式
            export_format = self.config['export']['format'].lower()
            output_path = output_path or self.config['paths']['output_path']
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            if export_format == 'torchscript':
                self._export_torchscript(model, dummy_input, output_path)
            elif export_format == 'onnx':
                self._export_onnx(model, dummy_input, output_path)
            else:
                raise ValueError(f"Unsupported export format: {export_format}")
            
            # 验证导出的模型
            if self.config['validation']['enabled']:
                self._validate_exported_model(output_path, dummy_input)
            
            logger.info(f"Model exported successfully to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Export failed: {str(e)}")
            raise

    def _export_torchscript(
        self,
        model: torch.nn.Module,
        dummy_input: torch.Tensor,
        output_path: str
    ) -> None:
        """导出为TorchScript格式"""
        try:
            if self.config['export']['trace_method'] == 'trace':
                traced_model = torch.jit.trace(
                    model,
                    dummy_input,
                    check_trace=True
                )
            else:  # script
                traced_model = torch.jit.script(model)
            
            traced_model.save(output_path)
            
        except Exception as e:
            logger.error(f"TorchScript export failed: {str(e)}")
            raise

    def _export_onnx(
        self,
        model: torch.nn.Module,
        dummy_input: torch.Tensor,
        output_path: str
    ) -> None:
        """导出为ONNX格式"""
        try:
            import onnx
            import onnxruntime
            
            torch.onnx.export(
                model,
                dummy_input,
                output_path,
                input_names=['input'],
                output_names=['output'],
                dynamic_axes=self.config['export'].get('dynamic_axes', None),
                opset_version=self.config['export'].get('opset_version', 11),
                do_constant_folding=True,
                verbose=False
            )
            
            # 验证ONNX模型
            onnx_model = onnx.load(output_path)
            onnx.checker.check_model(onnx_model)
            
        except Exception as e:
            logger.error(f"ONNX export failed: {str(e)}")
            raise

    def _validate_exported_model(
        self,
        model_path: str,
        dummy_input: torch.Tensor
    ) -> None:
        """验证导出的模型"""
        try:
            # 获取原始模型输出
            original_model = self._load_model()
            with torch.no_grad():
                original_output = original_model(dummy_input)

            # 加载导出的模型
            if self.config['export']['format'].lower() == 'torchscript':
                exported_model = torch.jit.load(model_path)
                with torch.no_grad():
                    exported_output = exported_model(dummy_input)
            else:  # ONNX
                import onnxruntime
                session = onnxruntime.InferenceSession(model_path)
                exported_output = session.run(
                    None,
                    {'input': dummy_input.cpu().numpy()}
                )[0]
                exported_output = torch.from_numpy(exported_output)

            # 比较输出
            torch.testing.assert_close(
                original_output,
                exported_output,
                rtol=self.config['validation']['rtol'],
                atol=self.config['validation']['atol']
            )
            logger.info("Model validation passed")
            
        except Exception as e:
            logger.error(f"Model validation failed: {str(e)}")
            raise

def main():
    parser = argparse.ArgumentParser(description='Export model')
    parser.add_argument('--config', type=str, default='export/configs/export_config.yaml',
                      help='Path to config file')
    parser.add_argument('--output', type=str, default=None,
                      help='Output path for exported model')
    args = parser.parse_args()

    exporter = ModelExporter(args.config)
    exporter.export(args.output)

if __name__ == '__main__':
    main()