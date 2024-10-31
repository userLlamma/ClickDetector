import os
import logging
import argparse
import torch
from transformers import (
    ClapModel, 
    ClapProcessor,
    Wav2Vec2Model,
    Wav2Vec2FeatureExtractor,
    AutoModel,
    AutoFeatureExtractor
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

MODEL_CONFIGS = {
    'clap': {
        'model_name': 'laion/clap-htsat-unfused',
        'model_class': ClapModel,
        'processor_class': ClapProcessor
    },
    'wav2vec': {
        'model_name': 'facebook/wav2vec2-base-960h',
        'model_class': Wav2Vec2Model,
        'processor_class': Wav2Vec2FeatureExtractor
    },
    'panns': {
        'model_name': 'microsoft/wavlm-base',  # PANNs替代模型
        'model_class': AutoModel,
        'processor_class': AutoFeatureExtractor
    }
}

def download_model(model_type, save_path='./model_cache'):
    """
    下载指定类型的模型并保存到指定目录
    
    Args:
        model_type (str): 模型类型 ('clap', 'wav2vec', 或 'panns')
        save_path (str): 保存路径
    """
    try:
        if model_type not in MODEL_CONFIGS:
            raise ValueError(f"Unsupported model type: {model_type}")
        
        # 创建特定模型的保存目录
        model_save_path = os.path.join(save_path, model_type)
        os.makedirs(model_save_path, exist_ok=True)
        logger.info(f"Downloading {model_type} model to {model_save_path}")
        
        config = MODEL_CONFIGS[model_type]
        
        # 下载模型
        logger.info(f"Downloading {model_type} model...")
        model = config['model_class'].from_pretrained(config['model_name'])
        logger.info("Model downloaded successfully")
        
        # 下载处理器
        logger.info(f"Downloading {model_type} processor...")
        processor = config['processor_class'].from_pretrained(config['model_name'])
        logger.info("Processor downloaded successfully")
        
        # 保存到本地
        logger.info("Saving model to local directory...")
        model.save_pretrained(model_save_path)
        processor.save_pretrained(model_save_path)
        logger.info(f"Successfully saved {model_type} model and processor")
        
        # 清理GPU内存
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            
        return True
        
    except Exception as e:
        logger.error(f"Error downloading {model_type} model: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Download audio models')
    parser.add_argument('--models', nargs='+', choices=['clap', 'wav2vec', 'panns', 'all'],
                      default=['all'], help='Which models to download')
    parser.add_argument('--save_path', default='./model_cache',
                      help='Directory to save the models')
    parser.add_argument('--proxy', default='http://127.0.0.1:10809',
                      help='Proxy address (e.g., http://127.0.0.1:10809)')
    
    args = parser.parse_args()
    
    # 设置代理
    if args.proxy:
        os.environ['HTTP_PROXY'] = args.proxy
        os.environ['HTTPS_PROXY'] = args.proxy
    
    # 确定要下载的模型
    models_to_download = list(MODEL_CONFIGS.keys()) if 'all' in args.models else args.models
    
    # 下载每个选定的模型
    success_count = 0
    for model_type in models_to_download:
        logger.info(f"\nStarting download of {model_type} model...")
        if download_model(model_type, args.save_path):
            success_count += 1
            logger.info(f"{model_type} model downloaded successfully")
        else:
            logger.error(f"Failed to download {model_type} model")
    
    # 输出总结
    logger.info(f"\nDownload summary:")
    logger.info(f"Successfully downloaded {success_count} out of {len(models_to_download)} models")
    if success_count == len(models_to_download):
        logger.info("All models downloaded successfully!")
    else:
        logger.warning("Some models failed to download. Please check the logs above.")

if __name__ == "__main__":
    main()