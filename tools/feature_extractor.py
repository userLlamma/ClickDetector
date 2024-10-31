import os
import torch
import logging
from transformers import (
    ClapModel, 
    ClapProcessor,
    Wav2Vec2Model,
    Wav2Vec2FeatureExtractor,
    AutoModel,
    AutoFeatureExtractor
)
import librosa
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AudioFeatureExtractor:
    def __init__(self, model_type='clap', model_path='./model_cache', offline_mode=False):
        self.model_type = model_type
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Using device: {self.device}")
        
        self.MODEL_CONFIGS = {
            'clap': {
                'model_name': 'laion/clap-htsat-unfused',
                'model_class': ClapModel,
                'processor_class': ClapProcessor,
                'sample_rate': 48000,
                'local_dir': 'clap'
            },
            'wav2vec': {
                'model_name': 'facebook/wav2vec2-base-960h',
                'model_class': Wav2Vec2Model,
                'processor_class': Wav2Vec2FeatureExtractor,
                'sample_rate': 48000,
                'local_dir': 'wav2vec'
            },
            'panns': {
                'model_name': 'microsoft/wavlm-base',
                'model_class': AutoModel,
                'processor_class': AutoFeatureExtractor,
                'sample_rate': 32000,
                'local_dir': 'panns'
            }
        }
        
        if model_type not in self.MODEL_CONFIGS:
            raise ValueError(f"Unsupported model type: {model_type}")
            
        self._initialize_model(model_type, model_path, offline_mode)
        
    def _initialize_model(self, model_type, model_path, offline_mode):
        try:
            config = self.MODEL_CONFIGS[model_type]
            self.sample_rate = config['sample_rate']
            
            if offline_mode:
                load_path = os.path.join(model_path, config['local_dir'])
                if not os.path.exists(load_path):
                    raise FileNotFoundError(f"Model directory not found at {load_path}")
                logger.info(f"Loading {model_type} model from local path: {load_path}")
                
                self.model = config['model_class'].from_pretrained(
                    load_path,
                    local_files_only=True
                ).to(self.device)
                
                if model_type == 'wav2vec':
                    self.processor = config['processor_class'].from_pretrained(
                        load_path,
                        local_files_only=True,
                        sampling_rate=self.sample_rate,
                        do_normalize=True,
                        return_attention_mask=True
                    )
                else:
                    self.processor = config['processor_class'].from_pretrained(
                        load_path,
                        local_files_only=True
                    )
            else:
                logger.info(f"Loading {model_type} model from Hugging Face: {config['model_name']}")
                self.model = config['model_class'].from_pretrained(
                    config['model_name']
                ).to(self.device)
                
                if model_type == 'wav2vec':
                    self.processor = config['processor_class'].from_pretrained(
                        config['model_name'],
                        sampling_rate=self.sample_rate,
                        do_normalize=True,
                        return_attention_mask=True
                    )
                else:
                    self.processor = config['processor_class'].from_pretrained(
                        config['model_name']
                    )
            
            self.model.eval()
            logger.info(f"Successfully initialized {model_type} model")
            
        except Exception as e:
            logger.error(f"Error initializing {model_type} model: {str(e)}")
            raise
            
    def extract_features(self, audio_path, normalize_audio=True):
        try:
            # 加载音频文件
            audio, orig_sr = librosa.load(audio_path, sr=self.sample_rate)
            
            # 音频归一化
            if normalize_audio:
                audio = librosa.util.normalize(audio)
            
            with torch.no_grad():
                if self.model_type == 'clap':
                    inputs = self.processor(
                        audio, 
                        sampling_rate=self.sample_rate, 
                        return_tensors="pt"
                    ).to(self.device)
                    outputs = self.model.get_audio_features(**inputs)
                    
                elif self.model_type == 'wav2vec':
                    # 确保音频是float32类型
                    audio = audio.astype(np.float32)
                    
                    # 处理音频输入
                    inputs = self.processor(
                        audio,
                        sampling_rate=self.sample_rate,
                        return_tensors="pt",
                        padding=True
                    )
                    
                    # 移动到正确的设备
                    input_values = inputs.input_values.to(self.device)
                    attention_mask = inputs.attention_mask.to(self.device) if hasattr(inputs, 'attention_mask') else None
                    
                    # 获取模型输出
                    if attention_mask is not None:
                        outputs = self.model(input_values, attention_mask=attention_mask)
                    else:
                        outputs = self.model(input_values)
                    
                    outputs = outputs.last_hidden_state
                
                elif self.model_type == 'panns':
                    inputs = self.processor(
                        audio, 
                        sampling_rate=self.sample_rate, 
                        return_tensors="pt", 
                        padding=True
                    ).to(self.device)
                    outputs = self.model(**inputs).last_hidden_state
                
                # 获取特征向量
                features = outputs.mean(dim=1).cpu().numpy()
                
            return features.flatten()
            
        except Exception as e:
            logger.error(f"Error extracting features from {audio_path}: {str(e)}")
            raise
            
    def __call__(self, audio_path, normalize_audio=True):
        return self.extract_features(audio_path, normalize_audio)

    def get_model_info(self):
        return {
            'model_type': self.model_type,
            'sample_rate': self.sample_rate,
            'device': str(self.device),
            'model_config': self.MODEL_CONFIGS[self.model_type]
        }