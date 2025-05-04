#!/usr/bin/env python3
"""
Fix Background Image Converter

This script is specifically designed to correctly convert the XBoing
background pattern XPM to a PNG file for the Python port.
"""

import os
import sys

from PIL import Image


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
        print(f"Failed to extract pattern data from {xpm_path}")
        return False

    # Create a new image
    width = len(pattern_data[0])
    height = len(pattern_data)
    img = Image.new("RGB", (width, height))

    print(f"Creating {width}x{height} image from pattern data")

    # Set pixels according to the pattern
    for y, row in enumerate(pattern_data):
        for x, char in enumerate(row):
            if char in colors:
                img.putpixel((x, y), colors[char])
            else:
                print(f"Warning: Unknown character '{char}' at ({x}, {y})")
                img.putpixel((x, y), (0, 0, 0))  # Default to black

    # Save the image
    img.save(png_path)
    print(f"Saved background image to {png_path}")
    return True


def main():
    """Main entry point."""
    if len(sys.argv) != 3:
        print("Usage: python fix_background.py <xpm_file> <png_file>")
        return 1

    xpm_path = os.path.abspath(sys.argv[1])
    png_path = os.path.abspath(sys.argv[2])

    if not os.path.exists(xpm_path):
        print(f"Input file {xpm_path} does not exist")
        return 1

    if create_background_from_xpm(xpm_path, png_path):
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
