#!/usr/bin/env python3
"""
Asset synchronization script for XBoing Python port.

This script:
1. Creates the appropriate asset directory structure
2. Copies all necessary assets from the original XBoing directory
3. Converts XPM files to PNG format for use in the Python port
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

from utils.asset_paths import (
    ASSETS_DIR,
    get_backgrounds_dir,
    get_blocks_dir,
    get_sounds_dir,
)

# Add project root directory to Python path (parent of scripts directory)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Define paths
# Original XBoing directory is one level up from the Python port directory
ORIGINAL_XBOING_DIR = os.path.dirname(project_root)
CONVERTER_SCRIPT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "better_xpm_converter.py"
)


def ensure_directory(directory):
    """Ensure a directory exists, creating it if necessary."""
    os.makedirs(directory, exist_ok=True)
    print(f"Ensured directory exists: {directory}")


def copy_xpm_to_png(src_dir, dest_dir, pattern="*.xpm"):
    """Copy and convert XPM files to PNG format."""
    # Ensure the destination directory exists
    ensure_directory(dest_dir)

    # Find all XPM files in the source directory
    src_path = Path(src_dir)
    xpm_files = list(src_path.glob(pattern))

    print(f"Found {len(xpm_files)} XPM files in {src_dir}")

    # Process each XPM file
    for xpm_file in xpm_files:
        # Get the base name without extension
        base_name = xpm_file.stem

        # Define the destination PNG file
        png_file = os.path.join(dest_dir, f"{base_name}.png")

        # Convert XPM to PNG using our tool
        try:
            # Use the better_xpm_converter.py script
            converter_path = CONVERTER_SCRIPT

            if not os.path.exists(converter_path):
                print(f"Error: XPM converter script not found at {converter_path}")
                continue

            # Run the converter script
            cmd = ["python3", converter_path, str(xpm_file), png_file]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"Converted: {xpm_file.name} -> {os.path.basename(png_file)}")
            else:
                print(f"Error converting {xpm_file.name}: {result.stderr}")
        except Exception as e:
            print(f"Failed to convert {xpm_file.name}: {e}")


def copy_blocks():
    """Copy and convert block images."""
    # Source directories for block images
    src_dirs = [
        os.path.join(ORIGINAL_XBOING_DIR, "bitmaps/blocks"),
        os.path.join(ORIGINAL_XBOING_DIR, "bitmaps/blockex"),
    ]

    # Destination directory
    dest_dir = get_blocks_dir()

    # Process each source directory
    for src_dir in src_dirs:
        if os.path.exists(src_dir):
            copy_xpm_to_png(src_dir, dest_dir)
        else:
            print(f"Warning: Source directory not found: {src_dir}")


def copy_backgrounds():
    """Copy and convert background images."""
    # Source directory for background images
    src_dir = os.path.join(ORIGINAL_XBOING_DIR, "bitmaps/bgrnds")

    # Destination directory
    dest_dir = get_backgrounds_dir()

    if os.path.exists(src_dir):
        copy_xpm_to_png(src_dir, dest_dir)
    else:
        print(f"Warning: Source directory not found: {src_dir}")


def copy_sounds():
    """Copy sound files."""
    # Source directory for sound files
    src_dir = os.path.join(ORIGINAL_XBOING_DIR, "sounds")

    # Destination directory
    dest_dir = get_sounds_dir()

    # Ensure the destination directory exists
    ensure_directory(dest_dir)

    if not os.path.exists(src_dir):
        print(f"Warning: Source directory not found: {src_dir}")
        return

    # Find all AU files in the source directory
    au_files = list(Path(src_dir).glob("*.au"))
    print(f"Found {len(au_files)} sound files in {src_dir}")

    # Process each sound file
    for au_file in au_files:
        # For sound files, we'll need to convert .au to .wav
        # This would require additional tools, so for now just copy
        # if we have matching .wav files
        wav_name = f"{au_file.stem}.wav"

        # Check if this sound exists in the source sounds directory
        src_wav = os.path.join(project_root, "src", "assets", "sounds", wav_name)

        if os.path.exists(src_wav):
            # Copy existing converted WAV file
            dest_wav = os.path.join(dest_dir, wav_name)
            shutil.copy2(src_wav, dest_wav)
            print(
                f"Copied: {os.path.basename(src_wav)} -> {os.path.basename(dest_wav)}"
            )
        else:
            print(f"Warning: No WAV equivalent found for {au_file.name}")


def move_existing_assets():
    """Move existing assets from src/assets to the new assets directory."""
    src_assets = os.path.join(project_root, "src", "assets")

    if not os.path.exists(src_assets):
        print("No existing assets to move.")
        return

    print("Moving existing assets to new directory structure...")

    # Images - blocks
    src_blocks = os.path.join(src_assets, "images", "blocks")
    if os.path.exists(src_blocks):
        for file in os.listdir(src_blocks):
            src_file = os.path.join(src_blocks, file)
            if os.path.isfile(src_file):
                # Move file to new location
                dest_file = os.path.join(get_blocks_dir(), file)
                if not os.path.exists(dest_file):
                    shutil.copy2(src_file, dest_file)
                    print(f"Moved: {file} -> {dest_file}")

    # Images - backgrounds
    src_bgs = os.path.join(src_assets, "images", "backgrounds")
    if os.path.exists(src_bgs):
        for file in os.listdir(src_bgs):
            src_file = os.path.join(src_bgs, file)
            if os.path.isfile(src_file):
                # Move file to new location
                dest_file = os.path.join(get_backgrounds_dir(), file)
                if not os.path.exists(dest_file):
                    shutil.copy2(src_file, dest_file)
                    print(f"Moved: {file} -> {dest_file}")

    # Images - balls
    src_balls = os.path.join(src_assets, "images", "balls")
    dest_balls = os.path.join(ASSETS_DIR, "images", "balls")
    ensure_directory(dest_balls)
    if os.path.exists(src_balls):
        for file in os.listdir(src_balls):
            src_file = os.path.join(src_balls, file)
            if os.path.isfile(src_file):
                # Move file to new location
                dest_file = os.path.join(dest_balls, file)
                if not os.path.exists(dest_file):
                    shutil.copy2(src_file, dest_file)
                    print(f"Moved: {file} -> {dest_file}")

    # Sounds
    src_sounds = os.path.join(src_assets, "sounds")
    if os.path.exists(src_sounds):
        for file in os.listdir(src_sounds):
            src_file = os.path.join(src_sounds, file)
            if os.path.isfile(src_file):
                # Move file to new location
                dest_file = os.path.join(get_sounds_dir(), file)
                if not os.path.exists(dest_file):
                    shutil.copy2(src_file, dest_file)
                    print(f"Moved: {file} -> {dest_file}")


def copy_paddles():
    """Copy and convert paddle images."""
    # Source directory for paddle images
    src_dir = os.path.join(ORIGINAL_XBOING_DIR, "bitmaps/paddle")

    # Destination directory
    dest_dir = os.path.join(ASSETS_DIR, "images/paddle")

    # Ensure the destination directory exists
    ensure_directory(dest_dir)

    if os.path.exists(src_dir):
        copy_xpm_to_png(src_dir, dest_dir)
    else:
        print(f"Warning: Source directory for paddles not found: {src_dir}")


def main():
    """Main function to sync all assets."""
    print("XBoing Asset Synchronization Tool")
    print("=================================")

    # Ensure the assets directory exists
    ensure_directory(ASSETS_DIR)

    # Move existing assets first
    move_existing_assets()

    # Copy and convert block images
    print("\nProcessing block images...")
    copy_blocks()

    # Copy and convert background images
    print("\nProcessing background images...")
    copy_backgrounds()

    # Copy and convert paddle images
    print("\nProcessing paddle images...")
    copy_paddles()

    # Copy sound files
    print("\nProcessing sound files...")
    copy_sounds()

    print("\nAsset synchronization complete!")


if __name__ == "__main__":
    main()
