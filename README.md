# XBoing Python Port

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
xboing-py/
├── assets/               # Game assets (images, sounds, levels)
├── docs/                 # Documentation
├── scripts/              # Utility scripts for asset conversion, etc.
├── src/                  # Source code
│   ├── engine/           # Game engine (graphics, audio, input)
│   ├── game/             # Game logic (ball, blocks, paddle, collision)
│   ├── ui/               # User interface components
│   └── utils/            # Utility functions and helpers
└── tests/                # Test scripts
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

See the docs/ directory for detailed information:
- [Block Implementation](docs/BLOCK_IMPLEMENTATION.md) - How blocks work and their behaviors
- [Levels System](docs/LEVELS.md) - Level format and loading system
- [Python Migration Notes](docs/PYTHON_MIGRATION.md) - Notes on porting from C to Python
- [X11 Update Notes](docs/X11_UPDATE.md) - Notes on transitioning from X11 to pygame

### Contributing

Contributions are welcome! Areas that need work:
1. Complete implementation of all special block effects
2. High score system
3. Game state management and transitions
4. Enhanced visual effects
5. Additional sound effects
6. Level editor

### Testing & Quality

- **Unit tests** are in `tests/unit/` and run by default (see `pyproject.toml` and `pytest.ini`).
- **Integration tests** are in `tests/integration/` and can be run manually with `pytest tests/integration`.
- The audio system is fully unit tested, supports only `.wav` files, and uses a thread-safe, cached audio player.
- The lives display is fixed-width, always shows 3 slots, and invisible balls are on the left (matching the original game). This is also fully unit tested.
- Unused or legacy code (e.g., background pattern generator) has been removed for clarity and maintainability.
- Logging is used throughout for warnings and errors (no print statements in production code).
- Type hints and docstrings are used for clarity and static analysis.
- Caching is used where appropriate for performance (audio, lives display, etc.).

## License

This project is licensed under the same terms as the original XBoing - see the LICENSE file for details.

## Original Source

The original source code is available in the subdirectory: xboing2.4-clang

