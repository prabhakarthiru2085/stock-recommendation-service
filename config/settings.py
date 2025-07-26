import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Configuration
    API_TITLE: str = "Indian Stock Recommendation Service"
    API_DESCRIPTION: str = "AI-powered stock recommendations based on Screener.in data analysis"
    API_VERSION: str = "1.0.0"
    
    # Server Configuration
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = False
    
    # Scraping Configuration
    SCREENER_BASE_URL: str = "https://www.screener.in"
    REQUEST_TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    RATE_LIMIT_DELAY: float = 1.0
    
    # Cache Configuration
    CACHE_TTL: int = 3600  # 1 hour in seconds
    MAX_CACHE_SIZE: int = 1000
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Analysis Configuration
    MIN_QUARTERS_FOR_ANALYSIS: int = 4
    CONFIDENCE_THRESHOLD: float = 0.6
    
    # Security Configuration
    ALLOWED_ORIGINS: list = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()