#!/usr/bin/env python3
"""
Fix Background Image Converter

This script is specifically designed to correctly convert the XBoing
background pattern XPM to a PNG file for the Python port.

Usage:
  python fix_background.py [--input INPUT_FILE] [--output OUTPUT_FILE]
  (Defaults: input=xboing2.4-clang/bitmaps/bgrnds/bgrnd.xpm, output=assets/images/bgrnds/bgrnd.png)
"""
import argparse
import sys
from pathlib import Path
import logging

from PIL import Image

logger = logging.getLogger("xboing.scripts.fix_background")


def create_background_from_xpm(xpm_path, png_path):
    """
    Convert the XBoing background XPM to a PNG file.

    This function is specifically designed for the bgrnd.xpm file.
    """
    # Define the colors directly from the XPM file
    colors = {
        " ": (134, 134, 134),  # #868686 (medium gray)
        ".": (171, 171, 171),  # #ABABAB (light gray)
        "X": (101, 101, 101),  # #656565 (dark gray)
    }

    # Read the XPM file to extract the pattern
    pattern_data = []
    pixel_data_started = False

    with open(xpm_path) as f:
        for line in f:
            line = line.strip()
            if "/* pixels */" in line:
                pixel_data_started = True
                continue

            if pixel_data_started and '"' in line:
                # Extract the pattern data from between quotes
                pattern_row = line.split('"')[1].split('"')[0]
                if pattern_row:
                    pattern_data.append(pattern_row)

    if not pattern_data:
        logger.error(f"Failed to extract pattern data from {xpm_path}")
        return False

    # Create a new image
    width = len(pattern_data[0])
    height = len(pattern_data)
    img = Image.new("RGB", (width, height))

    logger.info(f"Creating {width}x{height} image from pattern data")

    # Set pixels according to the pattern
    for y, row in enumerate(pattern_data):
        for x, char in enumerate(row):
            if char in colors:
                img.putpixel((x, y), colors[char])
            else:
                logger.warning(f"Warning: Unknown character '{char}' at ({x}, {y})")
                img.putpixel((x, y), (0, 0, 0))  # Default to black

    # Save the image
    img.save(png_path)
    logger.info(f"Saved background image to {png_path}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Convert bgrnd.xpm to PNG for XBoing Python port."
    )
    parser.add_argument(
        "--input",
        "-i",
        default="xboing2.4-clang/bitmaps/bgrnds/bgrnd.xpm",
        help="Input XPM file (default: xboing2.4-clang/bitmaps/bgrnds/bgrnd.xpm)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="assets/images/bgrnds/bgrnd.png",
        help="Output PNG file (default: assets/images/bgrnds/bgrnd.png)",
    )
    args = parser.parse_args()
    xpm_path = Path(args.input).resolve()
    png_path = Path(args.output).resolve()
    png_path.parent.mkdir(parents=True, exist_ok=True)
    if not xpm_path.exists():
        logger.error(f"Input file {xpm_path} does not exist")
        return 1
    if create_background_from_xpm(str(xpm_path), str(png_path)):
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
