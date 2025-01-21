#!/bin/bash

# 检查是否已安装uv
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# 检查虚拟环境是否存在
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    uv venv
fi

# 激活虚拟环境
source .venv/bin/activate

# 检查依赖是否已安装
if [ ! -f ".venv/pyvenv.cfg" ]; then
    echo "Installing dependencies..."
    uv pip install -e ".[dev]"
fi

# 启动应用
echo "Starting UGC Content Generator..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080 