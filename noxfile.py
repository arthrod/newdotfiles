"""Nox configuration for testing and linting."""

import nox


@nox.session(python=["3.13"])
def tests(session):
    """Run the test suite with pytest and coverage."""
    session.install("uv")
    session.run("uv", "sync", "--group", "test")
    session.run("uv", "run", "pytest", "--cov=src", "--cov-report=xml", "--cov-report=term")


@nox.session
def lint(session):
    """Run linting with ruff."""
    session.install("uv")
    session.run("uv", "sync", "--group", "lint")
    session.run("uv", "run", "ruff", "check")
    session.run("uv", "run", "ruff", "format", "--check")


@nox.session
def mypy(session):
    """Run type checking with mypy."""
    session.install("uv")
    session.run("uv", "sync", "--group", "lint")
    session.run("uv", "run", "mypy", "src/")


@nox.session
def security(session):
    """Run security checks with bandit."""
    session.install("uv")
    session.run("uv", "sync", "--group", "test")
    session.run("uv", "run", "bandit", "-r", "src/", "-c", "pyproject.toml")


@nox.session
def format(session):
    """Auto-format code with ruff."""
    session.install("uv")
    session.run("uv", "sync", "--group", "lint")
    session.run("uv", "run", "ruff", "check", "--fix")
    session.run("uv", "run", "ruff", "format")


@nox.session
def docs(session):
    """Build documentation (placeholder for future use)."""
    session.install("uv")
    session.run("uv", "sync", "--group", "dev")
    session.log("Documentation building would go here")