"""Pytest configuration and fixtures for the test suite."""

import tempfile
from collections.abc import AsyncGenerator, Generator
from pathlib import Path
from typing import Any

import pytest
import uvloop
from loguru import logger


@pytest.fixture
def root_dir():
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent


@pytest.fixture(scope="session")
def event_loop_policy():
    """Use uvloop for all async tests."""
    return uvloop.EventLoopPolicy()


@pytest.fixture(scope="session")
async def async_session() -> AsyncGenerator[None, None]:
    """Session-scoped async fixture for setup/teardown."""
    logger.debug("Setting up async session")
    yield
    logger.debug("Tearing down async session")


@pytest.fixture
async def async_client() -> AsyncGenerator[None, None]:
    """Async client fixture for testing async operations."""
    logger.debug("Creating async client")
    yield
    logger.debug("Closing async client")


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as temp_path:
        yield Path(temp_path)


@pytest.fixture
def sample_data() -> dict[str, Any]:
    """Sample data for testing."""
    return {
        "name": "test_project",
        "version": "1.0.0",
        "numbers": [1, 2, 3, 4, 5],
        "config": {"debug": True, "timeout": 30},
    }


@pytest.fixture(autouse=True)
def configure_test_logging():
    """Configure logging for tests."""
    logger.remove()
    logger.add(
        lambda msg: None,  # Suppress logs during tests
        level="CRITICAL",
    )


@pytest.fixture
def mock_environment(monkeypatch):
    """Mock environment variables."""
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
