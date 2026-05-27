from pydantic_settings import BaseSettings
from typing import List
import google.generativeai as genai


class Settings(BaseSettings):
    # Render / Railway 用
    database_url: str | None = None

    # 本地開發用
    mysql_user: str = "travel"
    mysql_password: str = "travel"
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_db: str = "travel_db"

    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://my-travel-frontend-phi.vercel.app"
    ]

    app_host: str = "0.0.0.0"
    app_port: int = 8000

    # Gemini API
    gemini_api_key: str = ""

    # JWT
    secret_key: str = "my_super_secret_key_123"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    @property
    def final_database_url(self) -> str:
        # Render 有 DATABASE_URL 時優先使用
        if self.database_url:
            return self.database_url

        # 本地 fallback
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_db}"
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()

# Gemini 初始化
if settings.gemini_api_key:
    genai.configure(api_key=settings.gemini_api_key)