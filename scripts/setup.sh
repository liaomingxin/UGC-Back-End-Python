#!/bin/bash

# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 创建虚拟环境
uv venv

# 激活虚拟环境
source .venv/bin/activate

# 使用 uv 安装依赖
uv pip install -e ".[dev]" 