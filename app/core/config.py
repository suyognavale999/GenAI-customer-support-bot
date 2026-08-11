from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "GenAI Customer Support Bot"
    app_version: str = "1.0.0"
    app_env: str = "development"
    debug: bool = False
    log_level: str = "INFO"

    api_prefix: str = "/api/v1"

    sqlite_database_url: str = "sqlite:///./data/sqlite/app_support.db"
    chroma_persist_directory: Path = Path("./data/chroma")
    upload_directory: Path = Path("./data/uploads")

    llm_provider: str = "openai"
    llm_api_key: str = Field(default="")
    llm_model: str = Field(default="")

    jwt_secret_key: str = "change-this-secret-key"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    default_admin_username: str = "admin"
    default_admin_email: str = "admin@example.com"
    default_admin_password: str = "Admin@123"
    
    chat_rate_limit: str = "10/minute"
    max_chat_history: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    chroma_collection_name: str = "app_knowledge_base"

    rag_top_k: int = 4
    rag_min_similarity: float = 0.30

    llm_api_key: str = ""
    llm_model: str = ""
    llm_base_url: str = ""

    def create_storage_directories(self):
        directories = [
            Path("./data/sqlite"),
            self.chroma_persist_directory,
            self.upload_directory,
            Path("./logs"),
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()