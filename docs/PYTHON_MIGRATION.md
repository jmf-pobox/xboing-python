# XBoing Migration to Python/SDL2: Directory Structure

## Recommended Directory Structure

```
xboing/
├── docs/                    # Documentation
│   ├── original/           # Original game documentation
│   └── X11_UPDATE.md       # Migration analysis document
├── legacy/                 # Original C codebase (unmodified)
│   ├── audio/
│   ├── bitmaps/
│   ├── include/
│   └── ...
├── src/                    # New Python implementation
│   ├── assets/             # Converted game assets
│   │   ├── images/         # PNG images converted from XPM
│   │   │   ├── balls/      # Ball sprites
│   │   │   ├── blocks/     # Block sprites
│   │   │   ├── backgrounds/
│   │   │   └── ...
│   │   ├── sounds/         # Audio files
│   │   └── levels/         # Level data
│   ├── engine/             # Core engine components
│   │   ├── __init__.py
│   │   ├── graphics.py     # SDL2 rendering abstraction
│   │   ├── input.py        # Input handling
│   │   ├── audio.py        # Audio system
│   │   └── window.py       # Window management
│   ├── game/               # Game logic
│   │   ├── __init__.py
│   │   ├── paddle.py       # Paddle mechanics
│   │   ├── ball.py         # Ball physics
│   │   ├── blocks.py       # Block behaviors
│   │   ├── levels.py       # Level loading/management
│   │   ├── powerups.py     # Powerup system
│   │   ├── score.py        # Scoring system
│   │   └── states.py       # Game state machine
│   ├── ui/                 # User interface
│   │   ├── __init__.py
│   │   ├── menus.py        # Menu screens
│   │   ├── hud.py          # Heads-up display
│   │   └── effects.py      # Visual effects
│   ├── utils/              # Utility functions
│   │   ├── __init__.py
│   │   ├── asset_loader.py # Asset loading utilities
│   │   ├── config.py       # Configuration management
│   │   └── profiler.py     # Performance monitoring
│   ├── main.py             # Application entry point
│   └── config.ini          # Game configuration
├── tests/                  # Test suite
│   ├── test_ball.py
│   ├── test_blocks.py
│   └── ...
├── tools/                  # Development and conversion tools
│   ├── xpm_to_png.py       # Asset conversion utilities
│   ├── level_converter.py  # Level format converter
│   └── ...
├── .gitignore
├── pyproject.toml          # Modern Python packaging
├── requirements.txt        # Dependencies
└── README.md
```

## Rationale

This structure follows modern Python project organization principles while addressing the specific needs of the XBoing migration:

1. **Clear separation from legacy code**: The original C code remains untouched in the `legacy/` directory for reference

2. **Clean module organization**: 
   - `engine/` handles all SDL2 and system-level interactions
   - `game/` contains pure game logic with minimal dependencies
   - `ui/` separates user interface concerns
   - `utils/` houses supporting functionality

3. **Asset management**: The `assets/` directory organizes converted game resources in modern formats with a structure mirroring the original

4. **Development support**: Includes `tools/` for migration utilities and `tests/` for ensuring game logic correctness

5. **Modern Python practices**:
   - Uses packages with `__init__.py` files
   - Employs modern Python packaging with `pyproject.toml`
   - Follows Python naming conventions

This structure facilitates incremental development, allowing individual components to be implemented and tested in isolation while maintaining a clear path for the overall migration.