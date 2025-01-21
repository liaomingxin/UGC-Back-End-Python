@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

REM 检查是否已安装 uv
where uv >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo 正在安装 uv...
    curl -LsSf https://astral.sh/uv/install.sh -o install_uv.bat
    IF %ERRORLEVEL% NEQ 0 (
        echo 下载 uv 安装脚本失败，请检查网络连接。
        EXIT /B 1
    )
    REM 运行安装脚本
    call install_uv.bat
    IF %ERRORLEVEL% NEQ 0 (
        echo uv 安装失败，请检查安装脚本。
        EXIT /B 1
    )
    del install_uv.bat
)

REM 检查虚拟环境是否存在
IF NOT EXIST ".venv" (
    echo 正在创建虚拟环境...
    uv venv
    IF %ERRORLEVEL% NEQ 0 (
        echo 虚拟环境创建失败。
        EXIT /B 1
    )
)

REM 激活虚拟环境
CALL .venv\Scripts\activate.bat
IF %ERRORLEVEL% NEQ 0 (
    echo 虚拟环境激活失败。
    EXIT /B 1
)

REM 检查依赖是否已安装
IF NOT EXIST ".venv\pyvenv.cfg" (
    echo 正在安装依赖...
    uv pip install -e ".[dev]"
    IF %ERRORLEVEL% NEQ 0 (
        echo 依赖安装失败。
        CALL deactivate
        EXIT /B 1
    )
)

REM 启动应用
echo 正在启动 UGC Content Generator...
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

ENDLOCAL