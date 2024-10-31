# inference/core/preprocess.py
from src.features.preprocess_audio import AudioPreprocessor as BaseAudioPreprocessor
import torch
from typing import Dict, Any, Union
import numpy as np

class AudioPreprocessor(BaseAudioPreprocessor):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            target_sr=config['preprocess']['sample_rate'],
            n_mels=config['preprocess']['n_mels'],
            target_length=config['preprocess']['target_length'],
            n_fft=config['preprocess'].get('n_fft'),
            hop_length=config['preprocess'].get('hop_length')
        )
        self.config = config['preprocess']
    
    def __call__(self, audio_input: Union[str, np.ndarray, torch.Tensor]) -> torch.Tensor:
        """
        处理音频数据并返回适合模型输入的格式
        
        Args:
            audio_input: 音频输入，可以是文件路径、numpy数组或torch张量
            
        Returns:
            torch.Tensor: 形状为 [1, 1, F, T] 的梅尔频谱图
        """
        # 使用基类的预处理方法
        mel_spec = super().process_audio(audio_input)
        
        # 添加批次维度和通道维度 [F, T] -> [1, 1, F, T]
        if len(mel_spec.shape) == 2:
            mel_spec = mel_spec.unsqueeze(0).unsqueeze(0)
        elif len(mel_spec.shape) == 3:
            mel_spec = mel_spec.unsqueeze(0)
            
        return mel_spec