"""Logging configuration for development and production environments."""

import os
import sys

from loguru import logger


def configure_logging(environment: str = "development") -> None:
    """Configure loguru logging based on environment.

    Args:
        environment: Either 'development' or 'production'
    """
    # Remove default handler
    logger.remove()

    if environment == "production":
        # Production: JSON format, INFO level, structured
        logger.add(
            sys.stdout,
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
            level="INFO",
            serialize=True,  # JSON output
            backtrace=False,
            diagnose=False,
        )
        # Add file rotation for production
        logger.add(
            "logs/app.log",
            rotation="10 MB",
            retention="30 days",
            compression="gz",
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
            level="INFO",
            serialize=True,
        )
    else:
        # Development: Colorized, DEBUG level, detailed
        logger.add(
            sys.stdout,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                "<level>{message}</level>"
            ),
            level="DEBUG",
            colorize=True,
            backtrace=True,
            diagnose=True,
        )


def setup_logging() -> None:
    """Setup logging based on environment variables."""
    environment = os.getenv("ENVIRONMENT", "development").lower()
    configure_logging(environment)

    logger.info(f"Logging configured for {environment} environment")


# Auto-configure on import
setup_logging()
