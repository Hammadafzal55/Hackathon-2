"""
Configuration settings for the Todo backend application.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional


class Settings(BaseSettings):
    """
    Application settings using Pydantic BaseSettings.
    """

    # App settings
    app_name: str = "Todo Backend API"
    app_description: str = "A FastAPI backend for managing todos"
    app_version: str = "1.0.0"
    debug: bool = False

    # Database settings
    database_url: str = Field(default="postgresql+asyncpg://username:password@localhost/dbname", alias="DATABASE_URL")

    # JWT settings
    jwt_secret_key: str = Field(alias="JWT_SECRET_KEY")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Better Auth settings
    better_auth_secret: str = Field(alias="BETTER_AUTH_SECRET")

    # CORS settings
    allowed_origins: List[str] = ["http://localhost:3000", "https://your-deployment-url.vercel.app"]

    # Other application settings
    api_prefix: str = "/api"

    # MCP Server settings
    mcp_server_enabled: bool = Field(default=True, alias="MCP_SERVER_ENABLED")
    mcp_server_port: Optional[int] = Field(default=8001, alias="MCP_SERVER_PORT")
    mcp_log_level: str = Field(default="INFO", alias="MCP_LOG_LEVEL")

    model_config = {"env_file": ".env", "case_sensitive": True}


def get_settings() -> Settings:
    """
    Get application settings instance.

    Returns:
        Settings: The application settings object
    """
    return Settings()