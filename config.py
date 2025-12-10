from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "mysql+pymysql://user:password@localhost/textcort")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "tu-clave-super-secreta-cambiar-en-produccion")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]  # acepta cualquier origen
    ALLOWED_HOSTS: List[str] = ["*"]  # acepta cualquier host
    
    # Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIRECTORY: str = "./uploads"
    ALLOWED_EXTENSIONS: List[str] = ["png", "jpg", "jpeg", "gif", "webp"]
    
    class Config:
        env_file = ".env"

settings = Settings()
