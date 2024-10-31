import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import os
from typing import List, Dict

class AudioClusterer:
    def __init__(self, feature_extractor, n_clusters=5):
        self.feature_extractor = feature_extractor
        self.n_clusters = n_clusters
        self.scaler = StandardScaler()
        self.kmeans = KMeans(n_clusters=n_clusters, n_init=10)

    def cluster(self, wav_files: List[str]) -> Dict[int, List[str]]:
        if not wav_files:
            raise ValueError("No wav files provided")

        # 提取特征
        all_features = []
        valid_files = []

        for wav_path in wav_files:
            try:
                feature_vector = self.feature_extractor.extract_features(wav_path)
                all_features.append(feature_vector)
                valid_files.append(wav_path)
            except Exception as e:
                print(f"Error processing {wav_path}: {str(e)}")

        if len(valid_files) < self.n_clusters:
            raise ValueError(f"Not enough valid files for clustering")

        # 特征处理和聚类
        X = np.array(all_features)
        X_scaled = self.scaler.fit_transform(X)
        clusters = self.kmeans.fit_predict(X_scaled)

        # 整理聚类结果
        file_clusters = {}
        for i, cluster_idx in enumerate(clusters):
            if cluster_idx not in file_clusters:
                file_clusters[cluster_idx] = []
            file_clusters[cluster_idx].append(valid_files[i])

        return file_clusters