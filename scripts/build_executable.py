#!/usr/bin/env python3
"""
Build XBoing executable using PyInstaller.

Usage:
    python scripts/build_executable.py

This script runs PyInstaller to build a standalone executable for the game.
Requires PyInstaller to be installed in your environment.
"""
import subprocess
import sys

ENTRY_POINT = "src/xboing.py"

cmd = [
    sys.executable,
    "-m",
    "PyInstaller",
    "--onefile",
    "--name",
    "xboing",
    ENTRY_POINT,
]

print(f"Running: {' '.join(cmd)}")
subprocess.run(cmd, check=True) 