from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    """
    配置类，用于加载和存储应用程序的环境变量配置。
    """

    # Server Configuration
    APP_NAME: str = "UGC Content Generator"  # 应用名称
    DEBUG: bool = True  # 调试模式开关
    API_PREFIX: str = "/api"  # API 路由前缀

    # OpenAI Configuration
    OPENAI_API_KEY: str
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"

    # Selenium Configuration
    CHROME_DRIVER_PATH: Optional[str] = None

    # Database Configuration
    DATABASE_URL: str

    class Config:
        """
        Pydantic 配置类，用于指定环境变量文件。
        """
        env_file = ".env"

@lru_cache()
def get_settings():
    """
    获取配置实例，并通过 LRU 缓存优化。
    返回：
        Settings: 配置实例。
    """
    return Settings()

# 全局配置实例
settings = get_settings()
