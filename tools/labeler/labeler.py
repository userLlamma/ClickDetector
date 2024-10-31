import tkinter as tk
from tkinter import ttk, filedialog
import os
import numpy as np
import librosa
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import soundfile as sf
import matplotlib

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False

def blackman_harris(N):
    n = np.arange(N)
    w = (0.35875 - 
         0.48829 * np.cos(2 * np.pi * n / (N-1)) + 
         0.14128 * np.cos(4 * np.pi * n / (N-1)) - 
         0.01168 * np.cos(6 * np.pi * n / (N-1)))
    return w

def blackman_hanning(N):
    blackman = np.blackman(N)
    hanning = np.hanning(N)
    return 0.5 * (blackman + hanning)

class AudioLabeler:
    def __init__(self, audio_dir=None):
        self.root = tk.Tk()
        self.root.title("音频标注工具")
        self.root.geometry("800x600")
        
        self.target_sr = 48000
        
        # STFT参数
        self.n_fft = 2048
        self.hop_length = int(self.n_fft * 0.25)
        self.window = blackman_harris(self.n_fft)
        
        self.audio_dir = audio_dir
        if not self.audio_dir:
            self.audio_dir = filedialog.askdirectory(title="选择音频文件夹")
            if not self.audio_dir:
                self.root.destroy()
                return
                
        self.normal_dir = os.path.join(self.audio_dir, 'normal_clicks')
        self.others_dir = os.path.join(self.audio_dir, 'others')
        os.makedirs(self.normal_dir, exist_ok=True)
        os.makedirs(self.others_dir, exist_ok=True)
        
        self.audio_files = [f for f in os.listdir(self.audio_dir) 
                           if f.endswith(('.wav', '.WAV')) and 
                           os.path.isfile(os.path.join(self.audio_dir, f))]
        self.current_idx = 0
        
        self.fig = plt.Figure(figsize=(8, 4))
        self.ax = self.fig.add_subplot(111)
        
        self.setup_ui()
        
    def setup_ui(self):
        # 顶部信息框架
        info_frame = ttk.Frame(self.root)
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 文件名标签和输入框
        ttk.Label(info_frame, text="当前文件: ").pack(side=tk.LEFT)
        self.filename_entry = ttk.Entry(info_frame, width=50)
        self.filename_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 复制按钮
        ttk.Button(info_frame, text="复制文件名", command=self.copy_filename).pack(side=tk.LEFT, padx=5)
        
        # 采样率信息显示
        self.sr_info_var = tk.StringVar()
        ttk.Label(self.root, textvariable=self.sr_info_var).pack(pady=2)
        
        # 添加matplotlib画布
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 按钮框架
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=5)
        
        # 标注按钮
        ttk.Button(btn_frame, text="正常咔哒声 (1)", 
                  command=lambda: self.label_audio(True)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="异常/无咔哒声 (2)", 
                  command=lambda: self.label_audio(False)).pack(side=tk.LEFT, padx=5)
        
        # 进度显示
        self.progress_var = tk.StringVar()
        ttk.Label(self.root, textvariable=self.progress_var).pack(pady=5)
        
        # 绑定快捷键
        self.root.bind('1', lambda e: self.label_audio(True))
        self.root.bind('2', lambda e: self.label_audio(False))
        self.root.bind('<Control-c>', lambda e: self.copy_filename())
        
        self.update_display()
        
    def label_audio(self, is_normal):
        if self.current_idx < len(self.audio_files):
            src = os.path.join(self.audio_dir, self.audio_files[self.current_idx])
            dst_dir = self.normal_dir if is_normal else self.others_dir
            dst = os.path.join(dst_dir, self.audio_files[self.current_idx])
            os.rename(src, dst)
            self.current_idx += 1
            self.update_display()
            
    def load_and_resample_audio(self, audio_path):
        y, sr = librosa.load(audio_path, sr=None)
        if sr != self.target_sr:
            y = librosa.resample(y, orig_sr=sr, target_sr=self.target_sr)
        return y, sr
            
    def plot_spectrogram(self, audio_path):
        self.fig.clear()
        self.ax = self.fig.add_subplot(111)
        
        y, orig_sr = self.load_and_resample_audio(audio_path)
        self.sr_info_var.set(f"原始采样率: {orig_sr} Hz → 目标采样率: {self.target_sr} Hz")
        
        D = librosa.stft(y, 
                        n_fft=self.n_fft,
                        hop_length=self.hop_length,
                        window=self.window)
        
        S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
        
        img = librosa.display.specshow(S_db, 
                                     y_axis='linear', 
                                     x_axis='time',
                                     sr=self.target_sr,
                                     hop_length=self.hop_length,
                                     ax=self.ax,
                                     vmin=-60,
                                     vmax=60)
        
        self.fig.colorbar(img, ax=self.ax, format="%+2.f dB")
        self.ax.set_title('频谱图')
        
        self.fig.tight_layout()
        self.canvas.draw()

    def update_display(self):
        if self.current_idx < len(self.audio_files):
            current_file = self.audio_files[self.current_idx]
            # 更新文件名输入框
            self.filename_entry.config(state='normal')
            self.filename_entry.delete(0, tk.END)
            self.filename_entry.insert(0, current_file)
            self.filename_entry.config(state='readonly')
            
            audio_path = os.path.join(self.audio_dir, current_file)
            self.plot_spectrogram(audio_path)
        else:
            self.filename_entry.config(state='normal')
            self.filename_entry.delete(0, tk.END)
            self.filename_entry.insert(0, "已完成所有文件标注")
            self.filename_entry.config(state='readonly')
            self.sr_info_var.set("")
            self.fig.clear()
            self.ax = self.fig.add_subplot(111)
            self.ax.text(0.5, 0.5, '标注完成', 
                        horizontalalignment='center',
                        verticalalignment='center')
            self.canvas.draw()
            
        self.progress_var.set(f"进度: {self.current_idx}/{len(self.audio_files)}")

    def copy_filename(self):
        if self.current_idx < len(self.audio_files):
            self.root.clipboard_clear()
            self.root.clipboard_append(self.audio_files[self.current_idx])

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = AudioLabeler()
    app.run()