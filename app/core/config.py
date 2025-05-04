import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field
from typing import Dict, List, Optional, Any
from pydantic_settings import BaseSettings

# Đảm bảo load từ đường dẫn tuyệt đối
BASE_DIR = Path(__file__).resolve().parent.parent.parent
dotenv_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=dotenv_path)
print(f"Đã load biến môi trường từ: {dotenv_path}")
print(f"CHAT_MODEL từ env: {os.environ.get('CHAT_MODEL', 'không có')}")

# Đảm bảo biến môi trường OPENAI_MODEL được đặt
if not os.environ.get("OPENAI_MODEL") and os.environ.get("CHAT_MODEL"):
    os.environ["OPENAI_MODEL"] = os.environ.get("CHAT_MODEL")
    print(f"Đã đặt OPENAI_MODEL = {os.environ.get('OPENAI_MODEL')}")

class Settings(BaseSettings):
    """
    Cấu hình cho ứng dụng
    """
    # App settings
    APP_NAME: str = Field(default="Cosmetic Shop Chatbot", validation_alias="APP_NAME")
    API_PREFIX: str = Field(default="/api", validation_alias="API_PREFIX")
    DEBUG: bool = Field(default=False, validation_alias="DEBUG")
    PORT: int = Field(default=8000, validation_alias="PORT")
    CORS_ORIGINS: str = Field(default="http://localhost:3000,http://localhost:8080", validation_alias="CORS_ORIGINS")
    
    # API Keys
    OPENAI_API_KEY: str = Field(default="", validation_alias="OPENAI_API_KEY")
    
    # Spring Boot API settings
    SPRING_BOOT_API_URL: str = Field(default="http://localhost:8081", validation_alias="SPRING_BOOT_API_URL")
    SPRING_BOOT_TOKEN: str = Field(default="", validation_alias="SPRING_BOOT_TOKEN")
    
    # Vector DB settings
    VECTOR_DB_PATH: str = Field(default="./data/vector_db", validation_alias="VECTOR_DB_PATH")
    
    # Model settings
    EMBEDDING_MODEL: str = Field(
        default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", 
        validation_alias="EMBEDDING_MODEL"
    )
    CHAT_MODEL: str = Field(default="gpt-4o-mini-2024-07-18", validation_alias="CHAT_MODEL")
    
    # Chat settings
    MAX_TOKENS: int = Field(default=1024, validation_alias="MAX_TOKENS")
    TEMPERATURE: float = Field(default=0.7, validation_alias="TEMPERATURE")

    # MySQL Database URL
    DB_HOST: str = Field(default="localhost", validation_alias="DB_HOST")
    DB_PORT: str = Field(default="3306", validation_alias="DB_PORT")
    DB_USER: str = Field(default="root", validation_alias="DB_USER")
    DB_PASSWORD: str = Field(default="", validation_alias="DB_PASSWORD")
    DB_NAME: str = Field(default="cosmetic_chatbot", validation_alias="DB_NAME")
    
    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    # Milvus settings
    MILVUS_URI: str = Field(default="http://localhost:19530", validation_alias="MILVUS_URI")
    MILVUS_COLLECTION_NAME: str = Field(default="cosmo", validation_alias="MILVUS_COLLECTION_NAME")
    MILVUS_FORCE_RECREATE: bool = Field(default=False, validation_alias="MILVUS_FORCE_RECREATE")
    
    # OpenAI settings
    OPENAI_EMBEDDING_MODEL: str = Field(default="text-embedding-3-small", validation_alias="OPENAI_EMBEDDING_MODEL")
    OPENAI_API_BASE: str = Field(default="", validation_alias="OPENAI_API_BASE")
    OPENAI_API_TYPE: str = Field(default="", validation_alias="OPENAI_API_TYPE")
    OPENAI_API_VERSION: str = Field(default="", validation_alias="OPENAI_API_VERSION")

    API_KEY: str = Field(default="test-api-key", validation_alias="API_KEY")

    model_config = ConfigDict(
        env_file=dotenv_path,
        env_file_encoding="utf-8",
        extra="ignore"  # Cho phép các trường khác trong file .env mà không gây lỗi
    )

settings = Settings()
print(f"Cấu hình CHAT_MODEL từ settings: {settings.CHAT_MODEL}")

# Đảm bảo OPENAI_MODEL và CHAT_MODEL nhất quán
if settings.CHAT_MODEL and settings.CHAT_MODEL != os.environ.get("OPENAI_MODEL"):
    os.environ["OPENAI_MODEL"] = settings.CHAT_MODEL
    print(f"Đã đồng bộ OPENAI_MODEL thành {os.environ.get('OPENAI_MODEL')}")