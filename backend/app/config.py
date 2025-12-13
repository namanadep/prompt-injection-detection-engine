"""Configuration settings for the Prompt Injection Detection Engine."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Prompt Injection Detection Engine"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # CORS
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000"]
    
    # ML Models
    ML_MODEL_NAME: str = "distilbert-base-uncased"
    SENTENCE_TRANSFORMER_MODEL: str = "all-MiniLM-L6-v2"
    MODEL_CACHE_DIR: str = "./data/models"
    
    # ChromaDB
    CHROMA_PERSIST_DIR: str = "./data/chroma_db"
    CHROMA_COLLECTION_NAME: str = "injection_patterns"
    
    # Detection Thresholds
    RULE_CONFIDENCE_THRESHOLD: float = 0.7
    ML_CONFIDENCE_THRESHOLD: float = 0.8
    VECTOR_SIMILARITY_THRESHOLD: float = 0.85
    
    # Aggregator Weights
    RULE_WEIGHT: float = 0.4
    ML_WEIGHT: float = 0.4
    VECTOR_WEIGHT: float = 0.2
    
    # High confidence threshold for immediate flagging
    HIGH_CONFIDENCE_THRESHOLD: float = 0.8
    
    # Data Files
    INJECTION_PATTERNS_FILE: str = "./data/injection_patterns.json"
    KNOWN_ATTACKS_FILE: str = "./data/known_attacks.json"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

