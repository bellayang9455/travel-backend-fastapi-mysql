from pydantic_settings import BaseSettings
from typing import List
import google.generativeai as genai


class Settings(BaseSettings):
    database_url: str | None = None

    mysql_user: str = "travel"
    mysql_password: str = "travel"
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_db: str = "travel_db"

    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",

        "https://my-travel-frontend-eileb6t82-yyy-s-projects.vercel.app",
        "https://my-travel-frontend-phi.vercel.app",
        "https://my-travel-frontend-git-feature-xin-newwork-yyy-s-projects.vercel.app",
        "https://my-travel-frontend-8vlirsi75-yyy-s-projects.vercel.app",
    ]

    app_host: str = "0.0.0.0"
    app_port: int = 8000

    gemini_api_key: str = ""

    secret_key: str = "my_super_secret_key_123"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    @property
    def final_database_url(self) -> str:
        if self.database_url:
            return self.database_url

        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_db}"
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()

if settings.gemini_api_key:
    genai.configure(api_key=settings.gemini_api_key)