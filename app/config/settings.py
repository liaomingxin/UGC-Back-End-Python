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
    OPENAI_API_KEY: str  # OpenAI API 密钥
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"  # OpenAI API 基础 URL

    # Selenium Configuration 这里使用绝对路径了，最好改成相对路径
    # CHROME_DRIVER_PATH: str = 'D:/devolopment_tools/Cursor/workspace/UGC-Back-End-Python/app/resources/chromedriver.exe' # ChromeDriver 路径，可选
    CHROME_DRIVER_PATH: str = '/opt/homebrew/bin/chromedriver' # ChromeDriver 路径，可选
    # Database Configuration
    DATABASE_URL: str  # 数据库连接 URL

    class Config:
        """
        Pydantic 配置类，用于指定环境变量文件和大小写敏感性。
        """
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True  # 添加大小写敏感设置

@lru_cache()
def get_settings():
    """
    获取配置实例，并通过 LRU 缓存优化。

    返回：
        Settings: 配置实例。
    """
    settings = Settings()
    if settings.DEBUG:
        # 仅在调试模式下输出配置详情
        print(f"[DEBUG] Loaded Configuration:")
        print(f"  APP_NAME: {settings.APP_NAME}")
        print(f"  API_PREFIX: {settings.API_PREFIX}")
        print(f"  OPENAI_BASE_URL: {settings.OPENAI_BASE_URL}")
        print(f"  CHROME_DRIVER_PATH: {settings.CHROME_DRIVER_PATH}")
        print(f"  DATABASE_URL: {settings.DATABASE_URL}")
    return settings

# 全局配置实例
settings = get_settings()
