import os
from typing import Dict, Any, Optional
from pydantic import BaseSettings, validator
from functools import lru_cache

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Fraud Detection System"
    APP_VERSION: str = "2.1.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 30
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str
    KAFKA_TRANSACTIONS_TOPIC: str = "transactions"
    KAFKA_ALERTS_TOPIC: str = "fraud-alerts"
    KAFKA_GROUP_ID: str = "fraud-detection"
    
    # Redis
    REDIS_URL: str
    REDIS_POOL_SIZE: int = 20
    
    # Neo4j
    NEO4J_URI: str
    NEO4J_USER: str
    NEO4J_PASSWORD: str
    
    # ML Service
    ML_SERVICE_URL: str
    ML_MODEL_VERSION: str = "2.1.0"
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 900
    
    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    @validator("DATABASE_URL")
    def validate_database_url(cls, v):
        if not v:
            raise ValueError("DATABASE_URL is required")
        return v
    
    @validator("KAFKA_BOOTSTRAP_SERVERS")
    def validate_kafka_servers(cls, v):
        if not v:
            raise ValueError("KAFKA_BOOTSTRAP_SERVERS is required")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

# Export settings instance
settings = get_settings()