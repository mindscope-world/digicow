"""
Configuration module for DigiCow Farmer Intelligence System
"""
from pydantic_settings import BaseSettings
from pydantic import validator
from typing import List, Union
import json


class Settings(BaseSettings):
    PROJECT_NAME: str = "DigiCow Farmer Intelligence"
    API_V1_STR: str = "/api/v1"
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Neo4j settings
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "password"
    NEO4J_DATABASE: str = "neo4j"

    # Security settings
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Redis settings
    REDIS_URL: str = "redis://localhost:6379"

    # ML Model paths
    MODEL_STORAGE_PATH: str = "/models"

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
