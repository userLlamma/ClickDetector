import os
import torch
import psutil
import glob
import multiprocessing
from torch.utils.data import DataLoader
from sklearn.model_selection import train_test_split
import logging
from pathlib import Path
import time
import gc
from torch.optim.lr_scheduler import ReduceLROnPlateau

from config import (
    TRAIN_CONFIG, DATA_CONFIG, SYSTEM_CONFIG, 
    LOG_CONFIG, MODEL_CONFIG
)
from model import ClickClassifier
from dataset import AudioDataset
from utils import get_audio_files_and_labels
from train import train_model

class TrainingManager:
    def __init__(self):
        self.setup_logging()
        self.setup_device()
        self.setup_resources()
        self.best_val_loss = float('inf')
        self.early_stopping_counter = 0
        
    def setup_logging(self):
        """配置日志系统"""
        logging.basicConfig(
            level=getattr(logging, LOG_CONFIG['level']),
            format=LOG_CONFIG['format'],
            handlers=[
                logging.FileHandler(LOG_CONFIG['filename']),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def setup_device(self):
        """配置计算设备和相关参数"""
        self.device = TRAIN_CONFIG['device']
        if torch.cuda.is_available():
            torch.cuda.set_per_process_memory_fraction(
                SYSTEM_CONFIG['gpu_memory_fraction']
            )
            torch.cuda.empty_cache()
            self.logger.info(f"Using GPU: {torch.cuda.get_device_name()}")
            self.logger.info(
                f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB"
            )
        else:
            n_cores = multiprocessing.cpu_count()
            torch.set_num_threads(n_cores - SYSTEM_CONFIG['cpu_reserve_cores'])
            self.logger.info(f"Using CPU with {n_cores-2} threads")

    def setup_resources(self):
        """配置系统资源参数"""
        self.cpu_count = multiprocessing.cpu_count()
        self.memory_available = psutil.virtual_memory().available
        self.num_workers = TRAIN_CONFIG['num_workers']
        
        # 根据可用内存动态调整batch_size
        suggested_batch_size = min(
            TRAIN_CONFIG['batch_size'],
            int(self.memory_available * SYSTEM_CONFIG['memory_limit_factor'] / 
                (MODEL_CONFIG['input_channels'] * DATA_CONFIG['n_mels'] * 
                 DATA_CONFIG['target_length'] * 4))
        )
        self.batch_size = max(4, suggested_batch_size)
        
        self.logger.info(f"Configured batch_size: {self.batch_size}")
        self.logger.info(f"Using {self.num_workers} workers for data loading")

    def create_data_loaders(self, train_dataset, val_dataset):
        """创建优化的数据加载器"""
        loader_kwargs = {
            'batch_size': self.batch_size,
            'num_workers': self.num_workers,
            'pin_memory': TRAIN_CONFIG['pin_memory'],
            'persistent_workers': bool(self.num_workers)
        }
        
        if self.num_workers > 0:
            loader_kwargs['prefetch_factor'] = SYSTEM_CONFIG['prefetch_factor']
        
        train_loader = DataLoader(
            train_dataset,
            shuffle=True,
            **loader_kwargs
        )
        
        val_loader = DataLoader(
            val_dataset,
            shuffle=False,
            **loader_kwargs
        )
        
        return train_loader, val_loader

    def monitor_resources(self):
        """监控系统资源使用情况"""
        cpu_percent = psutil.cpu_percent()
        memory_percent = psutil.virtual_memory().percent
        
        if torch.cuda.is_available():
            gpu_memory_used = torch.cuda.memory_allocated() / 1024**3
            self.logger.info(f"GPU Memory Used: {gpu_memory_used:.2f} GB")
            
        self.logger.info(f"CPU Usage: {cpu_percent}%")
        self.logger.info(f"Memory Usage: {memory_percent}%")
        
        if memory_percent > 90:
            gc.collect()
            torch.cuda.empty_cache()
            time.sleep(1)

    def load_latest_checkpoint(self, model, optimizer, scheduler=None):
        """加载最新的checkpoint"""
        checkpoint_dir = Path(TRAIN_CONFIG['checkpoint_dir'])
        checkpoints = glob.glob(str(checkpoint_dir / 'checkpoint_epoch_*.pt'))
        
        if not checkpoints:
            self.logger.info("No checkpoint found. Starting from scratch.")
            return 0
        
        latest_checkpoint = max(
            checkpoints, 
            key=lambda x: int(x.split('_')[-1].split('.')[0])
        )
        self.logger.info(f"Loading checkpoint: {latest_checkpoint}")
        
        checkpoint = torch.load(latest_checkpoint, map_location=self.device)
        model.load_state_dict(checkpoint['model_state_dict'])
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        
        if scheduler and 'scheduler_state_dict' in checkpoint:
            scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
        
        self.best_val_loss = checkpoint.get('best_val_loss', float('inf'))
        
        # 确保优化器状态在正确的设备上
        for state in optimizer.state.values():
            for k, v in state.items():
                if isinstance(v, torch.Tensor):
                    state[k] = v.to(self.device)
        
        return checkpoint['epoch'] + 1

    def save_checkpoint(self, model, optimizer, epoch, val_loss, scheduler=None):
        """保存checkpoint"""
        is_best = val_loss < self.best_val_loss
        if is_best:
            self.best_val_loss = val_loss
            
        checkpoint_dir = Path(TRAIN_CONFIG['checkpoint_dir'])
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'best_val_loss': self.best_val_loss,
            'val_loss': val_loss
        }
        
        if scheduler:
            checkpoint['scheduler_state_dict'] = scheduler.state_dict()
            
        # 保存常规checkpoint
        torch.save(
            checkpoint,
            checkpoint_dir / f'checkpoint_epoch_{epoch}.pt'
        )
        
        # 保存最佳模型
        if is_best:
            torch.save(
                checkpoint,
                Path(TRAIN_CONFIG['best_model_path'])
            )
        
        self.cleanup_old_checkpoints(TRAIN_CONFIG['keep_n_checkpoints'])
        
        return is_best
    
    def cleanup_old_checkpoints(self, keep_num):
        """清理旧的checkpoints"""
        checkpoint_dir = Path(TRAIN_CONFIG['checkpoint_dir'])
        checkpoints = glob.glob(str(checkpoint_dir / 'checkpoint_epoch_*.pt'))
        
        if len(checkpoints) <= keep_num:
            return
            
        checkpoints.sort(key=lambda x: int(x.split('_')[-1].split('.')[0]))
        
        for checkpoint in checkpoints[:-keep_num]:
            try:
                os.remove(checkpoint)
                self.logger.info(f"Removed old checkpoint: {checkpoint}")
            except Exception as e:
                self.logger.warning(f"Failed to remove checkpoint {checkpoint}: {e}")

def main():
    trainer = TrainingManager()
    
    try:
        # 创建必要的目录
        checkpoint_dir = Path(TRAIN_CONFIG['checkpoint_dir'])
        checkpoint_dir.mkdir(exist_ok=True, parents=True)
        
        # 获取数据
        trainer.logger.info("Loading dataset...")
        audio_files, labels = get_audio_files_and_labels(
            DATA_CONFIG['normal_dir'], 
            DATA_CONFIG['abnormal_dir']
        )
        
        # 分割数据集
        train_files, val_files, train_labels, val_labels = train_test_split(
            audio_files, labels, 
            test_size=DATA_CONFIG['test_size'], 
            random_state=DATA_CONFIG['random_seed']
        )
        
        # 创建数据集
        train_dataset = AudioDataset(
            train_files, train_labels, 
            target_length=DATA_CONFIG['target_length']
        )
        val_dataset = AudioDataset(
            val_files, val_labels, 
            target_length=DATA_CONFIG['target_length']
        )
        
        # 创建数据加载器
        train_loader, val_loader = trainer.create_data_loaders(
            train_dataset, val_dataset
        )
        
        # 初始化模型、优化器和学习率调度器
        model = ClickClassifier().to(trainer.device)
        optimizer = torch.optim.Adam(
            model.parameters(),
            lr=TRAIN_CONFIG['learning_rate'],
            weight_decay=TRAIN_CONFIG['weight_decay']
        )
        scheduler = ReduceLROnPlateau(
            optimizer,
            mode='min',
            patience=TRAIN_CONFIG['scheduler_patience'],
            factor=TRAIN_CONFIG['scheduler_factor']
        )

        # 加载最新的checkpoint
        start_epoch = trainer.load_latest_checkpoint(model, optimizer, scheduler)
        
        # 定义监控回调
        def monitor_callback(epoch, batch_idx, loss):
            if batch_idx % TRAIN_CONFIG['log_interval'] == 0:
                progress = (batch_idx + 1) / len(train_loader) * 100
                trainer.logger.info(
                    f'Epoch {epoch + 1}: {progress:.1f}% | Loss: {loss:.4f}'
                )
                trainer.monitor_resources()

        # 定义checkpoint回调
        def checkpoint_callback(model, optimizer, scheduler, epoch, val_loss, is_best):
            trainer.save_checkpoint(
                model=model,
                optimizer=optimizer,
                scheduler=scheduler,
                epoch=epoch,
                val_loss=val_loss
            )
        
        # 训练模型
        trainer.logger.info(f"Starting training from epoch {start_epoch + 1}")
        model = train_model(
            model=model,
            train_loader=train_loader,
            val_loader=val_loader,
            optimizer=optimizer,
            scheduler=scheduler,
            start_epoch=start_epoch,
            best_val_loss=trainer.best_val_loss,
            monitor_callback=monitor_callback,
            checkpoint_callback=checkpoint_callback
        )
        
        trainer.logger.info("Training completed successfully!")

    except Exception as e:
        trainer.logger.error(
            f"Error occurred during training: {str(e)}", 
            exc_info=True
        )
        raise
    finally:
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

if __name__ == "__main__":
    try:
        process = psutil.Process(os.getpid())
        if os.name == 'nt':
            process.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
        else:
            process.nice(10)
    except Exception as e:
        pass
    
    main()