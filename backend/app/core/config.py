"""应用配置"""
from functools import lru_cache
from typing import List
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""

    # 应用信息
    APP_NAME: str = "Mini ITSM"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # 数据库
    DATABASE_URL: str = "mysql+aiomysql://root:11111111@localhost:3306/mini_itsm"

    # JWT 配置
    JWT_SECRET_KEY: str = "mini-itsm-secret-key-2024-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # 密码配置
    PASSWORD_MIN_LENGTH: int = 8

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
    )

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
