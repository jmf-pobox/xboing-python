# XBoing Python Port Development Guidelines

This document provides essential information for developers working on the XBoing Python port project.

## Build/Configuration Instructions

### Environment Setup

The project uses [Hatch](https://hatch.pypa.io/) for environment and dependency management:

1. **Install Hatch globally** (recommended):
   ```bash
   pip install --user hatch
   # or
   pipx install hatch
   # or
   brew install hatch
   ```

2. **Create or recreate the development environment**:
   ```bash
   hatch env remove      # (optional, to start fresh)
   hatch env create      # Creates new env based on pyproject.toml
   hatch shell           # Activates the environment
   ```

3. **VS Code Integration**:
   - Point VS Code's Python interpreter to the environment's `bin/python` (e.g., `.venv/bin/python` or the path shown by `hatch env find`)
   - This ensures both CLI and VS Code use the same dependencies

### Running the Game

```bash
# Run the game
hatch run game

# Run with coverage tracking
hatch run cov-game
```

### Building the Package

```bash
# Build the package (creates dist/ directory with wheel and sdist)
hatch build

# Check the built package for PyPI compatibility
hatch run publish:check

# Build and upload to PyPI (requires PyPI credentials)
hatch run publish:build
hatch run publish:upload
```

## Testing Information

### Running Tests

```bash
# Run all unit tests
hatch run test

# Run tests with coverage
hatch run cov

# Run a specific test file
hatch run pytest tests/unit/test_file.py

# Run tests with verbose output
hatch run pytest tests/unit/test_file.py -v
```

### Adding New Tests

1. **Test File Structure**:
   - Create test files in the `tests/unit/` directory
   - Name test files with the prefix `test_` (e.g., `test_feature.py`)
   - Name test functions with the prefix `test_` (e.g., `test_function_behavior()`)
   - Include docstrings for all test functions explaining what they test

2. **Test Example**:
   ```python
   #!/usr/bin/env python3
   """Test module description."""
   
   from xboing.module import function_to_test
   
   def test_function_behavior():
       """Test that function_to_test behaves as expected."""
       # Arrange
       input_value = "test"
       
       # Act
       result = function_to_test(input_value)
       
       # Assert
       assert result == "expected output"
   ```

3. **Best Practices**:
   - Use descriptive test names that explain what is being tested
   - Follow the Arrange-Act-Assert pattern
   - Test edge cases and error conditions
   - Keep tests independent of each other
   - Use pytest fixtures for common setup/teardown

## Code Quality Tools

The project uses several tools to maintain code quality:

```bash
# Format code with Black
hatch run format

# Check formatting without changing files
hatch run format-check

# Run linting with Ruff
hatch run lint

# Fix linting issues automatically
hatch run lint-fix

# Run type checking with MyPy
hatch run typecheck

# Run all quality checks at once
hatch run check

# Fix all formatting and linting issues
hatch run fix
```

## Development Guidelines

### Code Style

- Follow [PEP 8](https://peps.python.org/pep-0008/) style guidelines
- Use [PEP 484](https://peps.python.org/pep-0484/) type hints for all functions, methods, and class attributes
- Write docstrings for all public classes, methods, and functions following PEP 257 conventions
- Format code with Black before committing

### Commit Message Standard

The project uses the [Conventional Commits](https://www.conventionalcommits.org/) standard:

```
<type>(<scope>): <short summary>
```
- **type**: feat, fix, chore, refactor, test, docs, etc.
- **scope**: the area of the codebase affected (e.g., gun, ammo, ui)
- **summary**: a brief description of the change

Example:
```
feat(gun): implement ammo collection event, state, and UI update
```

### Debugging

- Use the logging system instead of print statements
- Check the `game_debug.log` file for error messages and debugging information
- When addressing bugs:
  1. Run tests first
  2. Read game_debug.log
  3. If the bug is not evidenced in the log, add more logging
  4. Run the app or request the user to run the app and trigger the bug
  5. Read game_debug.log again to pinpoint the issue

### Asset Management

- All assets are stored in `src/xboing/assets/` and its subdirectories
- Use the asset path helpers in `xboing.utils.asset_paths` to locate assets
- Asset conversion scripts are available in `src/xboing/scripts/`

### Project Structure

```
xboing-python/
├── src/
│   └── xboing/
│       ├── assets/           # Game assets (images, sounds, levels, config)
│       ├── controllers/      # Controllers for game, window, UI, etc.
│       ├── engine/           # Game engine (graphics, audio, input, window)
│       ├── game/             # Game logic (ball, blocks, paddle, collision, state)
│       ├── layout/           # Layout helpers and game layout logic
│       ├── renderers/        # Rendering helpers (digits, lives, etc.)
│       ├── scripts/          # Utility scripts for asset conversion, etc.
│       ├── ui/               # User interface components (views, displays)
│       └── utils/            # Utility functions and helpers
├── docs/                     # Documentation and design docs
└── tests/                    # Test scripts
    ├── integration/          # Integration tests
    └── unit/                 # Unit tests
```

For more detailed information, refer to the documentation in the `docs/` directory.