from loguru import logger
import sys
from pathlib import Path

def setup_logger():
    """
    配置日志记录器。
    移除默认处理器并添加控制台和文件处理器，支持详细的日志格式和日志轮换。

    返回：
        logger: 配置完成的 Loguru 日志记录器实例。
    """
    # 创建日志目录（如果不存在）
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    # 移除默认处理器
    logger.remove()

    # 添加控制台处理器
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="DEBUG",
        enqueue=True  # 异步处理日志
    )

    # 添加文件处理器
    logger.add(
        log_dir / "app.log",
        rotation="500 MB",  # 文件大小超过 500 MB 时轮换
        retention="10 days",  # 保留 10 天内的日志文件
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="INFO",
        enqueue=True  # 异步处理日志
    )

    return logger