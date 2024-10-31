import torch
import os
from pathlib import Path

# 基础路径配置
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / 'data' / 'labeled'

# 数据配置
DATA_CONFIG = {
    'sr': 48000,                # 采样率
    'n_fft': 2048,             # FFT窗口大小
    'hop_length': 512,         # 帧移
    'n_mels': 128,             # Mel滤波器组数量
    'normal_dir': str(DATA_DIR / 'OK_AUG'),
    'abnormal_dir': str(DATA_DIR / 'NG_AUG'),
    'target_length': 100,      # 目标音频长度
    'test_size': 0.2,          # 验证集比例
    'random_seed': 42          # 随机种子
}

# 模型配置
MODEL_CONFIG = {
    'input_channels': 1,
    'num_classes': 2,
    'initial_channels': 8,
    'dropout_rate': 0.5,
    'use_batch_norm': True
}

# 训练配置
TRAIN_CONFIG = {
    'batch_size': 32,
    'num_epochs': 50,
    'learning_rate': 0.001,
    'weight_decay': 1e-5,      # L2正则化
    'device': torch.device("cuda" if torch.cuda.is_available() else "cpu"),
    'checkpoint_dir': 'checkpoints',
    'best_model_path': 'checkpoints/best_model.pt',
    'early_stopping_patience': 5,
    'scheduler_patience': 3,    # 学习率调度器的耐心值
    'scheduler_factor': 0.1,    # 学习率调整因子
    'gradient_clip_val': 1.0,   # 梯度裁剪值
    'num_workers': min(4, os.cpu_count() - 1) if os.cpu_count() > 1 else 0,
    'pin_memory': torch.cuda.is_available(),
    'log_interval': 32,         # 每多少个batch记录一次日志
    'keep_n_checkpoints': 3     # 保留最近的checkpoint数量
}

# 系统资源配置
SYSTEM_CONFIG = {
    'gpu_memory_fraction': 0.85, # GPU显存使用限制
    'cpu_reserve_cores': 2,     # 预留的CPU核心数
    'memory_limit_factor': 0.2, # 内存使用限制因子
    'prefetch_factor': 2,       # DataLoader预加载因子
}

# 日志配置
LOG_CONFIG = {
    'filename': 'training.log',
    'level': 'INFO',
    'format': '%(asctime)s - %(levelname)s - %(message)s'
}