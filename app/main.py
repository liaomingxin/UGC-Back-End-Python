from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from app.utils.logger import setup_logger
from app.config.settings import settings
from app.api.content import router as content_router
import os
from pathlib import Path
from fastapi.exceptions import RequestValidationError
import json
import time

# 设置日志记录器
logger = setup_logger()

# 创建 FastAPI 应用实例
app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
)

# 配置跨域资源共享（CORS）中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# 注册 API 路由
app.include_router(
    content_router, 
    prefix="/api",  # 直接硬编码
    tags=["content"]
)

# 添加调试信息
for route in app.routes:
    logger.info(f"Registered route: {route.path}")

@app.on_event("startup")
async def startup_event():
    """
    应用启动事件。
    """
    logger.info("Starting up UGC Content Generator...")
    
    # 检查 ChromeDriver 环境
    chrome_driver_path = settings.CHROME_DRIVER_PATH
    if chrome_driver_path:
        driver_path = Path(chrome_driver_path)
        if driver_path.exists():
            import os, stat
            st = os.stat(driver_path)
            is_executable = bool(st.st_mode & stat.S_IXUSR)
            logger.info(f"ChromeDriver found at: {chrome_driver_path}")
            logger.info(f"ChromeDriver is executable: {is_executable}")
            
            # 检查版本
            import subprocess
            try:
                result = subprocess.run([chrome_driver_path, '--version'], 
                                     capture_output=True, text=True)
                logger.info(f"ChromeDriver version: {result.stdout.strip()}")
            except Exception as e:
                logger.error(f"Error checking ChromeDriver version: {str(e)}")
        else:
            logger.warning(f"ChromeDriver not found at: {chrome_driver_path}")

@app.on_event("shutdown")
async def shutdown_event():
    """
    应用关闭事件。
    记录关闭日志并执行关闭前的清理任务。
    """
    logger.info("Shutting down UGC Content Generator...")

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "code": exc.status_code
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """
    处理请求验证错误，返回详细的错误信息
    """
    logger.error(f"Validation error: {str(exc)}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": [
                {
                    "loc": err["loc"],
                    "msg": err["msg"],
                    "type": err["type"]
                }
                for err in exc.errors()
            ]
        }
    )

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录所有请求和响应的中间件"""
    # 记录请求开始时间
    start_time = time.time()
    
    # 获取请求体
    body = await request.body()
    if body:
        try:
            body_text = body.decode()
            # 尝试解析 JSON
            try:
                body_json = json.loads(body_text)
                logger.info(f"Request {request.method} {request.url.path}")
                logger.info(f"Request body: {json.dumps(body_json, ensure_ascii=False, indent=2)}")
            except json.JSONDecodeError:
                logger.info(f"Request body (raw): {body_text}")
        except:
            logger.info(f"Request body: <binary>")
    
    # 处理请求
    response = await call_next(request)
    
    # 计算处理时间
    process_time = time.time() - start_time
    
    # 记录响应
    response_body = b""
    async for chunk in response.body_iterator:
        response_body += chunk
    
    # 尝试解析响应体
    try:
        response_json = json.loads(response_body)
        logger.info(f"Response ({response.status_code}) took {process_time:.2f}s:")
        logger.info(f"Response body: {json.dumps(response_json, ensure_ascii=False, indent=2)}")
    except:
        logger.info(f"Response body (raw): {response_body.decode()}")
    
    # 重建响应
    return Response(
        content=response_body,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type
    )
