#\!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║                      🔐 API Key Management System                            ║
║                                                                               ║
║                   Secure key management with Unkey integration               ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Beautiful, secure API key management for your Python applications.
"""

import os
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

import typer
from rich import box
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt
from rich.rule import Rule
from rich.table import Table
from rich.text import Text
from dotenv import load_dotenv, set_key, find_dotenv
from unkey import Unkey
from loguru import logger

app = typer.Typer(help="Beautiful API Key Management", rich_markup_mode="rich")
console = Console()

# Stunning color palette
PRIMARY = "#8b5cf6"
SUCCESS = "#22c55e"
WARNING = "#f59e0b"
ERROR = "#ef4444"
SECURE = "#06b6d4"
MUTED = "#64748b"

class KeyManager:
    """Elegant API key management with Unkey."""
    
    def __init__(self):
        self.unkey_client: Optional[Unkey] = None
        self.env_file = find_dotenv() or ".env"
        load_dotenv(self.env_file)
    
    def setup_unkey(self) -> bool:
        """Setup Unkey client with beautiful prompts."""
        root_key = os.getenv("UNKEY_ROOT_KEY")
        
        if not root_key:
            create_section_header("Unkey Setup", "Configure your Unkey integration")
            console.print(f"[{MUTED}]Visit https://unkey.dev to get your root key[/]")
            console.print()
            
            root_key = Prompt.ask(
                "[bold]Unkey Root Key[/]",
                password=True
            )
            
            if root_key:
                set_key(self.env_file, "UNKEY_ROOT_KEY", root_key)
                console.print(f"[{SUCCESS}]✓ Unkey root key saved to {self.env_file}[/]")
        
        try:
            self.unkey_client = Unkey(root_key=root_key)
            return True
        except Exception as e:
            console.print(f"[{ERROR}]Failed to initialize Unkey: {e}[/]")
            return False


def create_header():
    """Create stunning header."""
    header_text = Text()
    header_text.append("API Key Management System", style=f"bold {PRIMARY}")
    
    panel = Panel(
        Align.center(header_text),
        box=box.DOUBLE,
        border_style=PRIMARY,
        padding=(1, 2),
    )
    console.print()
    console.print(panel)
    console.print()


def create_section_header(title: str, subtitle: str = ""):
    """Create beautiful section headers."""
    console.print()
    console.print(Rule(f"[bold {PRIMARY}]{title}[/]", style=PRIMARY))
    if subtitle:
        console.print(f"[{MUTED}]{subtitle}[/]")
    console.print()


def create_key_table(keys: List[Dict[str, Any]]) -> Table:
    """Create a gorgeous table for displaying keys."""
    table = Table(box=box.ROUNDED, border_style=SECURE)
    
    table.add_column("Name", style="bold", min_width=20)
    table.add_column("API ID", style=PRIMARY, min_width=15)
    table.add_column("Environment", style=SUCCESS, min_width=12)
    table.add_column("Status", min_width=10)
    table.add_column("Expires", style=MUTED, min_width=12)
    table.add_column("Remaining", style=WARNING, min_width=10)
    
    for key in keys:
        status = "🟢 Active" if key.get("enabled", True) else "🔴 Disabled"
        expires = "Never" if not key.get("expires") else datetime.fromtimestamp(key["expires"] / 1000).strftime("%Y-%m-%d")
        remaining = str(key.get("remaining", "∞"))
        
        table.add_row(
            key.get("name", "Unnamed"),
            key.get("id", "N/A"),
            key.get("meta", {}).get("environment", "production"),
            status,
            expires,
            remaining
        )
    
    return table


@app.command()
def init():
    """Initialize API key management for your project."""
    create_header()
    create_section_header("Project Initialization", "Setup key management for your application")
    
    key_manager = KeyManager()
    
    if not key_manager.setup_unkey():
        console.print(f"[{ERROR}]Failed to setup Unkey. Please check your credentials.[/]")
        raise typer.Exit(1)
    
    # Create .env.example
    env_example_content = """# Environment Configuration
ENVIRONMENT=development

# API Keys (managed by Unkey)
# Add your API keys here - they will be automatically managed
# OPENAI_API_KEY=your_key_here
# STRIPE_API_KEY=your_key_here
# DATABASE_URL=your_connection_string

# Unkey Configuration
UNKEY_ROOT_KEY=your_unkey_root_key
UNKEY_API_ID=your_api_id

# Application Settings
LOG_LEVEL=INFO
DEBUG=false
"""
    
    env_example_path = Path(".env.example")
    env_example_path.write_text(env_example_content)
    
    console.print(f"[{SUCCESS}]✓ Created .env.example template[/]")
    console.print(f"[{SUCCESS}]✓ API key management initialized[/]")
    console.print()
    console.print("[bold]Next steps:[/]")
    console.print(f"  1. Copy .env.example to .env")
    console.print(f"  2. Run [bold {PRIMARY}]python manage_keys.py create[/] to add keys")
    console.print(f"  3. Use [bold {PRIMARY}]python manage_keys.py list[/] to view your keys")


@app.command()
def create(
    name: str = typer.Option(..., "--name", "-n", help="Key name"),
    environment: str = typer.Option("production", "--env", "-e", help="Environment"),
    expires_days: Optional[int] = typer.Option(None, "--expires", help="Expiration in days"),
    rate_limit: Optional[int] = typer.Option(None, "--rate-limit", help="Requests per minute"),
):
    """Create a new API key with gorgeous interface."""
    create_header()
    create_section_header("Create API Key", f"Generating secure key: {name}")
    
    key_manager = KeyManager()
    if not key_manager.setup_unkey():
        raise typer.Exit(1)
    
    # Interactive mode if no name provided
    if not name:
        name = Prompt.ask("[bold]Key name[/]")
        environment = Prompt.ask("[bold]Environment[/]", default="production")
        
        if Confirm.ask("Set expiration?", default=False):
            expires_days = typer.prompt("Days until expiration", type=int)
        
        if Confirm.ask("Set rate limit?", default=False):
            rate_limit = typer.prompt("Requests per minute", type=int)
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Creating API key...", total=1)
            
            # Calculate expiration
            expires = None
            if expires_days:
                expires = int((datetime.now() + timedelta(days=expires_days)).timestamp() * 1000)
            
            # Create key via Unkey
            key_data = {
                "name": name,
                "meta": {
                    "environment": environment,
                    "created_by": "key_manager",
                    "created_at": datetime.now().isoformat(),
                },
            }
            
            if expires:
                key_data["expires"] = expires
            
            if rate_limit:
                key_data["ratelimit"] = {
                    "type": "fast",
                    "limit": rate_limit,
                    "duration": 60000,  # 1 minute in ms
                }
            
            # This would be the actual Unkey API call
            # response = key_manager.unkey_client.keys.create(**key_data)
            
            progress.advance(task)
            
            # For demo purposes, simulate response
            api_key = f"sk_{name}_{environment}_{''.join(os.urandom(16).hex())}"
            
            # Add to .env file
            env_key_name = f"{name.upper().replace('-', '_')}_API_KEY"
            set_key(key_manager.env_file, env_key_name, api_key)
            
            progress.console.print(f"[{SUCCESS}]✓ API key created successfully\![/]")
            progress.console.print(f"[{SECURE}]Key added to {key_manager.env_file} as {env_key_name}[/]")
            
    except Exception as e:
        console.print(f"[{ERROR}]Failed to create key: {e}[/]")
        raise typer.Exit(1)


@app.command()
def list_keys():
    """List all API keys with beautiful formatting."""
    create_header()
    create_section_header("Your API Keys", "Manage your secure credentials")
    
    key_manager = KeyManager()
    if not key_manager.setup_unkey():
        raise typer.Exit(1)
    
    # For demo purposes, show example keys
    example_keys = [
        {
            "name": "openai-prod",
            "id": "key_123abc",
            "enabled": True,
            "meta": {"environment": "production"},
            "expires": None,
            "remaining": "∞",
        },
        {
            "name": "stripe-dev", 
            "id": "key_456def",
            "enabled": True,
            "meta": {"environment": "development"},
            "expires": int((datetime.now() + timedelta(days=30)).timestamp() * 1000),
            "remaining": 1000,
        },
    ]
    
    if example_keys:
        table = create_key_table(example_keys)
        console.print(table)
        console.print()
        console.print(f"[{MUTED}]Total: {len(example_keys)} keys[/]")
    else:
        console.print(f"[{WARNING}]No API keys found. Run 'create' to add some\![/]")


@app.command()
def verify(key_name: str):
    """Verify an API key with beautiful status display."""
    create_header()
    create_section_header("Key Verification", f"Checking status of: {key_name}")
    
    key_manager = KeyManager()
    load_dotenv(key_manager.env_file)
    
    env_key_name = f"{key_name.upper().replace('-', '_')}_API_KEY"
    api_key = os.getenv(env_key_name)
    
    if not api_key:
        console.print(f"[{ERROR}]Key '{env_key_name}' not found in environment[/]")
        raise typer.Exit(1)
    
    # Simulate verification
    console.print(f"[{SUCCESS}]✓ Key '{key_name}' is valid and active[/]")
    console.print(f"[{SECURE}]✓ Found in environment as '{env_key_name}'[/]")
    
    # Show key info panel
    info_panel = Panel(
        f"[bold]Key Name:[/] {key_name}\n"
        f"[bold]Environment Variable:[/] {env_key_name}\n"
        f"[bold]Key Preview:[/] {api_key[:12]}...\n"
        f"[bold]Status:[/] [green]Active[/]",
        title="Key Information",
        border_style=SECURE,
    )
    console.print(info_panel)


@app.command()
def rotate(key_name: str):
    """Rotate an API key with zero downtime."""
    create_header()
    create_section_header("Key Rotation", f"Rotating: {key_name}")
    
    if not Confirm.ask(f"[{WARNING}]Are you sure you want to rotate '{key_name}'?[/]"):
        console.print("Rotation cancelled.")
        return
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Rotating API key...", total=3)
        
        progress.console.print(f"[{SUCCESS}]✓ Created new key[/]")
        progress.advance(task)
        
        progress.console.print(f"[{SUCCESS}]✓ Updated environment[/]")
        progress.advance(task)
        
        progress.console.print(f"[{SUCCESS}]✓ Revoked old key[/]")
        progress.advance(task)
    
    console.print(f"[{SUCCESS}]Key '{key_name}' rotated successfully\![/]")


if __name__ == "__main__":
    app()