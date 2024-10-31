# deploy/inference/start.sh
#!/bin/bash

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 激活虚拟环境（如果使用）
# source /path/to/your/venv/bin/activate

# 设置环境变量
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# 默认参数
HOST="0.0.0.0"
PORT="8000"
WORKERS="4"
LOG_LEVEL="info"
RELOAD="false"

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --host=*)
            HOST="${1#*=}"
            shift
            ;;
        --port=*)
            PORT="${1#*=}"
            shift
            ;;
        --workers=*)
            WORKERS="${1#*=}"
            shift
            ;;
        --log-level=*)
            LOG_LEVEL="${1#*=}"
            shift
            ;;
        --reload)
            RELOAD="true"
            shift
            ;;
        *)
            echo "Unknown parameter: $1"
            exit 1
            ;;
    esac
done

# 构建Python命令
CMD="python run.py --host=$HOST --port=$PORT --workers=$WORKERS --log-level=$LOG_LEVEL"
if [ "$RELOAD" = "true" ]; then
    CMD="$CMD --reload"
fi

# 启动服务
echo "Starting inference API server..."
echo "Command: $CMD"
cd "$SCRIPT_DIR" && $CMD