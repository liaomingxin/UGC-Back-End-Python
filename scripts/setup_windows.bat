@echo off

REM 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

REM 创建虚拟环境
uv venv

REM 激活虚拟环境
call .venv\Scripts\activate

REM 使用 uv 安装依赖
uv pip install -e ".[dev]"