# XBoing II (Python port)

[![PyPI version](https://img.shields.io/pypi/v/xboing.svg)](https://pypi.org/project/xboing/)
[![Pylint](https://github.com/jmf-pobox/xboing-python/actions/workflows/pylint.yml/badge.svg)](https://github.com/jmf-pobox/xboing-python/actions/workflows/pylint.yml)
[![Tests](https://github.com/jmf-pobox/xboing-python/actions/workflows/tests.yml/badge.svg)](https://github.com/jmf-pobox/xboing-python/actions/workflows/tests.yml)
[![Build](https://github.com/jmf-pobox/xboing-python/actions/workflows/build.yml/badge.svg)](https://github.com/jmf-pobox/xboing-python/actions/workflows/build.yml)

> **Now available on PyPI!**  
> Install with `pip install xboing` and run with `python -m xboing`.

## 🚀 Quick Start

```bash
pip install xboing
python -m xboing
```

## 🎮 For Players

### What is XBoing?

XBoing is a blockout type game where you have a paddle which you control to bounce a ball around the game zone destroying blocks with a proton ball. Each block carries a different point value. The more blocks you destroy, the better your score. The person with the highest score wins.

The arena is filled with blocks and other objects. You have a paddle that can move from left to right at the bottom of the arena. You control the paddle so that the proton ball bounces around blowing up blocks and that it does not go past the paddle and out the bottom, much like a pinball game.

XBoing has many features for a simple blockout type of game. Some of them are listed below :

- Over 20 different block types
- 80 pre-designed levels
- Sound support for many systems
- Very colourful - arcade like
- Keyboard and mouse control
- In game instructions
- (originally) Australian Made :-)

To be added:

- Builtin WYSIWYG level editor
- Simple installation
- Detailed manual page

Originally developed for X11 in C, XBoing was designed for speed and fun, with a focus on colorful visuals and responsive controls. This Python port faithfully recreates the original experience while adding modern compatibility.

### Installation & Playing

#### 1. Install from PyPI (Recommended)
```bash
pip install xboing
python -m xboing
```

#### 2. (Optional) Development Install from Source
If you want the latest development version or to contribute:

```bash
git clone https://github.com/jmf-pobox/xboing-python.git
cd xboing-python
pip install -e .
python -m xboing
```
Or use Hatch for advanced development workflows (see below).

### Game Controls

- **J-K-L Keys**: Move paddle left, fire/launch, move paddle right
- **Mouse**: Move left, click to fire/launch, move right
- **Control-Q**: Quit game

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

### Project Status

This Python port is under active development and is already playable. Current features include:
- ✅ Full conversion of all original XBoing assets (graphics, sounds, levels)
- ✅ Level loading system that reads and displays original level files
- ✅ Block implementation with correct behaviors and effects
- ✅ Ball physics and collision detection
- ✅ Paddle movement and control (keyboard and mouse)
- ✅ Audio system for event-driven sound effects
- ✅ Event-driven, component-based UI (score, lives, ammo, level, timer, messages)
- ✅ Paddle gun/ammo feature: ammo state, UI, collection, and sound (Phase 1 complete)
- 🚧 Special power-ups and effects (in progress)
- 🚧 Game state management and transitions (polished, but ongoing)
- 🚧 Score tracking and high scores (basic, more to come)
- 🚧 Machine gun mode and bullet logic (planned)

The game is fully playable, with most core features implemented and tested. Remaining work focuses on advanced power-ups, polish, and additional features to match and extend the original XBoing experience.

## 💻 For Developers

### Project Structure

```
xboing-python/
├── src/
│   └── xboing/
│       ├── assets/           # Game assets (images, sounds, levels, config)
│       │   ├── images/       # All game images (balls, blocks, backgrounds, etc.)
│       │   ├── sounds/       # Sound effects (WAV)
│       │   ├── levels/       # Level data files
│       │   └── config/       # Block types and other config
│       ├── controllers/      # Controllers for game, window, UI, etc.
│       ├── engine/           # Game engine (graphics, audio, input, window)
│       ├── game/             # Game logic (ball, blocks, paddle, collision, state)
│       ├── layout/           # Layout helpers and game layout logic
│       ├── renderers/        # Rendering helpers (digits, lives, etc.)
│       ├── ui/               # User interface components (views, displays)
│       ├── utils/            # Utility functions and helpers
│       ├── di_module.py      # Dependency injection setup
│       ├── app_coordinator.py# App entry coordination
│       └── main.py           # Main entry point
├── docs/                     # Documentation and design docs
├── src/
│   └── xboing/
│       └── scripts/         # Utility scripts for asset conversion, etc. (run as modules)
├── tests/                    # Test scripts
│   ├── integration/          # Integration tests
│   └── unit/                 # Unit tests
└── xboing2.4-clang/          # Original XBoing C source/assets (reference)
```

### Asset Management

All asset path helpers resolve to `src/xboing/assets/` and its subfolders. All images, sounds, and levels are loaded from this canonical directory inside the package. Asset conversion scripts in `scripts/` should use this path for input/output.

- Original XPM graphics → PNG format (in `src/xboing/assets/images/`)
- Original AU sound files → WAV format (in `src/xboing/assets/sounds/`)

Use the provided conversion scripts in `scripts/` to update or add assets as needed.

### Asset Migration Tools

```bash
# Run tests
hatch run test

# Convert XPM to PNG (for new assets)
python -m xboing.scripts.convert_xpm_to_png --input path/to/image.xpm --output output.png

# Convert AU to WAV (for new sounds)
python -m xboing.scripts.convert_au_to_wav --input path/to/sound.au --output output.wav

# Normalize all audio files in the assets directory
python -m xboing.scripts.normalize_audio

# Fix background images (formatting, transparency, etc.)
python -m xboing.scripts.fix_background

# Fix ball lost sound or related assets
python -m xboing.scripts.fix_balllost

# Search dependencies in the codebase
python -m xboing.scripts.dep_grep <search_term>
```

### Design Documentation

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

The original source code is available at: https://www.techrescue.org/xboing/xboing2.4.tar.gz

## Commit Message Standard

This project uses the [Conventional Commits](https://www.conventionalcommits.org/) standard for all commit messages. This helps automate changelogs, semantic versioning, and improves code review clarity.

**Format:**
```
<type>(<scope>): <short summary>
```
- **type**: feat, fix, chore, refactor, test, docs, etc.
- **scope**: the area of the codebase affected (e.g., gun, ammo, ui)
- **summary**: a brief description of the change

**Example:**
```
feat(gun): implement ammo collection event, state, and UI update
```

See the [Conventional Commits documentation](https://www.conventionalcommits.org/) for more details.

