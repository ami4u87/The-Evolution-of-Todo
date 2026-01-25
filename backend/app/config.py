"""Application configuration using Pydantic Settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = "postgresql://user:password@localhost:5432/todo_db"

    # Authentication
    better_auth_secret: str
    jwt_algorithm: str = "HS256"

    # API
    api_prefix: str = "/api"
    debug: bool = False

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:3003"]

    # AI Provider (supports "openai" or "groq")
    ai_provider: str = "groq"

    # OpenAI (if using OpenAI)
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    # Groq (free alternative - get key at https://console.groq.com)
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


# Global settings instance
settings = Settings()
