import argparse
import json
import shutil
from pathlib import Path
from feature_extractor import AudioFeatureExtractor
from feature_cluster import AudioClusterer
from audio_utils import get_wav_files, print_clustering_results
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def save_results_and_organize_files(clusters, input_dir, output_dir=None):
    """
    保存聚类结果为JSON并将文件按类别整理到子目录
    
    Args:
        clusters (dict): 聚类结果字典
        input_dir (str): 输入目录路径
        output_dir (str, optional): 输出目录路径，默认为input_dir下的classified_结果
    """
    try:
        # 创建时间戳
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 如果没有指定输出目录，则在输入目录下创建
        if output_dir is None:
            output_dir = os.path.join(input_dir, f'classified_{timestamp}')
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 准备JSON数据
        json_data = {
            "clustering_time": timestamp,
            "total_clusters": len(clusters),
            "clusters": {}
        }
        
        # 处理每个聚类
        for cluster_id, files in clusters.items():
            # 创建聚类子目录
            cluster_dir = os.path.join(output_dir, f'cluster_{cluster_id}')
            os.makedirs(cluster_dir, exist_ok=True)
            
            # 复制文件到对应子目录
            cluster_files = []
            for file_path in files:
                # 获取文件名
                file_name = os.path.basename(file_path)
                # 目标路径
                dest_path = os.path.join(cluster_dir, file_name)
                # 复制文件
                shutil.copy2(file_path, dest_path)
                cluster_files.append(file_name)
            
            # 添加到JSON数据
            json_data["clusters"][f"cluster_{cluster_id}"] = {
                "file_count": len(cluster_files),
                "files": cluster_files
            }
        
        # 保存JSON文件
        json_path = os.path.join(output_dir, 'clustering_results.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4)
            
        logger.info(f"Results saved to: {output_dir}")
        logger.info(f"JSON file saved as: {json_path}")
        
        return output_dir, json_path
        
    except Exception as e:
        logger.error(f"Error saving results: {str(e)}")
        raise

def main():
    parser = argparse.ArgumentParser(description='Audio clustering tool')
    parser.add_argument('--input_dir', required=True, help='Directory containing WAV files')
    parser.add_argument('--output_dir', help='Directory to save clustered files (optional)')
    parser.add_argument('--model_type', default='clap', 
                        choices=['panns', 'clap', 'wav2vec'],
                        help='Type of feature extraction model to use')
    parser.add_argument('--n_clusters', type=int, default=5,
                        help='Number of clusters')
    parser.add_argument('--model_path', default='./model_cache',
                        help='Path to the local model directory')
    parser.add_argument('--offline', action='store_true',
                        help='Run in offline mode using local model files')
    
    args = parser.parse_args()

    try:
        # 设置离线模式环境变量
        if args.offline:
            os.environ['HF_HUB_OFFLINE'] = '1'
            os.environ['TRANSFORMERS_OFFLINE'] = '1'

        # 获取音频文件
        wav_files = get_wav_files(args.input_dir)
        if not wav_files:
            logger.error(f"No WAV files found in {args.input_dir}")
            return

        # 初始化特征提取器和聚类器
        feature_extractor = AudioFeatureExtractor(
            model_type=args.model_type,
            model_path=args.model_path,
            offline_mode=args.offline
        )
        clusterer = AudioClusterer(feature_extractor, n_clusters=args.n_clusters)

        # 执行聚类
        clusters = clusterer.cluster(wav_files)

        # 打印结果
        logger.info(f"\nClustering results using {args.model_type} model:")
        print_clustering_results(clusters)

        # 保存结果并整理文件
        output_dir, json_path = save_results_and_organize_files(
            clusters, 
            args.input_dir,
            args.output_dir
        )
        
        logger.info(f"\nResults have been saved to: {output_dir}")
        logger.info(f"JSON results file: {json_path}")

    except Exception as e:
        logger.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()