import logging
import warnings
from torch.utils.data import Dataset
from src.features.preprocess_audio import AudioPreprocessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AudioDataset(Dataset):
    def __init__(self, audio_files, labels, config):
        self.audio_files = audio_files
        self.labels = labels
        self.preprocessor = AudioPreprocessor(config)
        
        # 可选：在初始化时检查采样率
        self._check_sample_rates()
    
    def _check_sample_rates(self):
        """检查所有音频文件的采样率"""
        inconsistent_files = []
        for file_path in self.audio_files:
            _, sr = sf.read(file_path, frames=1)
            if sr != self.preprocessor.target_sr:
                inconsistent_files.append((file_path, sr))
        
        if inconsistent_files:
            warning_msg = (
                f"Found {len(inconsistent_files)} files with non-target sample rate "
                f"({self.preprocessor.target_sr}Hz):\n" +
                "\n".join([f"File: {f}, SR: {sr}Hz" for f, sr in inconsistent_files[:5]])
            )
            if len(inconsistent_files) > 5:
                warning_msg += f"\n... and {len(inconsistent_files)-5} more"
            warnings.warn(warning_msg)
            logger.warning(warning_msg)
    
    def __len__(self):
        return len(self.audio_files)
    
    def __getitem__(self, idx):
        mel_spec = self.preprocessor.process_audio(self.audio_files[idx])
        return mel_spec, torch.tensor(self.labels[idx], dtype=torch.long)