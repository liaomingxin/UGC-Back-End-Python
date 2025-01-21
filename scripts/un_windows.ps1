# 检查是否已安装 uv
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Output "正在安装 uv..."
    try {
        Invoke-WebRequest -Uri "https://astral.sh/uv/install.sh" -OutFile "install_uv.ps1"
        .\install_uv.ps1
        Remove-Item "install_uv.ps1"
    }
    catch {
        Write-Error "uv 安装失败，请检查安装脚本或网络连接。"
        exit 1
    }
}

# 检查虚拟环境是否存在
if (-Not (Test-Path ".venv")) {
    Write-Output "正在创建虚拟环境..."
    uv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Error "虚拟环境创建失败。"
        exit 1
    }
}

# 激活虚拟环境
& .\.venv\Scripts\Activate.ps1
if ($LASTEXITCODE -ne 0) {
    Write-Error "虚拟环境激活失败。"
    exit 1
}

# 检查依赖是否已安装
if (-Not (Test-Path ".venv\pyvenv.cfg")) {
    Write-Output "正在安装依赖..."
    uv pip install -e ".[dev]"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "依赖安装失败。"
        deactivate
        exit 1
    }
}

# 启动应用
Write-Output "正在启动 UGC Content Generator..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080