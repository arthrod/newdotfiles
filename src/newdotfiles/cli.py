"""Command line interface for newdotfiles."""

import click
from loguru import logger

from newdotfiles.add import add, multiply
from newdotfiles.config import Config, config


@click.group()
@click.version_option()
@click.option("--env-file", help="Path to environment file", default=".env")
def main(env_file: str) -> None:
    """Newdotfiles CLI with secure API key management."""
    # Import here to ensure logging is configured
    from newdotfiles import logging_config  # noqa: F401

    # Load configuration
    if env_file != ".env":
        # Reinitialize config with custom env file
        global config
        config = Config(env_file)

    logger.info(f"Starting newdotfiles CLI in {config.environment} mode")
    logger.debug(f"Configuration: {config.to_dict()}")


@main.command()
@click.argument("x", type=float)
@click.argument("y", type=float)
def add_numbers(x: float, y: float) -> None:
    """Add two numbers."""
    result = add(x, y)
    logger.info(f"Adding {x} + {y} = {result}")
    click.echo(f"{x} + {y} = {result}")


@main.command()
@click.argument("x", type=float)
@click.argument("y", type=float)
def multiply_numbers(x: float, y: float) -> None:
    """Multiply two numbers."""
    result = multiply(x, y)
    logger.info(f"Multiplying {x} * {y} = {result}")
    click.echo(f"{x} * {y} = {result}")


@main.command()
def config_info() -> None:
    """Display current configuration and API key status."""
    click.echo("📋 Current Configuration:")
    click.echo(f"  Environment: {config.environment}")
    click.echo(f"  Debug Mode: {config.debug}")
    click.echo(f"  Log Level: {config.log_level}")

    unkey_config = config.get_unkey_config()
    if unkey_config["root_key"]:
        click.echo("  🔐 Unkey: ✅ Configured")
    else:
        click.echo("  🔐 Unkey: ❌ Not configured")
        click.echo("    Run 'python manage_keys.py init' to setup")


@main.command()
@click.argument("service")
def check_key(service: str) -> None:
    """Check if an API key exists for a service."""
    key = config.get_api_key(service)
    if key:
        click.echo(f"✅ API key found for {service}")
        click.echo(f"   Key preview: {key[:12]}...")
    else:
        click.echo(f"❌ No API key found for {service}")
        click.echo(f"   Run 'python manage_keys.py create --name {service}' to add it")


@main.command()
@click.argument("services", nargs=-1, required=True)
def validate_keys(services: list[str]) -> None:
    """Validate that all required API keys are present."""
    if config.validate_required_keys(list(services)):
        click.echo("✅ All required API keys are present")
    else:
        click.echo("❌ Some required API keys are missing")
        click.echo("   Use the manage_keys.py script to add them")


if __name__ == "__main__":
    main()
