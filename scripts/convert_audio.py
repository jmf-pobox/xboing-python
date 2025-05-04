#!/usr/bin/env python3
"""
Audio Converter

This script converts .au audio files to .wav format that pygame can play.
Requires the pydub library (pip install pydub) and ffmpeg.
"""

import argparse
import glob
import os
import subprocess
import sys


def convert_au_to_wav(input_file, output_file=None):
    """
    Convert an .au file to .wav format using ffmpeg.

    Args:
        input_file (str): Path to the .au file
        output_file (str): Path for the output .wav file (optional)

    Returns:
        str: Path to the output file
    """
    if output_file is None:
        # Create output filename by replacing .au with .wav
        output_file = os.path.splitext(input_file)[0] + ".wav"

    # Run ffmpeg to convert the file
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",  # Overwrite output files without asking
                "-i",
                input_file,  # Input file
                output_file,  # Output file
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        print(f"Converted {input_file} to {output_file}")
        return output_file
    except subprocess.CalledProcessError as e:
        print(f"Error converting {input_file}: {e}")
        return None
    except FileNotFoundError:
        print("Error: ffmpeg not found. Please install ffmpeg on your system.")
        return None


def convert_directory(input_dir, output_dir):
    """
    Convert all .au files in a directory to .wav format.

    Args:
        input_dir (str): Directory containing .au files
        output_dir (str): Directory to save .wav files

    Returns:
        int: Number of successfully converted files
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Find all .au files in the input directory
    au_files = glob.glob(os.path.join(input_dir, "*.au"))
    success_count = 0

    for au_file in au_files:
        filename = os.path.basename(au_file)
        wav_file = os.path.join(output_dir, os.path.splitext(filename)[0] + ".wav")

        if convert_au_to_wav(au_file, wav_file):
            success_count += 1

    return success_count


def main():
    parser = argparse.ArgumentParser(
        description="Convert .au audio files to .wav format"
    )
    parser.add_argument(
        "--input", "-i", default="../sounds", help="Input directory or file"
    )
    parser.add_argument(
        "--output", "-o", default="../src/assets/sounds", help="Output directory"
    )

    args = parser.parse_args()

    # Resolve paths relative to script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.abspath(os.path.join(script_dir, args.input))
    output_path = os.path.abspath(os.path.join(script_dir, args.output))

    if os.path.isdir(input_path):
        # Convert all files in directory
        count = convert_directory(input_path, output_path)
        print(f"Successfully converted {count} files")
    elif os.path.isfile(input_path):
        # Convert single file
        if input_path.lower().endswith(".au"):
            output_file = os.path.join(
                output_path, os.path.splitext(os.path.basename(input_path))[0] + ".wav"
            )
            convert_au_to_wav(input_path, output_file)
        else:
            print(f"Error: {input_path} is not an .au file")
    else:
        print(f"Error: {input_path} not found")

    return 0


if __name__ == "__main__":
    sys.exit(main())
