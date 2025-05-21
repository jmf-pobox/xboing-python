#!/usr/bin/env python3
"""Convert the XBoing background pattern XPM to a PNG file for the Python port.

This script is specifically designed to correctly convert the XBoing
background pattern XPM to a PNG file for the Python port.

Usage:
  python fix_background.py [--input INPUT_FILE] [--output OUTPUT_FILE]
  (Defaults: input=xboing2.4-clang/bitmaps/bgrnds/bgrnd.xpm, output=assets/images/bgrnds/bgrnd.png)
"""

import argparse
import logging
from pathlib import Path
import sys

from PIL import Image

logger = logging.getLogger("xboing.scripts.fix_background")


def create_background_from_xpm(xpm_path: str, png_path: str) -> bool:
    """Convert the XBoing background XPM to a PNG file.

    This function is specifically designed for the bgrnd.xpm file.

    Args:
    ----
        xpm_path (str): Path to the input XPM file.
        png_path (str): Path to the output PNG file.

    Returns:
    -------
        bool: True if successful, False otherwise.

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

    with open(xpm_path, encoding="utf-8") as f:
        for line in f:
            if "/* pixels */" in line.strip():
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


def main() -> int:
    """Convert the XBoing background pattern XPM to a PNG file for the Python port.

    Returns
    -------
        int: Exit code (0 for success, 1 for error)

    """
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
    return 1


if __name__ == "__main__":
    sys.exit(main())
