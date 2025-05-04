#!/bin/bash

# Script to reorganize the XBoing Python project structure

set -e  # Exit on error

echo "Reorganizing XBoing Python project..."

# Create needed directories
mkdir -p docs tests scripts

# Move documentation files to docs/
echo "Moving documentation files..."
mv BLOCK_IMPLEMENTATION.md docs/
mv LEVELS.md docs/
mv UPDATE.md docs/
mv README.md docs/README.md.tmp  # Move temporarily, we'll create a new one

# Move test files to tests/
echo "Moving test files..."
mv test_*.py tests/
# Make sure test files still work after moving
sed -i 's|sys.path.append(os.path.dirname(os.path.abspath(__file__)))|sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))|g' tests/*.py

# Move tool scripts to scripts/
echo "Moving utility scripts to scripts/"
mv tools/* scripts/
rmdir tools
mv sync_assets.py scripts/

# Set up a standard Python project structure
echo "Creating a new README.md..."
cat > README.md << 'EOF'
# XBoing Python Port

A Python reimplementation of the classic XBoing game originally written for X11 in C.

## Overview

XBoing is a breakout-style game with colorful blocks, power-ups, and challenging levels.
This project is a faithful recreation of the original game using Python and pygame.

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/xboing-py.git
cd xboing-py

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Run the game
python -m src.main
```

## Documentation

See the docs/ directory for detailed information:
- [Block Implementation](docs/BLOCK_IMPLEMENTATION.md)
- [Levels System](docs/LEVELS.md)
- [Python Migration Notes](docs/PYTHON_MIGRATION.md)
- [X11 Update Notes](docs/X11_UPDATE.md)

## Development

The project uses a standard Python package structure:
- `src/`: Main source code
- `assets/`: Game assets (images, sounds, etc.)
- `tests/`: Test scripts
- `scripts/`: Utility scripts
- `docs/`: Documentation

## License

This project is licensed under the same terms as the original XBoing - see the LICENSE file for details.
EOF

# Move any custom README content to docs/ORIGINAL_README.md
mv docs/README.md.tmp docs/ORIGINAL_README.md

# Create a dedicated assets directory structure
echo "Organizing assets..."
mkdir -p assets/images/{blocks,backgrounds,balls} assets/sounds assets/levels

# We'll leave src/assets for now and let the sync_assets.py script handle
# moving everything to the proper locations

echo "Project reorganization complete!"
echo "Next steps:"
echo "1. Update imports in Python files if needed"
echo "2. Run scripts/sync_assets.py to organize game assets"
echo "3. Test the application to ensure everything works correctly"