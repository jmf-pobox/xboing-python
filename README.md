# XBoing Python Port

[![GitHub release](https://img.shields.io/github/v/release/jmf-pobox/xboing-python?include_prereleases)](https://github.com/jmf-pobox/xboing-python/releases)
[![Pylint](https://github.com/jmf-pobox/xboing-python/actions/workflows/pylint.yml/badge.svg)](https://github.com/jmf-pobox/xboing-python/actions/workflows/pylint.yml)
[![Tests](https://github.com/jmf-pobox/xboing-python/actions/workflows/tests.yml/badge.svg)](https://github.com/jmf-pobox/xboing-python/actions/workflows/tests.yml)
[![Build](https://github.com/jmf-pobox/xboing-python/actions/workflows/build.yml/badge.svg)](https://github.com/jmf-pobox/xboing-python/actions/workflows/build.yml)

A Python reimplementation of the classic XBoing game originally written for X11 in C. This modernized port maintains the gameplay and charm of the original while offering improved compatibility with modern systems.

## 🎮 For Players

### What is XBoing?

XBoing is an addictive breakout-style arcade game featuring:
- 80 challenging levels with unique layouts
- Colorful block types with different behaviors
- Special power-ups and power-downs (paddle expanders, multiball, etc.)
- Lively sound effects and colorful graphics
- Classic arcade-style gameplay with modern conveniences

### Installation & Playing

```bash
# Clone the repository
git clone https://github.com/yourusername/xboing-py.git
cd xboing-py

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the game
python src/main.py
```

### Game Controls

- **Left/Right Arrow Keys**: Move paddle
- **Space**: Launch ball / Pause game
- **Esc**: Quit game
- **F**: Toggle fullscreen

### Special Blocks & Power-ups

- **Multiball**: Splits your ball into multiple balls
- **Extra Ball**: Gives you an additional ball
- **Paddle Expander**: Makes your paddle larger
- **Paddle Shrinker**: Makes your paddle smaller
- **Counter Blocks**: Require multiple hits to destroy
- **Death Blocks**: End your current life when hit
- **Black Blocks**: Indestructible, bounce balls away
- **Bomb Blocks**: Explode and destroy neighboring blocks
- **Sticky Blocks**: Make balls stick to paddle

## 💻 For Developers

### Project Status

This Python port is currently in active development. Current features:
- ✅ Full conversion of all original XBoing assets
- ✅ Level loading system that reads original level files
- ✅ Block implementation with proper behaviors
- ✅ Basic ball physics and collision detection
- ✅ Paddle movement and control
- ✅ Audio system for sound effects
- ✅ Background cycling between levels
- 🚧 Special power-ups and effects (partially implemented)
- 🚧 Game state management and transitions
- 🚧 Score tracking and high scores

### Project Structure

```
xboing-python/
├── assets/               # Game assets (images, sounds, levels)
│   ├── images/           # All game images (balls, blocks, backgrounds, etc.)
│   ├── sounds/           # Sound effects (WAV, AU)
│   └── levels/           # Level data files
├── docs/                 # Documentation and design docs
├── scripts/              # Utility scripts for asset conversion, etc.
├── src/                  # Source code
│   ├── app_coordinator.py# App entry coordination
│   ├── controllers/      # Controllers for game, window, UI, etc.
│   ├── di_module.py      # Dependency injection setup
│   ├── engine/           # Game engine (graphics, audio, input, window)
│   ├── game/             # Game logic (ball, blocks, paddle, collision, state)
│   ├── layout/           # Layout helpers and game layout logic
│   ├── main.py           # Main entry point
│   ├── renderers/        # Rendering helpers (digits, lives, etc.)
│   ├── ui/               # User interface components (views, displays)
│   └── utils/            # Utility functions and helpers
├── tests/                # Test scripts
│   ├── integration/      # Integration tests
│   └── unit/             # Unit tests
└── xboing2.4-clang/      # Original XBoing C source/assets (reference)
```

### Asset Management

The game uses assets from the original XBoing converted to modern formats:
- Original XPM graphics → PNG format
- Original AU sound files → WAV format

Use `scripts/sync_assets.py` to synchronize assets from the original XBoing directory.

### Development Tools

```bash
# Run tests
python -m pytest

# Convert XPM to PNG (for new assets)
python scripts/better_xpm_converter.py path/to/image.xpm output.png

# Convert AU to WAV (for new sounds)
python scripts/convert_audio.py path/to/sound.au output.wav

# Sync all assets from original XBoing
python scripts/sync_assets.py
```

### Documentation

See the `docs/` directory for detailed information:
- [Audio Design](docs/AUDIO-DESIGN.md) – Audio system, event-driven sound playback, and sound asset management
- [Block Design](docs/BLOCKS-DESIGN.md) – How blocks work, their types, and behaviors
- [Dependency Injection Design](docs/DI-DESIGN.md) – Dependency injection and modularity
- [GUI Design](docs/GUI-DESIGN.md) – Window layout, UI regions, and event-driven UI architecture
- [Hatch Usage](docs/HATCH_USAGE.md) – Using Hatch for environment and dependency management
- [Highscore Design](docs/HIGHSCORE-DESIGN.md) – High score system design
- [Levels Design](docs/LEVELS-DESIGN.md) – Level format, loading system, and level structure
- [Logging Design](docs/LOGGING-DESIGN.md) – Logging system and best practices
- [Project Paths](docs/PROJECT-PATHS.md) – Directory structure and asset locations
- [Scripts Design](docs/SCRIPTS-DESIGN.md) – Utility and asset conversion scripts

### Contributing

Contributions are welcome! Areas that need work:
1. Complete implementation of all special block effects
2. High score system
3. Game state management and transitions
4. Enhanced visual effects
5. Additional sound effects
6. Level editor

### Testing & Quality

- All major UI components (score, lives, level, timer, message window) are event-driven, component-based, and have dedicated unit tests.
- The test suite includes both unit and integration tests, covering game logic, event-driven UI updates, and core systems.
- Tests are run before and after each major change to ensure stability and catch regressions early.
- Type hints and docstrings are used throughout for clarity and static analysis.
- Logging is used for warnings and errors (no print statements in production code).
- The codebase is designed for maintainability, extensibility, and testability, following modern Python best practices.

## License

This project is licensed under the same terms as the original XBoing - see the LICENSE file for details.

## Original Source

The original source code is available in the subdirectory: xboing2.4-clang

## Building a Standalone Executable

You can build a standalone executable for XBoing using PyInstaller:

1. Install PyInstaller: `pip install pyinstaller`
2. Run the build script: `python scripts/build_executable.py`
3. The executable will be in the `dist/` directory.

See [docs/PYINSTALLER-GUIDE.md](docs/PYINSTALLER-GUIDE.md) for full details and troubleshooting.

