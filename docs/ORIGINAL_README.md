# XBoing Python/SDL2 Port

This is a modern port of the classic XBoing game, migrated from X11 to a cross-platform Python/SDL2 implementation that works on both X11 and Wayland display servers.

## About XBoing

XBoing is a breakout-style game originally developed by Justin C. Kibell. This port preserves the gameplay and aesthetics of the original while modernizing the codebase.

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the game
python src/main.py
```

## Development

This project is organized with a clean separation between game logic, rendering, and asset management. Key directories:

- `src/engine/`: SDL2 abstraction layer
- `src/game/`: Game logic and mechanics
- `src/ui/`: User interface
- `src/assets/`: Game assets (images, sounds, levels)

## License

This software is licensed under the X Consortium License, the same as the original XBoing.