"""Application configuration via environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """App settings loaded from environment variables."""

    jwt_secret: str = "dev-secret-change-me"
    jwt_expiry_hours: int = 24
    port: int = 8080
    log_level: str = "info"

    # Cosmos DB settings — used when switching from in-memory to persistent storage
    cosmos_endpoint: str = ""
    cosmos_database: str = ""
    cosmos_container: str = ""

    model_config = {"env_prefix": "", "case_sensitive": False}


settings = Settings()
