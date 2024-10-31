# deploy/inference/__init__.py
import sys
from pathlib import Path

# 将项目根目录添加到Python路径
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT_DIR))