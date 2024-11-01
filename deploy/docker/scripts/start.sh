# deploy/scripts/start.sh
#!/bin/bash

# Windows用.bat文件
# @echo off
# if not exist "venv" (
#     python -m venv venv
#     call venv\Scripts\activate
#     pip install -r requirements.txt
# ) else (
#     call venv\Scripts\activate
# )
# uvicorn inference.app.main:app --host 0.0.0.0 --port 8000

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
    source venv/bin/activate
    pip install uvicorn
    # 先装最基础的包运行起来
    echo "Installing basic dependencies..."
fi

# 激活虚拟环境
source venv/bin/activate

# 检查并安装缺失的依赖
check_and_install_dependency() {
    python -c "import $1" 2>/dev/null || pip install $2
}

# 基础依赖检查
check_and_install_dependency "fastapi" "fastapi"
check_and_install_dependency "torch" "torch torchaudio"
check_and_install_dependency "librosa" "librosa"

# 启动服务
echo "Starting inference service..."
uvicorn inference.app.main:app --host 0.0.0.0 --port 8000 --reload