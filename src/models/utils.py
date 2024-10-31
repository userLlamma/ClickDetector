import os
import torch
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

def get_audio_files_and_labels(normal_dir, abnormal_dir):
    normal_files = [os.path.join(normal_dir, f) for f in os.listdir(normal_dir) if f.endswith('.wav')]
    abnormal_files = [os.path.join(abnormal_dir, f) for f in os.listdir(abnormal_dir) if f.endswith('.wav')]
    
    audio_files = normal_files + abnormal_files
    labels = [1] * len(normal_files) + [0] * len(abnormal_files)
    
    return audio_files, labels

def compute_metrics(y_true, y_pred):
    return {
        'accuracy': accuracy_score(y_true, y_pred),
        'precision': precision_score(y_true, y_pred),
        'recall': recall_score(y_true, y_pred),
        'f1': f1_score(y_true, y_pred)
    }

def save_checkpoint(model, optimizer, scheduler, epoch, loss, path):
    """
    保存检查点
    Args:
        model: 模型
        optimizer: 优化器
        scheduler: 学习率调度器
        epoch: 当前轮数
        loss: 损失值
        path: 保存路径
    """
    checkpoint = {
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'scheduler_state_dict': scheduler.state_dict() if scheduler else None,
        'loss': loss,
    }
    
    torch.save(checkpoint, path)