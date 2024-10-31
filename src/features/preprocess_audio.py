# src/features/preprocess_audio.py
import torch
import torchaudio
import numpy as np
from scipy import signal
import torch.nn.functional as F
import logging
from typing import Union, Optional
import argparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AudioPreprocessor:
    def __init__(
        self,
        target_sr: int,
        n_mels: int,
        target_length: int,
        n_fft: Optional[int] = None,
        hop_length: Optional[int] = None
    ):
        self.target_sr = target_sr
        self.target_length = target_length
        
        # 如果没有指定，使用默认值
        self.n_fft = n_fft or 2048
        self.hop_length = hop_length or self.n_fft // 4
        
        self.mel_transform = torchaudio.transforms.MelSpectrogram(
            sample_rate=self.target_sr,
            n_fft=self.n_fft,
            hop_length=self.hop_length,
            n_mels=n_mels
        )

    def load_audio(self, audio_input: Union[str, np.ndarray, torch.Tensor]) -> torch.Tensor:
        """
        加载并预处理音频数据
        
        Args:
            audio_input: 可以是文件路径、numpy数组或torch张量
            
        Returns:
            torch.Tensor: 形状为 [1, T] 的音频波形
        """
        if isinstance(audio_input, str):
            # 从文件加载
            try:
                waveform, sr = torchaudio.load(audio_input)
                waveform = waveform.mean(dim=0, keepdim=True)  # 转换为单声道
            except Exception as e:
                logger.error(f"Error loading audio file {audio_input}: {e}")
                raise
                
            # 重采样如果需要
            if sr != self.target_sr:
                logger.warning(f"Resampling from {sr}Hz to {self.target_sr}Hz")
                resampler = torchaudio.transforms.Resample(sr, self.target_sr)
                waveform = resampler(waveform)
                
        elif isinstance(audio_input, np.ndarray):
            # 从numpy数组转换
            waveform = torch.from_numpy(audio_input).float()
            if len(waveform.shape) == 1:
                waveform = waveform.unsqueeze(0)
            elif len(waveform.shape) == 2:
                waveform = waveform.mean(dim=0, keepdim=True)
                
        elif isinstance(audio_input, torch.Tensor):
            # 已经是torch张量
            waveform = audio_input
            if len(waveform.shape) == 1:
                waveform = waveform.unsqueeze(0)
            elif len(waveform.shape) > 2:
                waveform = waveform.mean(dim=0, keepdim=True)
                
        else:
            raise TypeError(f"Unsupported audio input type: {type(audio_input)}")
            
        return waveform
    
    def compute_melspec(self, waveform: torch.Tensor) -> torch.Tensor:
        """计算梅尔频谱图"""
        return self.mel_transform(waveform)
    
    def normalize_spec(self, mel_spec: torch.Tensor) -> torch.Tensor:
        """归一化频谱图"""
        mel_spec = torch.log10(torch.clamp(mel_spec, min=1e-10))
        mel_spec = (mel_spec - mel_spec.mean()) / (mel_spec.std() + 1e-8)
        return mel_spec
    
    def adjust_length(self, mel_spec: torch.Tensor) -> torch.Tensor:
        """调整频谱图长度"""
        curr_length = mel_spec.shape[-1]
        
        if curr_length > self.target_length:
            start = (curr_length - self.target_length) // 2
            mel_spec = mel_spec[..., start:start + self.target_length]
        elif curr_length < self.target_length:
            pad_left = (self.target_length - curr_length) // 2
            pad_right = self.target_length - curr_length - pad_left
            mel_spec = F.pad(mel_spec, (pad_left, pad_right), mode='reflect')
            
        return mel_spec
    
    def process_audio(self, audio_input: Union[str, np.ndarray, torch.Tensor]) -> torch.Tensor:
        """
        完整的音频处理流程
        
        Returns:
            torch.Tensor: 形状为 [C, F, T] 的梅尔频谱图
        """
        waveform = self.load_audio(audio_input)
        mel_spec = self.compute_melspec(waveform)
        mel_spec = self.normalize_spec(mel_spec)
        mel_spec = self.adjust_length(mel_spec)
        
        return mel_spec

def main():
    parser = argparse.ArgumentParser(description='Audio Preprocessing Tool')
    parser.add_argument('--input_dir', type=str, required=True,
                      help='Input directory containing WAV files')
    parser.add_argument('--output_dir', type=str, required=True,
                      help='Output directory for processed WAV files')
    parser.add_argument('--sample_rate', type=int, default=16000,
                      help='Target sample rate (default: 16000)')
    parser.add_argument('--workers', type=int, default=4,
                      help='Number of worker threads (default: 4)')
    
    args = parser.parse_args()
    
    preprocessor = AudioPreprocessor(target_sr=args.sample_rate)
    success_count, error_count = preprocessor.process_directory(
        args.input_dir,
        args.output_dir,
        num_workers=args.workers
    )

if __name__ == "__main__":
    main()