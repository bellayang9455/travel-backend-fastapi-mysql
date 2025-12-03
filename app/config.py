from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    mysql_user: str = "travel"
    mysql_password: str = "travel"
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_db: str = "travel_db"
    cors_origins: List[str] = ["http://localhost:3000"]
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    @property
    def database_url(self) -> str:
        # mysql+pymysql://user:password@host:port/dbname
        return f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}@{self.mysql_host}:{self.mysql_port}/{self.mysql_db}"
 
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
