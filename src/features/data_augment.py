import os
import soundfile as sf
import numpy as np
from scipy import signal
import random
from tqdm import tqdm
import json
from pathlib import Path

class AudioAugmenter:
    def __init__(self, target_sr=48000):
        self.target_sr = target_sr
        
    def load_audio(self, file_path):
        """加载并预处理音频"""
        waveform, sr = sf.read(file_path)
        
        # 转换为单声道
        if len(waveform.shape) > 1:
            waveform = np.mean(waveform, axis=1)
            
        # 重采样
        if sr != self.target_sr:
            duration = len(waveform) / sr
            new_length = int(duration * self.target_sr)
            waveform = signal.resample(waveform, new_length)
            
        return waveform
    
    def random_gain(self, waveform):
        """随机增益"""
        gain = random.uniform(0.8, 1.2)
        return waveform * gain
    
    def add_noise(self, waveform, noise_type='gaussian', noise_level=0.005):
        """添加噪声"""
        if noise_type == 'gaussian':
            noise = np.random.normal(0, 1, len(waveform))
        elif noise_type == 'pink':
            # 生成粉红噪声
            freqs = np.fft.fftfreq(len(waveform))
            freqs[0] = 1e-6
            f_filter = 1 / np.abs(freqs)
            f_filter = f_filter / np.sqrt(np.mean(f_filter**2))
            noise = np.fft.ifft(
                np.fft.fft(np.random.normal(0, 1, len(waveform))) * f_filter
            ).real
        else:
            raise ValueError(f"Unsupported noise type: {noise_type}")
            
        noise = noise / np.std(noise) * noise_level
        return waveform + noise
    
    def time_shift(self, waveform, max_shift_samples=16000):
        """时间偏移"""
        shift = random.randint(-max_shift_samples, max_shift_samples)
        return np.roll(waveform, shift)
    
    def augment_file(self, input_path, output_path, aug_types):
        """对单个文件进行增强"""
        waveform = self.load_audio(input_path)
        
        # 应用指定的增强
        for aug_type in aug_types:
            if aug_type == 'gain':
                waveform = self.random_gain(waveform)
            elif aug_type == 'gaussian_noise':
                waveform = self.add_noise(waveform, 'gaussian')
            elif aug_type == 'pink_noise':
                waveform = self.add_noise(waveform, 'pink')
            elif aug_type == 'time_shift':
                waveform = self.time_shift(waveform)
                
        # 保存增强后的音频
        sf.write(output_path, waveform, self.target_sr)
        
        return {
            'original_file': input_path,
            'augmented_file': output_path,
            'augmentations': aug_types
        }

def create_augmented_dataset(target_sr, input_dir, output_dir, augment_config):
    """
    为数据集创建增强版本，保留原始数据
    
    Args:
        input_dir: 输入目录
        output_dir: 输出目录
        augment_config: 增强配置，包含增强组合和比例
    """
    augmenter = AudioAugmenter(target_sr=target_sr)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    augmentation_info = []
    
    # 获取所有音频文件
    audio_files = [f for f in Path(input_dir).rglob('*') 
                  if f.suffix.lower() in ['.wav', '.mp3', '.flac']]
    
    # 首先复制所有原始文件
    print("复制原始文件...")
    for audio_file in tqdm(audio_files):
        rel_path = audio_file.relative_to(input_dir)
        out_path = output_dir / rel_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 复制原始文件
        import shutil
        shutil.copy2(audio_file, out_path)
        
        # 记录原始文件信息
        augmentation_info.append({
            'original_file': str(audio_file),
            'augmented_file': str(out_path),
            'augmentations': []  # 空列表表示无增强
        })
    
    # 然后进行数据增强
    print("生成增强数据...")
    for combo in augment_config['combinations']:
        if not combo:  # 跳过空组合（原始文件）
            continue
            
        # 将列表转换为更简单的键格式
        combo_key = str(combo).replace("'", "").replace("[", "").replace("]", "")
        ratio = augment_config['augmentation_ratio'][combo_key]
        num_files = int(len(audio_files) * ratio)
        
        # 随机选择文件进行增强
        selected_files = random.sample(audio_files, num_files)
        
        for audio_file in tqdm(selected_files, desc=f"Processing {combo}"):
            rel_path = audio_file.relative_to(input_dir)
            
            # 构建输出文件名
            aug_str = '_'.join(combo)
            out_name = f"{rel_path.stem}_{aug_str}{rel_path.suffix}"
            out_path = output_dir / out_name
            
            # 确保输出目录存在
            out_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 执行增强并记录信息
            aug_info = augmenter.augment_file(
                str(audio_file),
                str(out_path),
                combo
            )
            augmentation_info.append(aug_info)
    
    # 保存增强信息
    with open(output_dir / 'augmentation_info.json', 'w') as f:
        json.dump(augmentation_info, f, indent=2)
    
    # 打印统计信息
    print("\n数据集统计:")
    total_files = len(augmentation_info)
    original_files = len(audio_files)
    print(f"原始文件数: {original_files}")
    print(f"增强后总文件数: {total_files}")
    print(f"增强文件数: {total_files - original_files}")
    
    # 统计每种增强类型的数量
    combo_counts = {}
    for info in augmentation_info:
        combo = str(info['augmentations'])
        combo_counts[combo] = combo_counts.get(combo, 0) + 1
    
    print("\n各类型文件数量:")
    for combo, count in combo_counts.items():
        combo_name = "原始文件" if combo == "[]" else f"增强类型 {combo}"
        percentage = (count / original_files) * 100
        print(f"{combo_name}: {count} 文件 ({percentage:.1f}%)")
        
    return augmentation_info


# 使用示例
if __name__ == "__main__":
    config = {
        'combinations': [
            [],  # 空列表表示保持原样，不进行增强
            ['gain'],  # 仅使用增益调整
            ['gaussian_noise'],  # 仅添加高斯噪声
            ['pink_noise'],  # 仅添加粉红噪声
            ['gain', 'gaussian_noise'],  # 组合：增益调整+高斯噪声
            ['gain', 'time_shift']  # 组合：增益调整+时间偏移
        ],
        'augmentation_ratio': {  # 每种增强方式占原始数据的比例
            '': 1.0,  # 保持100%原始数据
            'gain': 0.3,  # 增益增强30%的数据
            'gaussian_noise': 0.2,  # 高斯噪声增强20%的数据
            'pink_noise': 0.2,  # 粉红噪声增强20%的数据
            'gain, gaussian_noise': 0.15,  # 组合增强15%的数据
            'gain, time_shift': 0.15  # 组合增强15%的数据
        }
    }
    
    augmentation_info = create_augmented_dataset(
        target_sr = 48000,
        input_dir=r'D:\东莞噪声检测\click_detection\data\labeled\NG',
        output_dir=r'D:\东莞噪声检测\click_detection\data\labeled\NG_AUG',
        augment_config=config
    )
    
    # 打印增强统计信息
    print("\nAugmentation Summary:")
    print(f"Total files generated: {len(augmentation_info)}")
    
    # 统计每种增强组合的数量
    combo_counts = {}
    for info in augmentation_info:
        combo = tuple(info['augmentations'])
        combo_counts[combo] = combo_counts.get(combo, 0) + 1
    
    print("\nFiles per augmentation combination:")
    for combo, count in combo_counts.items():
        print(f"{combo}: {count} files")