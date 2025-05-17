# PyInstaller for PyGame Distribution

PyInstaller is an excellent choice for packaging your PyGame project into a standalone executable. Here's a detailed overview:

## How PyInstaller Works

PyInstaller analyzes your Python application to find all dependencies (including PyGame) and bundles them together with a Python interpreter into a single package. When users run the executable, it extracts these files to a temporary directory and runs your application without requiring Python installation.

## Key Features

- **One-file or one-directory mode**: Create either a single executable or a directory with all dependencies
- **Cross-platform**: Generate executables for Windows (.exe), macOS (.app), or Linux
- **Hooks system**: PyInstaller has specific hooks for PyGame to ensure all resources are properly included
- **Automatic dependency resolution**: Identifies and includes required libraries without manual configuration
- **Resource inclusion**: Can bundle images, sounds, and other assets your game needs

## Installation and Basic Usage

```python
# Install PyInstaller
pip install pyinstaller

# Basic usage to create a one-file executable
pyinstaller --onefile your_game_main.py

# For PyGame projects, often better to use:
pyinstaller --windowed --onefile your_game_main.py
```

The `--windowed` flag prevents a console window from appearing when your game runs.

## Including Game Resources

For PyGame projects, you'll likely have image and sound files that need to be included. There are two approaches:

1. **Using a spec file**:
```python
# Create a spec file first
pyi-makespec --onefile --windowed your_game_main.py

# Then edit the .spec file to add data files and run:
pyinstaller your_game_main.spec
```

2. **Direct command with data options**:
```python
pyinstaller --onefile --windowed --add-data "assets/*:assets/" your_game_main.py
```

## Advanced Configuration via .spec File

For more control, you can create and modify a .spec file:

```python
# Create a spec file
pyi-makespec --onefile --windowed your_game_main.py
```

Then edit the .spec file to include your game assets:

```python
# Example .spec file modification for game resources
a = Analysis(
    ['your_game_main.py'],
    pathex=[],
    binaries=[],
    datas=[('assets/images/*', 'assets/images'), 
           ('assets/sounds/*', 'assets/sounds'),
           ('assets/music/*', 'assets/music')],
    # ...rest of the spec file
)
```

## Code Considerations for PyInstaller Compatibility

When developing your PyGame project with PyInstaller distribution in mind:

```python
import os
import sys
from typing import str

# Helper function to get the correct path for bundled resources
def resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Use this function when loading assets
image = pygame.image.load(resource_path("assets/images/player.png"))
```

## Common Issues and Solutions

1. **Missing assets**: Use the `resource_path` function shown above
2. **Hidden imports**: Some libraries need explicit declaration:
```
pyinstaller --hidden-import pygame.mixer --onefile your_game_main.py
```
3. **Large file size**: Use UPX compression:
```
pyinstaller --onefile --windowed --upx-dir=/path/to/upx your_game_main.py
```

## Platform-Specific Considerations

### Windows
- Creates .exe files
- Add icon: `pyinstaller --icon=your_icon.ico --onefile your_game_main.py`
- Consider using NSIS for creating installers from PyInstaller output

### macOS
- Creates .app bundles
- Add icon: `pyinstaller --icon=your_icon.icns --onefile your_game_main.py`
- Use `--target-architecture` for universal binaries (Intel/Apple Silicon)

### Linux
- Creates executable binaries
- Consider AppImage format for better distribution

## Testing Your Distribution

Always test your PyInstaller package on a clean system without Python installed to ensure all dependencies are correctly bundled.

# Building XBoing Executable with PyInstaller

## Prerequisites
- Python 3.7+
- PyInstaller (`pip install pyinstaller`)

## Build Steps

1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   pip install pyinstaller
   ```

2. Build the executable:
   ```sh
   python scripts/build_executable.py
   # or directly:
   pyinstaller --onefile --name xboing src/xboing.py
   ```

3. The executable will be in the `dist/` directory.

## Platform Notes
- **macOS:** You may need to allow the app in Security & Privacy settings.
- **Windows:** The `.exe` will be in `dist\xboing.exe`.
- **Linux:** The binary will be in `dist/xboing`.

## Including Assets
- Edit `xboing.spec` to include assets (images, sounds, etc.) in the build.
- Example:
  ```python
  datas=[('assets/images', 'assets/images'), ('assets/sounds', 'assets/sounds')]
  ```

## Troubleshooting
- If you see missing module errors, add them to `hiddenimports` in `xboing.spec`.
- For more advanced options, see the [PyInstaller documentation](https://pyinstaller.org/).
