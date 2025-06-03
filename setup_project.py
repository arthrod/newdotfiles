#\!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║                     🐍 Python Project Boilerplate Setup                      ║
║                                                                               ║
║                    Transform this template into your project                  ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝

A beautiful, interactive script to customize your Python project boilerplate.
"""

import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import typer
from rich import box
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

app = typer.Typer(help="Beautiful Python Project Setup", rich_markup_mode="rich")
console = Console()

# Color scheme
PRIMARY = "#6366f1"
SUCCESS = "#10b981" 
WARNING = "#f59e0b"
ERROR = "#ef4444"
MUTED = "#6b7280"

class ProjectConfig:
    """Project configuration container."""
    
    def __init__(self):
        self.project_name: str = ""
        self.package_name: str = ""
        self.description: str = ""
        self.author_name: str = ""
        self.author_email: str = ""
        self.github_username: str = ""
        self.repository_name: str = ""
        self.year: int = datetime.now().year
        self.license_type: str = "Apache-2.0"
        self.python_version: str = "3.13"


def create_header():
    """Create a beautiful header."""
    header_text = Text()
    header_text.append("Python Project Boilerplate Setup", style=f"bold {PRIMARY}")
    
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
    """Create a beautiful section header."""
    console.print()
    console.print(Rule(f"[bold {PRIMARY}]{title}[/]", style=PRIMARY))
    if subtitle:
        console.print(f"[{MUTED}]{subtitle}[/]")
    console.print()


def validate_project_name(name: str) -> bool:
    """Validate project name."""
    return bool(re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*$", name))


def validate_email(email: str) -> bool:
    """Validate email address."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_github_username(username: str) -> bool:
    """Validate GitHub username."""
    return bool(re.match(r"^[a-zA-Z0-9](?:[a-zA-Z0-9]|-(?=[a-zA-Z0-9])){0,38}$", username))


def to_snake_case(name: str) -> str:
    """Convert project name to snake_case for package name."""
    name = re.sub(r"[-\s]+", "_", name)
    name = re.sub(r"[^a-zA-Z0-9_]", "", name)
    return name.lower()


def collect_project_info() -> ProjectConfig:
    """Collect project information with beautiful prompts."""
    config = ProjectConfig()
    
    create_section_header("Project Information", "Tell us about your awesome project")
    
    # Project name
    while True:
        config.project_name = Prompt.ask(
            "[bold]Project name[/]",
            default="my-awesome-project"
        )
        if validate_project_name(config.project_name):
            config.package_name = to_snake_case(config.project_name)
            break
        console.print(f"[{ERROR}]Invalid project name. Use letters, numbers, hyphens, and underscores only.[/]")
    
    console.print(f"[{MUTED}]Package name will be: {config.package_name}[/]")
    
    # Description
    config.description = Prompt.ask(
        "[bold]Project description[/]",
        default="A modern Python project"
    )
    
    create_section_header("Author Information", "Who's the brilliant mind behind this?")
    
    # Author name
    config.author_name = Prompt.ask(
        "[bold]Your name[/]",
        default="Arthur Souza Rodrigues"
    )
    
    # Author email
    while True:
        config.author_email = Prompt.ask(
            "[bold]Your email[/]",
            default="arthrod@umich.edu"
        )
        if validate_email(config.author_email):
            break
        console.print(f"[{ERROR}]Please enter a valid email address.[/]")
    
    create_section_header("Repository Information", "Where will this masterpiece live?")
    
    # GitHub username
    while True:
        config.github_username = Prompt.ask(
            "[bold]GitHub username[/]",
            default="arthrod"
        )
        if validate_github_username(config.github_username):
            break
        console.print(f"[{ERROR}]Invalid GitHub username.[/]")
    
    # Repository name
    config.repository_name = Prompt.ask(
        "[bold]Repository name[/]",
        default=config.project_name
    )
    
    create_section_header("Project Settings", "Final touches for perfection")
    
    # Year
    config.year = IntPrompt.ask(
        "[bold]Copyright year[/]",
        default=datetime.now().year
    )
    
    # Python version
    python_versions = ["3.13", "3.12", "3.11"]
    console.print("[bold]Python version:[/]")
    for i, version in enumerate(python_versions, 1):
        marker = "●" if version == "3.13" else "○"
        color = SUCCESS if version == "3.13" else MUTED
        console.print(f"  [{color}]{marker}[/] {version}")
    
    version_choice = Prompt.ask(
        "Select version",
        choices=python_versions,
        default="3.13"
    )
    config.python_version = version_choice
    
    return config


def show_configuration_summary(config: ProjectConfig):
    """Display a beautiful configuration summary."""
    create_section_header("Configuration Summary", "Please review your choices")
    
    table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    table.add_column("Setting", style="bold")
    table.add_column("Value", style=PRIMARY)
    
    table.add_row("Project Name", config.project_name)
    table.add_row("Package Name", config.package_name)
    table.add_row("Description", config.description)
    table.add_row("Author", f"{config.author_name} <{config.author_email}>")
    table.add_row("Repository", f"github.com/{config.github_username}/{config.repository_name}")
    table.add_row("Python Version", config.python_version)
    table.add_row("License", config.license_type)
    table.add_row("Copyright Year", str(config.year))
    
    console.print(table)
    console.print()


def apply_configuration(config: ProjectConfig):
    """Apply the configuration to project files."""
    create_section_header("Applying Configuration", "Transforming your project...")
    
    files_to_update = [
        "pyproject.toml",
        "LICENSE",
        "README.md",
        ".github/workflows/ci.yml",
        ".github/workflows/release.yml",
        ".devcontainer/devcontainer.json",
        ".claude/CLAUDE.md",
    ]
    
    replacements = {
        "python-boilerplate": config.project_name,
        "python_boilerplate": config.package_name,
        "Modern Python project boilerplate": config.description,
        "Arthur Souza Rodrigues": config.author_name,
        "arthrod@umich.edu": config.author_email,
        "arthrod": config.github_username,
        "https://github.com/arthrod/python-boilerplate": f"https://github.com/{config.github_username}/{config.repository_name}",
        "[2025]": f"[{config.year}]",
        "requires-python = \">=3.13\"": f"requires-python = \">={config.python_version}\"",
        "python_version = \"3.13\"": f"python_version = \"{config.python_version}\"",
        "target-version = \"py313\"": f"target-version = \"py{config.python_version.replace('.', '')}\"",
    }
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Updating files...", total=len(files_to_update))
        
        for file_path in files_to_update:
            path = Path(file_path)
            if path.exists():
                content = path.read_text(encoding="utf-8")
                
                for old, new in replacements.items():
                    content = content.replace(old, new)
                
                path.write_text(content, encoding="utf-8")
                progress.console.print(f"  [{SUCCESS}]✓[/] Updated {file_path}")
            else:
                progress.console.print(f"  [{WARNING}]⚠[/] Skipped {file_path} (not found)")
            
            progress.advance(task)
    
    # Rename package directory
    old_package_dir = Path("src/python_boilerplate")
    new_package_dir = Path(f"src/{config.package_name}")
    
    if old_package_dir.exists() and old_package_dir \!= new_package_dir:
        old_package_dir.rename(new_package_dir)
        console.print(f"  [{SUCCESS}]✓[/] Renamed package directory to src/{config.package_name}")
        
        # Update CLI entry point
        cli_file = new_package_dir / "cli.py"
        if cli_file.exists():
            content = cli_file.read_text()
            content = content.replace("python_boilerplate", config.package_name)
            cli_file.write_text(content)


def create_success_message(config: ProjectConfig):
    """Create a beautiful success message."""
    console.print()
    
    success_panel = Panel(
        Align.center(
            Text("Project setup complete\!", style=f"bold {SUCCESS}")
        ),
        box=box.DOUBLE,
        border_style=SUCCESS,
        padding=(1, 2),
    )
    console.print(success_panel)
    
    console.print()
    console.print("[bold]Next steps:[/]")
    console.print(f"  1. [bold]cd[/] into your project directory")
    console.print(f"  2. Run [bold]{PRIMARY}]uv sync[/] to install dependencies")
    console.print(f"  3. Run [bold]{PRIMARY}]pre-commit install[/] to set up git hooks")
    console.print(f"  4. Start coding your amazing project\!")
    console.print()
    
    repo_url = f"https://github.com/{config.github_username}/{config.repository_name}"
    console.print(f"[{MUTED}]Repository URL: {repo_url}[/]")
    console.print()


@app.command()
def setup(
    interactive: bool = typer.Option(True, "--interactive/--batch", help="Run in interactive mode"),
):
    """Setup your Python project with style."""
    try:
        create_header()
        
        if not interactive:
            console.print(f"[{ERROR}]Batch mode not implemented yet. Use --interactive[/]")
            raise typer.Exit(1)
        
        config = collect_project_info()
        show_configuration_summary(config)
        
        if not Confirm.ask("\n[bold]Proceed with setup?[/]", default=True):
            console.print(f"[{WARNING}]Setup cancelled.[/]")
            raise typer.Exit(0)
        
        apply_configuration(config)
        create_success_message(config)
        
    except KeyboardInterrupt:
        console.print(f"\n[{WARNING}]Setup interrupted by user.[/]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"\n[{ERROR}]Setup failed: {e}[/]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()