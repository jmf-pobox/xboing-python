#!/usr/bin/env python3
"""Convert XBoing XPM files to PNG format for the Python/SDL2 implementation.

This tool converts the original XBoing XPM files to PNG format with proper color
handling for use with the Python/SDL2 implementation.

- Default input: xboing2.4-clang/bitmaps
- Default output: assets/images
- Uses Pillow for image conversion (must be installed)
- Works on Linux and Mac OS X
- Prints a summary of converted, skipped, and failed files
- Supports --dry-run mode

Usage:
  python better_xpm_converter.py [--input INPUT_DIR] [--output OUTPUT_DIR] [--dry-run]
"""

import argparse
import logging
import os
from pathlib import Path
import re
import sys
from typing import Dict, List, Optional, Tuple

from PIL import Image

from xboing.scripts.utils import (
    print_conversion_summary,
    run_cli_conversion,
)

# Color mapping for XBoing's named colors (based on X11 color names)
X11_COLORS = {
    "black": (0, 0, 0, 255),
    "white": (255, 255, 255, 255),
    "red": (255, 0, 0, 255),
    "red1": (255, 0, 0, 255),
    "red2": (238, 0, 0, 255),
    "red3": (205, 0, 0, 255),
    "red4": (139, 0, 0, 255),
    "green": (0, 255, 0, 255),
    "green1": (0, 255, 0, 255),
    "green2": (0, 238, 0, 255),
    "green3": (0, 205, 0, 255),
    "green4": (0, 139, 0, 255),
    "blue": (0, 0, 255, 255),
    "blue1": (0, 0, 255, 255),
    "blue2": (0, 0, 238, 255),
    "blue3": (0, 0, 205, 255),
    "blue4": (0, 0, 139, 255),
    "yellow": (255, 255, 0, 255),
    "yellow1": (255, 255, 0, 255),
    "yellow2": (238, 238, 0, 255),
    "yellow3": (205, 205, 0, 255),
    "yellow4": (139, 139, 0, 255),
    "cyan": (0, 255, 255, 255),
    "magenta": (255, 0, 255, 255),
    "purple": (160, 32, 240, 255),
    "purple1": (155, 48, 255, 255),
    "purple2": (145, 44, 238, 255),
    "purple3": (125, 38, 205, 255),
    "purple4": (85, 26, 139, 255),
    "pink": (255, 192, 203, 255),
    "pink1": (255, 181, 197, 255),
    "pink2": (238, 169, 184, 255),
    "pink3": (205, 145, 158, 255),
    "pink4": (139, 99, 108, 255),
    "gold": (255, 215, 0, 255),
    "gold1": (255, 215, 0, 255),
    "gold2": (238, 201, 0, 255),
    "gold3": (205, 173, 0, 255),
    "gold4": (139, 117, 0, 255),
    "orange": (255, 165, 0, 255),
    "orange1": (255, 165, 0, 255),
    "orange2": (238, 154, 0, 255),
    "orange3": (205, 133, 0, 255),
    "orange4": (139, 90, 0, 255),
    "ivory": (255, 255, 240, 255),
    "tan": (210, 180, 140, 255),
    "tan1": (210, 180, 140, 255),  # Same as 'tan'
    "tan2": (238, 197, 145, 255),  # Slightly lighter/saturated tan
    "tan3": (205, 175, 149, 255),  # Medium tan
    "tan4": (139, 117, 85, 255),  # Darker tan for shadows
    "grey": (190, 190, 190, 255),
    "gray": (190, 190, 190, 255),
    "None": (0, 0, 0, 0),  # Transparent
}

logger = logging.getLogger("xboing.scripts.convert_xpm_to_png")


def _extract_xpm_lines(content: str) -> List[str]:
    """Extract quoted XPM data lines from the file content."""
    match = re.search(
        r"static\s+char\s+\*\s*\w+\s*\[\s*]\s*=\s*{(.*?)};", content, re.DOTALL
    )
    if not match:
        return []
    xpm_data = match.group(1).strip()
    lines = []
    for line in xpm_data.split("\n"):
        if not line.strip():
            continue
        quote_match = re.search(r'"([^"]*)"', line)
        if quote_match:
            lines.append(quote_match.group(1))
    return lines


def _parse_xpm_header(lines: List[str]) -> Optional[Tuple[int, int, int, int, int]]:
    """Parse the XPM header and return (header_index, width, height, num_colors, chars_per_pixel)."""
    header_index = 0
    while header_index < len(lines) and (
        lines[header_index].startswith("/*") or not lines[header_index].strip()
    ):
        header_index += 1
    if header_index >= len(lines):
        return None
    header = lines[header_index].split()
    try:
        width = int(header[0])
        height = int(header[1])
        num_colors = int(header[2])
        chars_per_pixel = int(header[3])
        return header_index, width, height, num_colors, chars_per_pixel
    except (ValueError, IndexError):
        return None


def _parse_xpm_color_table(
    lines: List[str], header_index: int, num_colors: int, chars_per_pixel: int
) -> Optional[Dict[str, Tuple[int, int, int, int]]]:
    """Parse the color table from XPM lines."""
    color_table = {}
    for i in range(header_index + 1, header_index + num_colors + 1):
        if i >= len(lines):
            return None
        color_line = lines[i]
        if len(color_line) < chars_per_pixel:
            return None
        key = color_line[:chars_per_pixel]
        if re.search(r"c\s+None", color_line):
            color_table[key] = (0, 0, 0, 0)
            continue
        hex_match = re.search(r"c\s+#([0-9A-Fa-f]{6})", color_line)
        if hex_match:
            color_hex = hex_match.group(1)
            r = int(color_hex[0:2], 16)
            g = int(color_hex[2:4], 16)
            b = int(color_hex[4:6], 16)
            color_table[key] = (r, g, b, 255)
            continue
        hex_match_long = re.search(r"c\s+#([0-9A-Fa-f]{8,12})", color_line)
        if hex_match_long:
            color_hex = hex_match_long.group(1)
            if len(color_hex) == 12:
                r = int(color_hex[0:4], 16) >> 8
                g = int(color_hex[4:8], 16) >> 8
                b = int(color_hex[8:12], 16) >> 8
            elif len(color_hex) == 8:
                r = int(color_hex[0:2], 16)
                g = int(color_hex[2:4], 16)
                b = int(color_hex[4:6], 16)
                a = int(color_hex[6:8], 16)
                color_table[key] = (r, g, b, a)
                continue
            else:
                r = int(color_hex[0:2], 16)
                g = int(color_hex[2:4], 16)
                b = int(color_hex[4:6], 16)
            color_table[key] = (r, g, b, 255)
            continue
        named_match = re.search(r"c\s+(\w+)", color_line)
        if named_match:
            color_name = named_match.group(1).lower()
            color_table[key] = X11_COLORS.get(color_name, (0, 0, 0, 255))
            continue
        color_table[key] = (0, 0, 0, 255)
    return color_table


def _parse_xpm_pixels(
    lines: List[str],
    pixel_start_index: int,
    height: int,
    chars_per_pixel: int,
    color_table: Dict[str, Tuple[int, int, int, int]],
) -> List[List[Tuple[int, int, int, int]]]:
    """Parse the pixel data from XPM lines."""
    pixels = []
    for i in range(pixel_start_index, pixel_start_index + height):
        if i >= len(lines):
            break
        row = lines[i]
        row_pixels = []
        for j in range(0, len(row), chars_per_pixel):
            if j + chars_per_pixel <= len(row):
                pixel_key = row[j : j + chars_per_pixel]
                row_pixels.append(color_table.get(pixel_key, (0, 0, 0, 255)))
        pixels.append(row_pixels)
    return pixels


def _validate_xpm_pixels(
    pixels: List[List[Tuple[int, int, int, int]]],
    width: int,
    height: int,
    xpm_file: str,
) -> None:
    if len(pixels) != height:
        logger.warning(
            f"Warning: Expected {height} rows, got {len(pixels)} in {xpm_file}"
        )
    for row_index, row in enumerate(pixels):
        if len(row) != width:
            logger.warning(
                f"Warning: Row {row_index} expected {width} pixels, got {len(row)} in {xpm_file}"
            )


def parse_xpm(
    xpm_file: str,
) -> Optional[Tuple[int, int, List[List[Tuple[int, int, int, int]]]]]:
    """Parse an XPM file and extract image data.

    Args:
    ----
        xpm_file (str): Path to the XPM file

    Returns:
    -------
        tuple: (width, height, pixels) or None on failure

    """
    with open(xpm_file, encoding="utf-8") as f:
        content = f.read()

    logger.info(f"\nParsing {xpm_file}")

    lines = _extract_xpm_lines(content)
    if not lines:
        logger.error(f"Failed to parse XPM data in {xpm_file}")
        return None

    header_info = _parse_xpm_header(lines)
    if not header_info:
        logger.error(f"Invalid XPM header in {xpm_file}: {lines}")
        return None

    header_index, width, height, num_colors, chars_per_pixel = header_info

    logger.info(f"Header line: '{lines[header_index]}'")

    color_table = _parse_xpm_color_table(
        lines, header_index, num_colors, chars_per_pixel
    )
    if color_table is None:
        logger.error(f"Unexpected end of color table in {xpm_file}")
        return None

    pixel_start_index = header_index + num_colors + 1
    pixels = _parse_xpm_pixels(
        lines, pixel_start_index, height, chars_per_pixel, color_table
    )
    _validate_xpm_pixels(pixels, width, height, xpm_file)

    return width, height, pixels


def convert_xpm_to_png(xpm_path: str, png_path: str) -> bool:
    """Convert an XPM file to a PNG file.

    Args:
    ----
        xpm_path (str): Path to the XPM file
        png_path (str): Path to save the PNG file

    Returns:
    -------
        bool: True if successful, False otherwise

    """
    result = False
    xpm_data = parse_xpm(xpm_path)
    if not xpm_data:
        return result

    width, height, pixels = xpm_data

    # Create a new image with RGBA mode for transparency
    img = Image.new("RGBA", (width, height))

    # Set pixels with proper handling of array bounds
    for y in range(height):
        if y >= len(pixels):
            # If we're missing rows, fill with transparent pixels
            for x in range(width):
                img.putpixel((x, y), (0, 0, 0, 0))
        else:
            row = pixels[y]
            for x in range(width):
                if x < len(row):
                    img.putpixel((x, y), row[x])
                else:
                    # If we're missing pixels in a row, fill with transparent
                    img.putpixel((x, y), (0, 0, 0, 0))

    # Verify the image has valid pixel data (not all transparent or black)
    valid_pixels = 0
    for y in range(height):
        for x in range(width):
            pixel = img.getpixel((x, y))
            if (
                isinstance(pixel, tuple)
                and len(pixel) == 4
                and pixel[3] > 0
                and sum(pixel[:3]) > 0
            ):
                valid_pixels += 1

    if valid_pixels == 0:
        logger.warning(
            f"Warning: Image {os.path.basename(xpm_path)} has no visible pixels, generating a placeholder."
        )
        base_name = os.path.basename(xpm_path)

        def get_placeholder_color(name: str) -> Tuple[int, int, int, int]:
            name = name.lower()
            color_map = [
                ("blue", (60, 120, 255, 255)),
                ("red", (255, 60, 60, 255)),
                ("green", (40, 220, 40, 255)),
                ("grn", (40, 220, 40, 255)),
                ("yellow", (255, 255, 40, 255)),
                ("yell", (255, 255, 40, 255)),
                ("purple", (200, 40, 200, 255)),
                ("purp", (200, 40, 200, 255)),
                ("tan", (210, 180, 140, 255)),
                ("black", (40, 40, 40, 255)),
            ]
            for key, color in color_map:
                if key in name:
                    return color
            return (150, 150, 150, 255)

        color = get_placeholder_color(base_name)
        # Create a rounded block with a 3D effect
        for y in range(height):
            for x in range(width):
                # Leave corners transparent
                is_corner = (
                    (x < 2 and y < 2)
                    or (x < 2 and y >= height - 2)
                    or (x >= width - 2 and y < 2)
                    or (x >= width - 2 and y >= height - 2)
                )
                is_main_body = 2 <= x < width - 2 and 2 <= y < height - 2
                is_top_edge = y < 2 or x < 2
                is_bottom_edge = y >= height - 2 or x >= width - 2
                if is_corner:
                    img.putpixel((x, y), (0, 0, 0, 0))
                elif is_main_body:
                    img.putpixel((x, y), color)
                elif is_top_edge:
                    highlight = (
                        min(255, color[0] + 40),
                        min(255, color[1] + 40),
                        min(255, color[2] + 40),
                        255,
                    )
                    img.putpixel((x, y), highlight)
                elif is_bottom_edge:
                    shadow = (
                        max(0, color[0] - 40),
                        max(0, color[1] - 40),
                        max(0, color[2] - 40),
                        255,
                    )
                    img.putpixel((x, y), shadow)

    try:
        img.save(png_path, optimize=True)
        logger.info(f"Successfully converted {xpm_path} to {png_path}")
        result = True
    except Exception as e:
        logger.error(f"Failed to save PNG {png_path}: {e}")
        result = False

    return result


def convert_directory(
    input_dir: Path, output_dir: Path, dry_run: bool = False
) -> Dict[str, List[str]]:
    """Convert all XPM files in a directory tree to PNG.

    Args:
    ----
        input_dir (Path): Input directory with XPM files
        output_dir (Path): Output directory for PNG files
        dry_run (bool): If True, do not convert
    Returns:
        dict: {'converted': [...], 'skipped': [...], 'failed': [...]}

    """
    results: Dict[str, List[str]] = {"converted": [], "skipped": [], "failed": []}
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith(".xpm"):
                rel_path = os.path.relpath(root, input_dir)
                out_subdir = Path(output_dir) / rel_path
                out_subdir.mkdir(parents=True, exist_ok=True)
                xpm_path = Path(root) / file
                png_name = Path(file).with_suffix(".png").name
                png_path = out_subdir / png_name
                if png_path.exists():
                    logger.info(
                        f"[SKIP] {png_path.relative_to(output_dir)} already exists."
                    )
                    results["skipped"].append(str(xpm_path.relative_to(input_dir)))
                    continue
                if dry_run:
                    logger.info(
                        f"[DRY-RUN] Would convert {xpm_path.relative_to(input_dir)} -> {png_path.relative_to(output_dir)}"
                    )
                    results["converted"].append(str(xpm_path.relative_to(input_dir)))
                    continue
                logger.info(f"Converting {xpm_path} to {png_path}...")
                try:
                    if convert_xpm_to_png(str(xpm_path), str(png_path)):
                        results["converted"].append(
                            str(xpm_path.relative_to(input_dir))
                        )
                    else:
                        results["failed"].append(str(xpm_path.relative_to(input_dir)))
                except Exception as e:
                    logger.error(f"[FAIL] Error converting {xpm_path}: {e}")
                    results["failed"].append(str(xpm_path.relative_to(input_dir)))
    return results


def main() -> int:
    """Convert XBoing XPM files to PNG format for the Python/SDL2 implementation.

    Returns
    -------
        int: Exit code (0 for success, 1 for error)

    """
    parser = argparse.ArgumentParser(
        description="Convert XBoing XPM files to PNG format. Requires Pillow."
    )
    return run_cli_conversion(
        parser,
        "xboing2.4-clang/bitmaps",
        "assets/images",
        logger,
        convert_directory,
        print_conversion_summary,
    )


if __name__ == "__main__":
    sys.exit(main())
