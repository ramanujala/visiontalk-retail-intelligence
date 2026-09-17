from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "VisionTalk Retail Intelligence"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    
    API_V1_STR: str = "/api/v1"
    PORT: int = 8000
    
    # CORS Configuration
    CORS_ORIGINS: Union[List[str], str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"]
    )
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
        
    # Database Configuration
    DATABASE_URL: str = "postgresql://visiontalk_user:visiontalk_password@localhost:5432/visiontalk_db"
    
    # Storage Configuration
    STORAGE_DIR: str = "storage_uploads"

    # Image Ingestion & Validation Limits
    MAX_IMAGE_SIZE_MB: int = 15
    MIN_IMAGE_WIDTH: int = 100
    MIN_IMAGE_HEIGHT: int = 100
    MAX_IMAGE_WIDTH: int = 8000
    MAX_IMAGE_HEIGHT: int = 8000
    ALLOWED_IMAGE_MIME_TYPES: List[str] = ["image/jpeg", "image/png", "image/webp"]

    # YOLO Object Detection Configuration
    YOLO_MODEL_PATH: str = "yolov8n.pt"
    YOLO_CONFIDENCE_THRESHOLD: float = 0.25
    YOLO_IOU_THRESHOLD: float = 0.45
    YOLO_DEVICE: str = "cpu"


    # JWT Authentication Configuration
    JWT_SECRET_KEY: str = Field(
        default="DEV_ONLY_SECRET_KEY_CHANGE_IN_PRODUCTION_32BYTES_LONG_KEY_12345",
        description="Secret key for signing JWT tokens"
    )
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
