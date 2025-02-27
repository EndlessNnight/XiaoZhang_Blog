from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # 数据库配置
    DATABASE_URL: str = "mysql+pymysql://root:960204Zly!!@localhost:3306/xiaozhangblog"
    
    # JWT配置
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24小时
    
    # 邮件配置
    EMAIL_HOST: str = os.getenv("EMAIL_HOST", "smtp.qq.com")
    EMAIL_PORT: int = int(os.getenv("EMAIL_PORT", "465"))
    EMAIL_USER: str = os.getenv("EMAIL_USER", "")
    EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD", "")
    
    # Jellyfin配置
    # JELLYFIN_URL: str = os.getenv("JELLYFIN_URL", "")
    # JELLYFIN_API_KEY: str = os.getenv("JELLYFIN_API_KEY", "")
    # JELLYFIN_USER_ID: str = os.getenv("JELLYFIN_USER_ID", "")
    JELLYFIN_URL: str = ""
    JELLYFIN_API_KEY: str = ""
    JELLYFIN_USER_ID: str = ""
    JELLYFIN_IGNORE_SSL: bool = False
    
    # TMDB配置
    TMDB_API_KEY: str = "459906f3a00258e919f2f6792482ae1b"
    TMDB_BASE_URL: str = "https://api.themoviedb.org/3"
    TMDB_IMAGE_BASE_URL: str = "https://image.tmdb.org/t/p/w500"
    
    # 上传文件配置
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 2 * 1024 * 1024  # 2MB

    
    # 添加新的配置字段

    MYSQL_ROOT_PASSWORD: str

    MYSQL_DATABASE: str = "xiaozhangblog"

    class Config:
        env_file = ".env"

settings = Settings() 