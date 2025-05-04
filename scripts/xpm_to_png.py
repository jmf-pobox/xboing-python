#!/usr/bin/env python3
"""
XPM to PNG Converter

This tool converts the original XBoing XPM files to PNG format
for use with the new Python/SDL2 implementation.

Usage:
  python xpm_to_png.py [input_directory] [output_directory]
"""

import os
import sys
import re
import argparse
from PIL import Image

def parse_xpm(xpm_file):
    """
    Parse an XPM file and extract image data.
    
    Args:
        xpm_file (str): Path to the XPM file
        
    Returns:
        tuple: (width, height, pixels) or None on failure
    """
    with open(xpm_file, 'r') as f:
        content = f.read()
    
    print(f"\nDEBUG: Parsing {xpm_file}")
    
    # Extract the XPM data array with improved regex pattern
    # This handles both formats:
    # static char *name[] = { ... };
    # static char * name [] = { ... };
    match = re.search(r'static\s+char\s+\*\s*\w+\s*\[\s*\]\s*=\s*{(.*?)};', content, re.DOTALL)
    if not match:
        print(f"Failed to parse XPM data in {xpm_file}")
        return None
    
    xpm_data = match.group(1).strip()
    # Clean up lines, handling quoted strings properly
    lines = []
    for line in xpm_data.split('\n'):
        line = line.strip()
        if not line:
            continue
        
        # Extract quoted strings
        quote_match = re.search(r'"([^"]*)"', line)
        if quote_match:
            lines.append(quote_match.group(1))
    
    # Parse header (first line after comments)
    header_index = 0
    while header_index < len(lines) and (lines[header_index].startswith('/*') or not lines[header_index].strip()):
        header_index += 1
    
    if header_index >= len(lines):
        print(f"Could not find header in {xpm_file}")
        return None
    
    print(f"DEBUG: Header line: '{lines[header_index]}'")
    
    header = lines[header_index].split()
    try:
        width = int(header[0])
        height = int(header[1])
        num_colors = int(header[2])
        chars_per_pixel = int(header[3])
        print(f"DEBUG: Parsed header: width={width}, height={height}, colors={num_colors}, chars_per_pixel={chars_per_pixel}")
    except (ValueError, IndexError):
        print(f"Invalid XPM header in {xpm_file}: {lines[header_index]}")
        return None
    
    # Parse color table
    color_table = {}
    for i in range(header_index + 1, header_index + num_colors + 1):
        if i >= len(lines):
            print(f"Unexpected end of color table in {xpm_file}")
            return None
            
        color_line = lines[i]
        if len(color_line) < chars_per_pixel:
            print(f"Invalid color definition in {xpm_file}, line too short: {color_line}")
            return None
            
        key = color_line[:chars_per_pixel]
        print(f"DEBUG: Color key '{key}', line: '{color_line}'") 
        
        # Handle special case for None (transparent) with 's None' syntax
        none_match = re.search(r's\s+None\s+c\s+None', color_line)
        if none_match:
            r, g, b, a = 0, 0, 0, 0  # Transparent
            color_table[key] = (r, g, b, a)
            continue
        
        # Extract color
        # Try hex color format (#RRGGBB)
        hex_match = re.search(r'c\s+#([0-9A-Fa-f]{6})', color_line)
        if hex_match:
            color_hex = hex_match.group(1)
            r = int(color_hex[0:2], 16)
            g = int(color_hex[2:4], 16)
            b = int(color_hex[4:6], 16)
            a = 255  # Fully opaque
            color_table[key] = (r, g, b, a)
            continue
            
        # Try None without s None format
        if re.search(r'c\s+None', color_line):
            r, g, b, a = 0, 0, 0, 0  # Transparent
            color_table[key] = (r, g, b, a)
            continue
            
        # Try named colors
        named_match = re.search(r'c\s+(\w+)', color_line)
        if named_match:
            color_name = named_match.group(1).lower()
            # Handle common named colors
            if color_name == 'black':
                r, g, b, a = 0, 0, 0, 255
            elif color_name == 'white':
                r, g, b, a = 255, 255, 255, 255
            elif color_name == 'red':
                r, g, b, a = 255, 0, 0, 255
            elif color_name == 'green':
                r, g, b, a = 0, 255, 0, 255
            elif color_name == 'blue':
                r, g, b, a = 0, 0, 255, 255
            elif color_name == 'yellow':
                r, g, b, a = 255, 255, 0, 255
            elif color_name == 'cyan':
                r, g, b, a = 0, 255, 255, 255
            elif color_name == 'magenta':
                r, g, b, a = 255, 0, 255, 255
            else:
                print(f"Unknown color name {color_name} in {xpm_file}, using black")
                r, g, b, a = 0, 0, 0, 255
                
            color_table[key] = (r, g, b, a)
            continue
            
        # Check for 'None c None' format
        if 'None' in color_line and 'c' in color_line:
            r, g, b, a = 0, 0, 0, 0  # Transparent
            color_table[key] = (r, g, b, a)
            continue
            
        print(f"Could not parse color in {xpm_file}, line: {color_line} - using black")
        color_table[key] = (0, 0, 0, 255)  # Default to black
    
    # Parse pixel data
    pixels = []
    pixel_start_index = header_index + num_colors + 1
    print(f"DEBUG: Pixel data starts at index {pixel_start_index} (line {pixel_start_index+1})")
    print(f"DEBUG: Color table has {len(color_table)} entries: {list(color_table.keys())}")
    
    for i in range(pixel_start_index, pixel_start_index + height):
        if i >= len(lines):
            print(f"Unexpected end of pixel data in {xpm_file}")
            return None
            
        row = lines[i]
        print(f"DEBUG: Pixel row {i-pixel_start_index}: '{row}' (length={len(row)})")
        row_pixels = []
        
        for j in range(0, len(row), chars_per_pixel):
            if j + chars_per_pixel <= len(row):
                pixel_key = row[j:j+chars_per_pixel]
                if pixel_key in color_table:
                    row_pixels.append(color_table[pixel_key])
                else:
                    print(f"Unknown pixel key '{pixel_key}' in {xpm_file}, row {i}, column {j}")
                    row_pixels.append((0, 0, 0, 255))  # Default to black
        
        pixels.append(row_pixels)
        print(f"DEBUG: Row {i-pixel_start_index} has {len(row_pixels)} pixels")
    
    # Verify image dimensions
    if len(pixels) != height:
        print(f"Warning: Expected {height} rows, got {len(pixels)} in {xpm_file}")
    
    for row_index, row in enumerate(pixels):
        if len(row) != width:
            print(f"Warning: Row {row_index} expected {width} pixels, got {len(row)} in {xpm_file}")
    
    return width, height, pixels

def convert_xpm_to_png(xpm_path, png_path):
    """
    Convert an XPM file to a PNG file.
    
    Args:
        xpm_path (str): Path to the XPM file
        png_path (str): Path to save the PNG file
        
    Returns:
        bool: True if successful, False otherwise
    """
    result = parse_xpm(xpm_path)
    if not result:
        return False
        
    width, height, pixels = result
    
    # Create a new image with RGBA mode for transparency
    img = Image.new('RGBA', (width, height))
    
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
    
    # Save the image with maximum quality
    img.save(png_path, optimize=True)
    
    print(f"Successfully converted {xpm_path} to {png_path}")
    return True

def convert_directory(input_dir, output_dir):
    """
    Convert all XPM files in a directory to PNG.
    
    Args:
        input_dir (str): Input directory with XPM files
        output_dir (str): Output directory for PNG files
        
    Returns:
        int: Number of successfully converted files
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    success_count = 0
    
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.xpm'):
                # Create matching output subdirectory
                rel_path = os.path.relpath(root, input_dir)
                out_subdir = os.path.join(output_dir, rel_path)
                if not os.path.exists(out_subdir):
                    os.makedirs(out_subdir)
                
                # Convert the file
                xpm_path = os.path.join(root, file)
                png_name = os.path.splitext(file)[0] + '.png'
                png_path = os.path.join(out_subdir, png_name)
                
                print(f"Converting {xpm_path} to {png_path}...")
                if convert_xpm_to_png(xpm_path, png_path):
                    success_count += 1
    
    return success_count

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Convert XBoing XPM files to PNG format')
    parser.add_argument('input', 
                       help='Input XPM file or directory')
    parser.add_argument('output',
                       help='Output PNG file or directory')
    
    args = parser.parse_args()
    
    input_path = os.path.abspath(args.input)
    output_path = os.path.abspath(args.output)
    
    if not os.path.exists(input_path):
        print(f"Input path {input_path} does not exist")
        return 1
    
    # Check if input is a file or directory
    if os.path.isfile(input_path):
        # Single file conversion
        print(f"Converting single XPM file {input_path} to {output_path}")
        if convert_xpm_to_png(input_path, output_path):
            print("Conversion successful")
            return 0
        else:
            print("Conversion failed")
            return 1
    else:
        # Directory conversion
        if not os.path.exists(output_path):
            os.makedirs(output_path)
            
        print(f"Converting XPM files from {input_path} to {output_path}...")
        count = convert_directory(input_path, output_path)
        print(f"Successfully converted {count} files")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())