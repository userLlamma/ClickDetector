import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from tqdm import tqdm
import logging
from config import TRAIN_CONFIG
from utils import compute_metrics, save_checkpoint

logger = logging.getLogger(__name__)

def train_model(model, train_loader, val_loader, optimizer=None, scheduler=None,
                start_epoch=0, best_val_loss=float('inf'),
                monitor_callback=None, checkpoint_callback=None):
    # 确保device设置正确
    device = torch.device(TRAIN_CONFIG['device']) if isinstance(TRAIN_CONFIG['device'], str) else TRAIN_CONFIG['device']
    logger.info(f'Using device: {device}')
    
    # 将模型移到设备
    model = model.to(device)

    if optimizer is None:
        optimizer = torch.optim.Adam(model.parameters(), lr=TRAIN_CONFIG['learning_rate'])
    
    criterion = nn.CrossEntropyLoss()
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', patience=5)
    
    best_val_loss = float('inf')
    
    try:
        for epoch in range(TRAIN_CONFIG['num_epochs']):
            logger.info(f'Starting epoch {epoch+1}/{TRAIN_CONFIG["num_epochs"]}')
            
            # 训练阶段
            model.train()
            train_loss = 0
            train_preds = []
            train_labels = []
            
            progress_bar = tqdm(train_loader, desc=f'Epoch {epoch+1}')
            for batch_idx, (specs, labels) in enumerate(progress_bar):
                try:
                    # 确保数据是tensor
                    if not isinstance(specs, torch.Tensor):
                        specs = torch.tensor(specs)
                    if not isinstance(labels, torch.Tensor):
                        labels = torch.tensor(labels)
                    
                    # 移动数据到设备
                    specs = specs.to(device)
                    labels = labels.to(device)
                    
                    optimizer.zero_grad()
                    outputs = model(specs)
                    loss = criterion(outputs, labels)
                    loss.backward()
                    optimizer.step()
                    
                    train_loss += loss.item()
                    _, predicted = outputs.max(1)
                    train_preds.extend(predicted.cpu().numpy())
                    train_labels.extend(labels.cpu().numpy())
                    
                    # 更新进度条
                    progress_bar.set_postfix({'loss': f'{loss.item():.4f}'})
                    
                    if monitor_callback:
                        monitor_callback(epoch, batch_idx, loss.item())
                        
                except Exception as e:
                    logger.error(f'Error in training batch {batch_idx}: {str(e)}')
                    raise
            
            # 计算训练指标
            train_metrics = compute_metrics(train_labels, train_preds)
            train_loss = train_loss / len(train_loader)
            
            # 验证阶段
            model.eval()
            val_loss = 0
            val_preds = []
            val_labels = []
            
            with torch.no_grad():
                for specs, labels in tqdm(val_loader, desc='Validation'):
                    try:
                        specs = specs.to(device)
                        labels = labels.to(device)
                        outputs = model(specs)
                        loss = criterion(outputs, labels)
                        
                        val_loss += loss.item()
                        _, predicted = outputs.max(1)
                        val_preds.extend(predicted.cpu().numpy())
                        val_labels.extend(labels.cpu().numpy())
                    except Exception as e:
                        logger.error(f'Error in validation: {str(e)}')
                        raise
            
            # 计算验证指标
            val_metrics = compute_metrics(val_labels, val_preds)
            val_loss = val_loss / len(val_loader)
            
            # 学习率调整
            scheduler.step(val_loss)
            current_lr = optimizer.param_groups[0]['lr']
            
            # 保存最佳模型
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                save_checkpoint(model, optimizer, scheduler, epoch, val_loss, TRAIN_CONFIG['best_model_path'])
                logger.info(f'Saved new best model with validation loss: {val_loss:.4f}')
            
            # 记录训练信息
            logger.info(f'Epoch: {epoch+1}')
            logger.info(f'Learning Rate: {current_lr:.6f}')
            logger.info(f'Train Loss: {train_loss:.4f} | Train Metrics: {train_metrics}')
            logger.info(f'Val Loss: {val_loss:.4f} | Val Metrics: {val_metrics}')
            
            # 打印训练信息
            print(f'\nEpoch: {epoch+1}')
            print(f'Learning Rate: {current_lr:.6f}')
            print(f'Train Loss: {train_loss:.4f} | Train Metrics: {train_metrics}')
            print(f'Val Loss: {val_loss:.4f} | Val Metrics: {val_metrics}\n')

            # 在每个epoch结束时保存checkpoint
            if checkpoint_callback:
                is_best = val_loss < best_val_loss
                best_val_loss = min(val_loss, best_val_loss)
                checkpoint_callback(model, optimizer, scheduler, epoch, best_val_loss, is_best)
            
    except Exception as e:
        logger.error(f'Training failed: {str(e)}')
        raise
    
    logger.info('Training completed successfully')
    return model

# 辅助函数：检查数据格式
def check_data_format(specs, labels):
    """检查数据格式是否正确"""
    if not isinstance(specs, torch.Tensor):
        raise TypeError(f"Expected specs to be torch.Tensor, got {type(specs)}")
    if not isinstance(labels, torch.Tensor):
        raise TypeError(f"Expected labels to be torch.Tensor, got {type(labels)}")
    return True