"""Tests for the config module."""

import os
from unittest.mock import patch

from newdotfiles.config import Config


def test_config_defaults():
    """Test config default values."""
    config = Config()
    assert config.environment == "development"
    assert config.debug is False
    assert config.log_level == "INFO"


def test_config_with_env_vars():
    """Test config with environment variables."""
    with patch.dict(os.environ, {"ENVIRONMENT": "production", "DEBUG": "true", "LOG_LEVEL": "DEBUG"}):
        config = Config()
        assert config.environment == "production"
        assert config.debug is True
        assert config.log_level == "DEBUG"


def test_get_api_key():
    """Test API key retrieval."""
    config = Config()

    # Test missing key
    assert config.get_api_key("nonexistent") is None

    # Test existing key
    with patch.dict(os.environ, {"TEST_API_KEY": "secret123"}):
        assert config.get_api_key("test") == "secret123"


def test_get_database_url():
    """Test database URL retrieval."""
    config = Config()

    # Test missing URL
    assert config.get_database_url() is None

    # Test existing URL
    with patch.dict(os.environ, {"DATABASE_URL": "postgresql://test"}):
        assert config.get_database_url() == "postgresql://test"


def test_get_unkey_config():
    """Test Unkey configuration."""
    config = Config()

    # Test default (empty) config
    unkey_config = config.get_unkey_config()
    assert unkey_config["root_key"] is None
    assert unkey_config["api_id"] is None

    # Test with values
    with patch.dict(os.environ, {"UNKEY_ROOT_KEY": "root123", "UNKEY_API_ID": "api456"}):
        unkey_config = config.get_unkey_config()
        assert unkey_config["root_key"] == "root123"
        assert unkey_config["api_id"] == "api456"


def test_validate_required_keys():
    """Test required keys validation."""
    config = Config()

    # Test with missing keys
    assert config.validate_required_keys(["missing1", "missing2"]) is False

    # Test with existing keys
    with patch.dict(os.environ, {"TEST_API_KEY": "secret"}):
        assert config.validate_required_keys(["test"]) is True

    # Test empty list
    assert config.validate_required_keys([]) is True


def test_to_dict():
    """Test config dictionary export."""
    config = Config()
    config_dict = config.to_dict()

    assert "environment" in config_dict
    assert "debug" in config_dict
    assert "log_level" in config_dict
    assert "database_url" in config_dict
    assert "unkey_configured" in config_dict

    assert config_dict["environment"] == "development"
    assert config_dict["debug"] is False
