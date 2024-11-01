# deploy/scripts/verify_traced_model.py
import torch
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_traced_model(model_path: str, input_shape: tuple = (1, 1, 16000)):
    """验证 traced/scripted 模型"""
    try:
        logger.info(f"Loading model from {model_path}")
        model = torch.jit.load(model_path)
        model.eval()
        
        logger.info("Model loaded successfully")
        logger.info(f"Model type: {type(model)}")
        
        # 创建测试输入
        dummy_input = torch.randn(*input_shape)
        logger.info(f"Testing with input shape: {input_shape}")
        
        # 测试前向传播
        with torch.no_grad():
            output = model(dummy_input)
            logger.info(f"Forward pass successful")
            logger.info(f"Output shape: {output.shape}")
        
        # 打印模型信息
        logger.info("\nModel structure:")
        logger.info(model)
        
        return True
        
    except Exception as e:
        logger.error(f"Error verifying model: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python verify_traced_model.py <model_path>")
        sys.exit(1)
        
    model_path = sys.argv[1]
    verify_traced_model(model_path)