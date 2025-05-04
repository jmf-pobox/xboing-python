# Hatch Usage Guide for XBoing Python Port

This document explains how to use [Hatch](https://hatch.pypa.io/) for development and packaging of the XBoing Python port.

## What is Hatch?

Hatch is a modern, extensible Python project manager that handles everything from dependency management to building and publishing packages. It's designed to simplify development workflows and provides a unified interface for common Python project tasks.

## Installation

Hatch is already installed in the project's virtual environment. To use it:

```bash
# Activate the virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Verify Hatch is installed
hatch --version
```

If you need to install Hatch in a new environment:

```bash
pip install hatch
```

## Common Commands

### Development Environment

Run the game:
```bash
hatch run game
```

Run tests:
```bash
hatch run test
```

Run tests with coverage:
```bash
hatch run cov
```

### Code Quality

Format code with Black:
```bash
hatch run format
```

Check formatting without changing files:
```bash
hatch run format-check
```

Run linting with Ruff:
```bash
hatch run lint
```

Fix linting issues automatically:
```bash
hatch run lint-fix
```

Run type checking with MyPy:
```bash
hatch run typecheck
```

Run all quality checks at once:
```bash
hatch run check
```

Fix all formatting and linting issues:
```bash
hatch run fix
```

### Building and Publishing

Build the package (creates dist/ directory with wheel and sdist):
```bash
hatch build
```

Check the built package for PyPI compatibility:
```bash
hatch run publish:check
```

Build and upload to PyPI (requires PyPI credentials):
```bash
hatch run publish:build
hatch run publish:upload
```

## Project Structure

The project uses Hatch for package management with the following key features:

1. **Entry Point**: The main executable is accessed via `xboing` command after installation
2. **Versioning**: Version is managed in `src/__version__.py`
3. **Asset Handling**: Game assets are automatically included in the package
4. **Test Configuration**: Tests are configured to run with pytest

## Environment Configuration

Hatch provides isolated environments for different tasks:

- **default**: For general development, testing, and code quality
- **publish**: For building and publishing the package

## Customizing Hatch Configuration

All Hatch configuration is in `pyproject.toml`. The main sections are:

- `[build-system]`: Specifies Hatch as the build system
- `[project]`: Core project metadata
- `[tool.hatch.build]`: Build configuration
- `[tool.hatch.envs]`: Environment configurations
- `[tool.hatch.version]`: Version management