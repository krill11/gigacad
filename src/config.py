"""
Configuration management for GigaCAD
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # Onshape API Configuration
    ONSHAPE_ACCESS_KEY: str = os.getenv("ONSHAPE_ACCESS_KEY", "")
    ONSHAPE_SECRET_KEY: str = os.getenv("ONSHAPE_SECRET_KEY", "")
    ONSHAPE_BASE_URL: str = os.getenv("ONSHAPE_BASE_URL", "https://cad.onshape.com")
    
    # LLM Configuration
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
    
    # Local LMStudio Configuration
    LMSTUDIO_BASE_URL: str = os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234/v1")
    LMSTUDIO_MODEL: str = os.getenv("LMSTUDIO_MODEL", "local-model")
    
    # Application Configuration
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration is present"""
        required_keys = [
            "ONSHAPE_ACCESS_KEY",
            "ONSHAPE_SECRET_KEY", 
            "GROQ_API_KEY"
        ]
        
        missing_keys = [key for key in required_keys if not getattr(cls, key)]
        
        if missing_keys:
            print(f"Missing required environment variables: {', '.join(missing_keys)}")
            return False
        
        return True

# Global config instance
config = Config() 