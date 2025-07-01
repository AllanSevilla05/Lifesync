from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://user:password@localhost:5432/lifesync"
    
    # Security
    secret_key: str = "your-super-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # AI Services
    openai_api_key: Optional[str] = None
    llama_api_key: Optional[str] = None
    
    # File Upload
    upload_dir: str = "uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    
    # Notifications
    redis_url: str = "redis://localhost:6379"
    
    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()

