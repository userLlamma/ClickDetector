# deploy/inference/run.py
import uvicorn
import argparse
import os
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(description='Start the inference API server')
    
    parser.add_argument(
        '--host',
        type=str,
        default='0.0.0.0',
        help='Host to bind the server to'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='Port to bind the server to'
    )
    
    parser.add_argument(
        '--workers',
        type=int,
        default=1,
        help='Number of worker processes'
    )
    
    parser.add_argument(
        '--reload',
        action='store_true',
        help='Enable auto-reload on code changes'
    )
    
    parser.add_argument(
        '--log-level',
        type=str,
        default='info',
        choices=['debug', 'info', 'warning', 'error', 'critical'],
        help='Logging level'
    )
    
    return parser.parse_args()

def main():
    args = parse_args()
    
    # 确保在项目根目录下运行
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # 配置uvicorn启动参数
    config = {
        'app': 'app.main:app',  # FastAPI应用的导入路径
        'host': args.host,
        'port': args.port,
        'workers': args.workers,
        'reload': args.reload,
        'log_level': args.log_level,
        'proxy_headers': True,  # 支持代理头部
        'forwarded_allow_ips': '*',  # 允许的转发IP
        'timeout_keep_alive': 65,  # keep-alive超时时间
        'loop': 'auto',  # 事件循环策略
        'ws': 'auto',  # websocket协议
    }
    
    # 启动服务器
    uvicorn.run(**config)

if __name__ == '__main__':
    main()