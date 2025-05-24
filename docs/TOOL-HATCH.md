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

# Understanding Python and Hatch Environments in This Project

## What is a Hatch Environment?
- A **Hatch environment** is a Python environment managed by the Hatch tool, as defined in `pyproject.toml`.
- Under the hood, a Hatch environment is a standard Python virtual environment (venv).
- Hatch can manage multiple environments (e.g., for different Python versions or purposes), each with its own dependencies.

## Where Are Hatch Environments Stored?
- By default, Hatch creates environments in a centralized user directory (e.g., `~/Library/Application Support/hatch/env/virtual/...` on macOS).
- You can configure Hatch to use a local `.venv` in your project root by adding this to `pyproject.toml`:
  ```toml
  [tool.hatch.envs.default]
  path = ".venv"
  ```
- Each environment is a standard Python venv directory, containing `bin/`, `lib/`, `pyvenv.cfg`, etc.

## Relationship to `.venv`
- If you set `path = ".venv"`, Hatch will create the environment in your project root as `.venv/`.
- This `.venv` is a standard Python virtual environment and can be used by VS Code or any other tool that supports venvs.
- If not set, Hatch uses its global environment store.

## Managing Dependencies
- `[project.dependencies]` in `pyproject.toml` lists main/runtime dependencies (e.g., `pygame`).
- `[tool.hatch.envs.default.dependencies]` lists dev-only dependencies (e.g., `pytest`, `black`, `pillow` for scripts).
- **Hatch always installs both** sets of dependencies when creating an environment.
- You do not need to duplicate runtime dependencies in the dev dependencies section.

## Creating and Updating Environments
- **Install Hatch globally** (recommended):
  ```sh
  pip install --user hatch
  # or
  pipx install hatch
  # or
  brew install hatch
  ```
- **Create or recreate an environment:**
  ```sh
  hatch env remove      # (optional, to start fresh)
  hatch env create      # Creates new env based on pyproject.toml
  hatch shell           # Activates the environment
  ```
- When you run `hatch shell` or any `hatch run ...` command, Hatch will auto-sync dependencies with `pyproject.toml`.

## VS Code Integration
- To use the same environment in VS Code, point VS Code's Python interpreter to the environment's `bin/python` (e.g., `.venv/bin/python` or the path shown by `hatch env find`).
- This ensures both CLI and VS Code use the same dependencies.

## Local vs. Global Environments
| Environment Location | Who Manages It | How to Use with VS Code         |
|----------------------|---------------|---------------------------------|
| Centralized (default)| Hatch         | Point VS Code to the path shown |
| Local `.venv`        | Hatch         | Point VS Code to `.venv/bin/python` |

## Best Practices
- Use Hatch as your environment and dependency manager.
- Install Hatch globally for consistent access to the `hatch` command.
- Use `pyproject.toml` as the single source of truth for dependencies.
- For a clean environment, use `hatch env remove` and `hatch env create`.
- For most updates, just run `hatch shell` or `hatch run ...` and Hatch will sync dependencies.

## Troubleshooting
- If you remove the environment, you need Hatch installed globally to recreate it.
- If you want a local `.venv`, set the `path` in `pyproject.toml` as shown above.
- To see all environments and their locations, run:
  ```sh
  hatch env find
  ```

---

*This document summarizes the key points about Hatch and Python environments, their relationship, and best practices for development and editor integration in this project.* 