import os
from typing import List

def get_wav_files(directory: str) -> List[str]:
    """获取目录下所有wav文件的路径"""
    wav_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.wav'):
                wav_files.append(os.path.join(root, file))
    return wav_files

def print_clustering_results(clusters: dict):
    """打印聚类结果"""
    for cluster_idx, files in clusters.items():
        print(f"\nCluster {cluster_idx}:")
        for f in files:
            print(f"  {os.path.basename(f)}")