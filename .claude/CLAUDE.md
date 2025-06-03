# Python Boilerplate Project Configuration

This document outlines all the decisions and configurations made for this Python boilerplate project by Arthur Souza Rodrigues (arthrod@umich.edu).

## Project Overview

- **Name**: python-boilerplate
- **Version**: 0.1.0
- **Description**: Modern Python project boilerplate
- **License**: Apache-2.0 (requires attribution)
- **Python Version**: 3.13+ (focused exclusively on latest Python)

## Core Dependencies

### Runtime Dependencies
- **loguru>=0.7.2**: Advanced logging with environment-based configuration
- **click>=8.1.7**: Modern CLI framework
- **uvloop>=0.21.0**: High-performance event loop (Unix/Linux only)
- **unkey-py>=0.6.2**: Secure API key management with Unkey
- **python-dotenv>=1.0.0**: Environment variable management

### Development Dependencies (by group)

#### Test Group
- **pytest>=8.3.4**: Testing framework
- **pytest-cov>=6.0.0**: Coverage reporting
- **pytest-asyncio>=0.25.2**: Async test support
- **pytest-mock>=3.14.0**: Mocking utilities
- **pytest-sugar>=1.0.0**: Enhanced test output

#### Dev Group
- **pytest-watcher>=0.4.3**: Live test watching
- **ipython>=8.31.0**: Enhanced REPL
- **pre-commit>=4.0.1**: Git hooks for quality
- **nox>=2025.2.9**: Task automation
- **nox-uv>=0.2.1**: UV integration for nox
- **typer>=0.15.1**: Beautiful CLI framework for scripts
- **rich>=13.9.4**: Rich text and beautiful formatting

#### Lint Group
- **ruff>=0.9.2**: Fast linting and formatting
- **mypy>=1.14.1**: Static type checking
- **pyrefly>=0.16.1**: Advanced type checking
- **types-click**: Type stubs for click

## Tool Configurations

### UV Package Manager
- **Default groups**: test, dev, lint
- **Lock file**: uv.lock for reproducible builds
- **Tool integration**: Used throughout CI/CD

### Ruff (Linting & Formatting)
- **Line length**: 140 characters
- **Target version**: py313
- **Quote style**: Double quotes
- **Auto-fix**: Enabled for UP, I, D rules
- **Comprehensive rules**: 20+ rule categories
- **Per-file ignores**: Tests and __init__.py exceptions
- **Docstring convention**: Google style

### Pytest Configuration
- **Async mode**: auto (automatic async test detection)
- **Coverage**: 85% minimum threshold
- **Test files**: `**/*_test.py` pattern
- **Coverage reporting**: XML and terminal

### MyPy Configuration
- **Strict mode**: Enabled
- **Untyped definitions**: Disallowed
- **Target**: Python 3.13

### Pyrefly Configuration
- **Project includes**: ["src"]
- **Python version**: 3.13
- **Untyped behavior**: error
- **Generated code**: ignored
- **Platform**: linux

## Logging Configuration

### Development Environment
- **Level**: DEBUG
- **Format**: Colorized with full tracebacks
- **Output**: stdout only

### Production Environment
- **Level**: INFO
- **Format**: JSON structured logging
- **Output**: stdout + rotated files (10MB, 30 days retention)
- **Compression**: gzip

## Project Structure

```
src/
├── python_boilerplate/
│   ├── __init__.py          # Package metadata
│   ├── add.py              # Example math operations
│   ├── cli.py              # Click-based CLI with key management
│   ├── config.py           # Configuration with API key management
│   └── logging_config.py   # Environment-based logging
tests/
├── __init__.py
├── conftest.py
└── test_*.py
.devcontainer/              # VS Code dev container
├── devcontainer.json       # UV + pyrefly configuration
└── Dockerfile.dev         # Multi-stage build with Oh My Zsh
.github/
├── workflows/
│   ├── ci.yml             # Nox-based CI pipeline
│   └── release.yml        # Tag-based releases with Docker
└── ENVIRONMENT_SETUP.md   # Security documentation
.claude/                   # AI communication directory
└── CLAUDE.md             # This file
setup_project.py           # Beautiful project setup script
manage_keys.py             # Gorgeous API key management script
```

## CI/CD Pipeline

### Continuous Integration (ci.yml)
- **Triggers**: Push to main/develop, PRs to main
- **Jobs**: Parallel nox sessions (tests, lint, mypy, security)
- **Docker**: Builds on main branch only
- **Environment protection**: production environment required

### Release Workflow (release.yml)
- **Triggers**: Version tags (v*)
- **Security**: Environment protection for all deployments
- **Outputs**: GitHub releases, Docker images, PyPI packages
- **Multi-arch**: AMD64 and ARM64 support

## Development Container

### Base Image
- **Image**: ghcr.io/astral-sh/uv:python3.13-bookworm-slim
- **Shell**: Zsh with Oh My Zsh
- **Dependencies**: Cached multi-stage build

### VS Code Extensions
- **ms-python.vscode-pylance**: Python language server
- **meta.pyrefly**: Advanced type checking
- **charliermarsh.ruff**: Linting and formatting

## Nox Task Automation

### Available Sessions
- **tests**: Run pytest with coverage
- **lint**: Ruff checking and formatting
- **mypy**: Type checking
- **security**: Bandit security scanning
- **format**: Auto-format code (dev use)
- **docs**: Documentation building (placeholder)

## Security & Quality

### Pre-commit Hooks
- Trailing whitespace removal
- File format validation (YAML, TOML, JSON)
- Ruff linting and formatting
- MyPy type checking
- Bandit security scanning

### Environment Protection
- **production**: Docker image builds (manual approval)
- **release**: GitHub releases (manual approval)
- **pypi**: Package publishing (manual approval)

## CLI Application

### Entry Point
- **Command**: `python-boilerplate`
- **Framework**: Click with logging integration
- **Examples**: add-numbers, multiply-numbers commands

## Key Design Decisions

1. **Python 3.13 Only**: Focus on latest features, no backward compatibility
2. **UV Package Manager**: Fastest dependency resolution and installation
3. **Nox over Tox**: Modern task automation with UV integration
4. **Environment-based Logging**: Automatic dev/prod configuration
5. **Comprehensive Linting**: 20+ rule categories with smart ignores
6. **Security First**: Environment protection, multi-layer Docker builds
7. **Type Safety**: Strict mypy + pyrefly for enhanced checking
8. **Apache 2.0 License**: Requires attribution, patent protection included

## Performance Optimizations

- **uvloop**: High-performance event loop for async operations
- **Docker caching**: Multi-stage builds with optimal layer caching
- **Parallel CI**: Nox matrix strategy for concurrent job execution
- **UV tool**: Fastest Python package management available

## Future Considerations

- Documentation generation (placeholder in nox)
- Additional CLI commands as needed
- Integration with monitoring tools in production
- Extension of logging for structured application metrics
EOF < /dev/null