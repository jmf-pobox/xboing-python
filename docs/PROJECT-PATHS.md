# XBoing Python Project Structure & Paths

This document describes the organization of the XBoing Python project, including the layout of source code, assets, documentation, tests, and legacy materials. The structure is designed to support incremental development, maintainability, and a clean separation between the modern Python implementation and the original C codebase.

---

## Project Directory Overview

```
xboing-python/
├── src/
│   └── xboing/
│       ├── assets/           # Game assets (images, sounds, levels, config)
│       │   ├── images/
│       │   ├── levels/
│       │   ├── sounds/
│       │   └── config/
│       ├── controllers/       # Controller logic for input and view transitions
│       ├── engine/            # Core engine: graphics, audio, input, window, events, event_bus
│       ├── game/              # Game logic: ball, paddle, blocks, collision, state
│       ├── layout/            # Layout management: GameLayout, GameWindow, Rect
│       ├── renderers/         # Stateless renderer utilities (LivesRenderer, DigitRenderer, etc.)
│       ├── ui/                # UI components: score, lives, timer, overlays, views
│       ├── utils/             # Utility functions and helpers (asset_loader, asset_paths, etc.)
│       ├── di_module.py
│       ├── app_coordinator.py
│       └── main.py
├── docs/                  # Project documentation and design docs
├── dist/                  # Build/distribution artifacts (if any)
├── scripts/               # Utility scripts for asset conversion, etc.
├── tests/                 # Test suite
│   ├── unit/              # Unit tests
│   └── integration/       # Integration tests
├── xboing2.4-clang/       # Original XBoing C codebase and assets (read-only)
├── .venv/                 # Python virtual environment (local, not versioned)
├── .vscode/               # VS Code settings (optional)
├── pyproject.toml         # Python project configuration and dependencies
├── README.md              # Project overview and instructions
├── TODO.md                # Developer action items
└── ...                    # Other standard files (.gitignore, LICENSE, etc.)
```

---

## Directory & File Descriptions

- **src/xboing/assets/**: Contains all game assets for the Python version, including images (PNG), sounds (WAV), level data, and config. This directory is the single source of truth for all asset files. All asset path helpers in the codebase resolve to this directory.

- **docs/**: Holds all design and technical documentation, including GUI, audio, level, and block design documents, as well as project path explanations and environment usage guides.

- **dist/**: Used for build or distribution artifacts. Typically empty unless building a distributable package.

- **scripts/**: Contains utility scripts for asset conversion (e.g., XPM to PNG, AU to WAV), asset synchronization, and other development tools. These scripts help bridge the gap between the legacy and modern codebases.

- **src/**: The main source code for the Python implementation.  N.B. 'src' is already in the PYTHONPATH and should not appear in imports.
  - **src/controllers/**: Controller logic for input handling and view transitions.
  - **src/engine/**: Handles graphics, audio, input, window management, and event systems (including event_bus and events).
  - **src/game/**: Contains core game logic, including ball and paddle mechanics, block behaviors, level management, and game state.
  - **src/layout/**: Layout management, including GameLayout, GameWindow, and Rect classes for window/region hierarchy.
  - **src/renderers/**: Stateless renderer utilities (e.g., LivesRenderer, DigitRenderer) used by UI components for drawing visual elements.
  - **src/ui/**: Houses all user interface components, including event-driven displays for score, lives, level, timer, messages, and content views.
  - **src/utils/**: Utility modules for asset loading, asset path resolution, and other generic helpers. No longer contains event_bus or layout logic.

- **tests/**: Contains all automated tests.
  - **tests/unit/**: Unit tests for individual modules and components.
  - **tests/integration/**: Integration tests for system-level and event-driven behaviors.

- **xboing2.4-clang/**: The original XBoing C codebase, including legacy assets and documentation. This directory is read-only and serves as a reference for the porting process.

- **.venv/**: Local Python virtual environment for dependency management (not tracked in version control).

- **pyproject.toml**: The central configuration file for Python packaging, dependencies, and development tools.

- **README.md**: Project overview, installation instructions, and developer notes.

- **TODO.md**: Ongoing developer action items and migration steps.

---

## Notes on Structure & Migration

- The project maintains a clear separation between the modern Python implementation (`src/`, `assets/`, `docs/`) and the original C codebase (`xboing2.4-clang/`).
- Asset conversion and synchronization are handled via scripts in the `scripts/` directory.
- The test suite is organized into `unit/` and `integration/` subdirectories for clarity and maintainability.
- Some directories (e.g., `.venv/`, `.vscode/`, `.mypy_cache/`, `.ruff_cache/`) are standard for Python development but are not part of the core project logic.
- The structure supports incremental development: new features and refactors can be implemented and tested in isolation, while legacy code remains available for reference.

---

This structure is designed to facilitate a clean, maintainable, and testable codebase, supporting both ongoing development and future extensions of XBoing Python.