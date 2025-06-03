"""Application configuration with secure API key management."""

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from loguru import logger


class Config:
    """Application configuration with environment-based settings."""

    def __init__(self, env_file: str | None = None):
        """Initialize configuration with optional env file."""
        if env_file:
            env_path = Path(env_file)
        else:
            env_path = Path(".env")

        if env_path.exists():
            load_dotenv(env_path)
            logger.debug(f"Loaded environment from {env_path}")
        else:
            logger.warning(f"Environment file not found: {env_path}")

    @property
    def environment(self) -> str:
        """Get current environment."""
        return os.getenv("ENVIRONMENT", "development")

    @property
    def debug(self) -> bool:
        """Get debug mode setting."""
        return os.getenv("DEBUG", "false").lower() == "true"

    @property
    def log_level(self) -> str:
        """Get logging level."""
        return os.getenv("LOG_LEVEL", "INFO")

    def get_api_key(self, service: str) -> str | None:
        """Get API key for a specific service."""
        key_name = f"{service.upper().replace('-', '_')}_API_KEY"
        key = os.getenv(key_name)

        if key:
            logger.debug(f"Found API key for {service}")
            return key
        logger.warning(f"API key not found for {service} (looking for {key_name})")
        return None

    def get_database_url(self) -> str | None:
        """Get database connection URL."""
        return os.getenv("DATABASE_URL")

    def get_unkey_config(self) -> dict[str, str | None]:
        """Get Unkey configuration."""
        return {
            "root_key": os.getenv("UNKEY_ROOT_KEY"),
            "api_id": os.getenv("UNKEY_API_ID"),
        }

    def validate_required_keys(self, required_services: list[str]) -> bool:
        """Validate that all required API keys are present."""
        missing_keys = [service for service in required_services if not self.get_api_key(service)]

        if missing_keys:
            logger.error(f"Missing required API keys: {missing_keys}")
            logger.info("Run 'python manage_keys.py create' to add missing keys")
            return False

        logger.info("All required API keys are present")
        return True

    def to_dict(self) -> dict[str, Any]:
        """Export configuration as dictionary."""
        return {
            "environment": self.environment,
            "debug": self.debug,
            "log_level": self.log_level,
            "database_url": self.get_database_url(),
            "unkey_configured": bool(self.get_unkey_config()["root_key"]),
        }


# Global configuration instance
config = Config()
