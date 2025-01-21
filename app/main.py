from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.utils.logger import setup_logger
from app.config.settings import settings
from app.api import content  # 导入路由模块

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
    content.router, 
    prefix=settings.API_PREFIX,
    tags=["content"]
)

@app.on_event("startup")
async def startup_event():
    """
    应用启动事件。
    记录启动日志并执行启动时的初始化任务。
    """
    logger.info("Starting up UGC Content Generator...")

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
