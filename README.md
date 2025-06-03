# 🐍 newdotfiles

A Python boilerplate project

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

## ✨ Features

- 🚀 Fast dependency management with [uv](https://github.com/astral-sh/uv)
- 🎯 Code linting and formatting with [Ruff](https://github.com/astral-sh/ruff)
- 🧪 Testing with [pytest](https://pytest.org/) and async support
- 🔧 Type checking with [mypy](https://mypy.readthedocs.io/)
- 🪝 Pre-commit hooks for code quality
- 🐳 Development container with VS Code support
- 📝 Comprehensive pyproject.toml configuration

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/arthrod/newdotfiles.git
cd newdotfiles
```

### 2. Install Dependencies

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies
uv sync
```

### 3. Setup Pre-commit Hooks

```bash
uv run pre-commit install
```

### 4. Run Tests

```bash
uv run pytest
```

## 🛠️ Development

### Adding Dependencies

```bash
uv add requests              # Add runtime dependency
uv add pytest --dev         # Add development dependency
```

### Code Quality

```bash
uv run ruff check           # Lint code
uv run ruff format          # Format code
uv run mypy src/            # Type check
uv run pytest              # Run tests
```

### Pre-commit Hooks

The project uses pre-commit hooks to ensure code quality:

- Trailing whitespace removal
- YAML/TOML/JSON validation
- Ruff linting and formatting
- MyPy type checking
- Bandit security checks

## 👥 Contributing

- 🍴 Fork the repository
- 🌿 Create your feature branch (git checkout -b feature/amazing-feature)
- 💾 Commit your changes (git commit -m 'Add some amazing feature')
- 🚢 Push to the branch (git push origin feature/amazing-feature)
- 🔍 Open a Pull Request

## ⚠️ Trusted publishing failure

That's good news!

You are not able to publish to PyPI unless you have registered your project
on PyPI. You get the following message:

```bash
Trusted publishing exchange failure:

Token request failed: the server refused the request for
the following reasons:

invalid-publisher: valid token, but no corresponding
publisher (All lookup strategies exhausted)
This generally indicates a trusted publisher
configuration error, but could
also indicate an internal error on GitHub or PyPI's part.

The claims rendered below are for debugging purposes only.
You should not
use them to configure a trusted publisher unless they
already match your expectations.
```

Please register your repository. The 'release.yml' flow is
publishing from the 'release' environment. Once you have
registered your new repo it should all work.