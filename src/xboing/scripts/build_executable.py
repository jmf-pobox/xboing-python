#!/usr/bin/env python3
"""
Build script for creating standalone executables using PyInstaller.

This script automates the process of building a standalone executable
for the XBoing game using PyInstaller. It handles:
1. Installing PyInstaller if not already installed
2. Creating a spec file with the correct configuration
3. Building the executable

Note: PyInstaller builds executables for the platform it's running on.
You must run this script on Windows to build a Windows .exe,
on macOS to build a macOS app, and on Linux to build a Linux executable.
"""

from pathlib import Path
import platform
import subprocess
import sys


def get_project_root():
    """Get the project root directory."""
    # Start from the current file and go up until we find pyproject.toml
    current_dir = Path(__file__).resolve().parent
    while current_dir != current_dir.parent:
        if (current_dir / "pyproject.toml").exists():
            return current_dir
        current_dir = current_dir.parent

    # If we couldn't find it, use the src directory's parent
    return Path(__file__).resolve().parent.parent.parent.parent


def create_spec_file(project_root):
    """Create a PyInstaller spec file for the project."""
    src_dir = project_root / "src"
    main_script = src_dir / "xboing" / "main.py"

    # Get all asset directories
    assets_dir = src_dir / "xboing" / "assets"

    # Create the spec file content
    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-
import os
import glob

block_cipher = None

# Collect all asset files
assets = []
assets_root = {repr(str(assets_dir))}

# Images - first add files directly in the images directory
for img_file in glob.glob(f"{{assets_root}}/images/*.png"):
    assets.append((img_file, "assets/images"))

# Then add files from subdirectories
for img_dir in glob.glob(f"{{assets_root}}/images/*"):
    if os.path.isdir(img_dir):
        img_dir_name = os.path.basename(img_dir)
        for img_file in glob.glob(f"{{img_dir}}/*"):
            assets.append((img_file, f"assets/images/{{img_dir_name}}"))

# Sounds
for sound_file in glob.glob(f"{{assets_root}}/sounds/*"):
    assets.append((sound_file, "assets/sounds"))

# Levels
for level_file in glob.glob(f"{{assets_root}}/levels/*"):
    assets.append((level_file, "assets/levels"))

# Config
for config_file in glob.glob(f"{{assets_root}}/config/*"):
    assets.append((config_file, "assets/config"))

a = Analysis(
    ['{main_script}'],
    pathex=[],
    binaries=[],
    datas=assets,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='xboing',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='{assets_dir}/images/icon.png' if os.path.exists('{assets_dir}/images/icon.png') else None,
)
"""

    # Write the spec file
    spec_file_path = project_root / "xboing.spec"
    with open(spec_file_path, "w", encoding="utf-8") as f:
        f.write(spec_content)

    print(f"Created spec file at {spec_file_path}")
    return spec_file_path


def build_executable(spec_file):
    """Build the executable using PyInstaller."""
    print("Building executable...")
    subprocess.check_call([sys.executable, "-m", "PyInstaller", str(spec_file)])
    print("Executable built successfully!")


def get_platform_info():
    """Get information about the current platform."""
    system = platform.system()
    if system == "Windows":
        return {
            "name": "Windows",
            "executable": "xboing.exe",
            "path": "dist\\xboing.exe",
            "notes": "The Windows executable (.exe) can be distributed to Windows users.",
        }
    if system == "Darwin":  # macOS
        return {
            "name": "macOS",
            "executable": "xboing",
            "path": "dist/xboing",
            "notes": "The macOS executable may need to be allowed in Security & Privacy settings.",
        }
    if system == "Linux":
        return {
            "name": "Linux",
            "executable": "xboing",
            "path": "dist/xboing",
            "notes": "Consider using AppImage for better Linux distribution.",
        }
    return {
        "name": system,
        "executable": "xboing",
        "path": "dist/xboing",
        "notes": "Unknown platform - executable may have platform-specific requirements.",
    }


def main():
    """Create the executable."""
    platform_info = get_platform_info()

    print(f"Starting XBoing executable build process for {platform_info['name']}...")
    print(f"Note: This will create a {platform_info['name']}-specific executable.")

    # Get project root
    project_root = get_project_root()
    print(f"Project root: {project_root}")

    # Create spec file
    spec_file = create_spec_file(project_root)

    # Build executable
    build_executable(spec_file)

    print("\nBuild completed!")
    print(
        f"The {platform_info['name']} executable can be found at: {platform_info['path']}"
    )
    print(f"Platform note: {platform_info['notes']}")
    print("\nRemember: PyInstaller builds for the current platform only.")
    print("To build for other platforms, run this script on those platforms.")


if __name__ == "__main__":
    main()
