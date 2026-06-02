"""
配置文件
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""

    # 应用配置
    APP_NAME: str = "剩食猎人"
    DEBUG: bool = True
    VERSION: str = "1.0.0"

    # 服务配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # 数据库配置
    DATABASE_URL: str = ""  # 优先使用此配置，如 mysql+pymysql://... 或 dm+pymysql://...
    DB_TYPE: str = "mysql"  # 数据库类型：mysql 或 dameng
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "food_saver_hunter"

    @property
    def DATABASE_URL_COMPUTED(self) -> str:
        """数据库连接 URL"""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        
        if self.DB_TYPE == "dameng":
            # 达梦数据库连接（使用 dm+pymysql 方言）
            return f"dm+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        
        # MySQL 数据库连接
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def DATABASE_URL_ASYNC(self) -> str:
        """异步数据库连接 URL"""
        if self.DB_TYPE == "dameng":
            return f"dm+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        return f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # Redis 配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0

    @property
    def REDIS_URL(self) -> str:
        """Redis 连接 URL"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # JWT 配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # Access Token 有效期
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # Refresh Token 有效期

    # CORS 配置
    CORS_ORIGINS: List[str] = ["*"]

    # 文件上传配置
    UPLOAD_DIR: str = "/tmp/uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB

    # AI 服务配置（百度 AI）
    BAIDU_AI_APP_ID: str = ""
    BAIDU_AI_API_KEY: str = ""
    BAIDU_AI_SECRET_KEY: str = ""

    # OSS 配置（阿里云）
    OSS_ACCESS_KEY_ID: str = ""
    OSS_ACCESS_KEY_SECRET: str = ""
    OSS_BUCKET_NAME: str = ""
    OSS_ENDPOINT: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """获取配置（单例）"""
    return Settings()


settings = get_settings()
