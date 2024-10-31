import numpy as np
import soundfile as sf
import io
from typing import Tuple
from scipy import signal

def load_audio(audio_bytes: bytes) -> Tuple[np.ndarray, int]:
    """
    从字节数据加载音频
    Args:
        audio_bytes: 音频文件的字节数据
    Returns:
        (audio_data, sample_rate): 音频数据和采样率
    """
    try:
        # 使用soundfile从内存中读取音频
        with io.BytesIO(audio_bytes) as buf:
            audio_data, sample_rate = sf.read(buf)
        return audio_data, sample_rate
    except Exception as e:
        raise ValueError(f"Failed to load audio: {str(e)}")



def resample_audio(audio_data: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
    """
    使用 SciPy 重采样音频

    Args:
        audio_data: 输入的音频数据，numpy数组
        orig_sr: 原始采样率
        target_sr: 目标采样率

    Returns:
        重采样后的音频数据
    """

    if not isinstance(audio_data, np.ndarray):
        raise TypeError("Input data must be a numpy array.")
    if not isinstance(orig_sr, int) or not isinstance(target_sr, int):
        raise TypeError("Sampling rates must be integers.")

    # 计算需要重采样的点数
    num_samples = int(len(audio_data) * target_sr / orig_sr)
    
    # 使用 SciPy 的 resample 函数进行重采样
    resampled_audio = signal.resample(audio_data, num_samples)
    
    return resampled_audio