#!/usr/bin/env python3
"""
Audio Converter (Cross-Platform, Modernized)

This script converts .au audio files from the legacy XBoing C codebase to .wav format for the Python port.
- Default input: xboing2.4-clang/sounds/
- Default output: assets/sounds/
- Uses ffmpeg for conversion (must be installed and in PATH)
- Works on Linux and Mac OS X
- Prints a summary of converted, skipped, and failed files

Usage:
  python convert_audio.py [--input INPUT_DIR] [--output OUTPUT_DIR] [--dry-run]
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Dict, List


def check_ffmpeg():
    """Check if ffmpeg is available in PATH."""
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            check=True,
            capture_output=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def convert_au_to_wav(input_file, output_file=None, dry_run=False):
    """
    Convert an .au file to .wav format using ffmpeg.
    Args:
        input_file (Path): Path to the .au file
        output_file (Path): Path for the output .wav file (optional)
        dry_run (bool): If True, do not actually convert
    Returns:
        bool: True if converted, False if failed or skipped
    """
    if output_file is None:
        output_file = input_file.with_suffix(".wav")
    if output_file.exists():
        print(f"[SKIP] {output_file.name} already exists.")
        return None  # Skipped
    if dry_run:
        print(f"[DRY-RUN] Would convert {input_file.name} -> {output_file.name}")
        return True
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(input_file),
                str(output_file),
            ],
            check=True,
            capture_output=True,
        )
        print(f"[OK] Converted {input_file.name} -> {output_file.name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[FAIL] Error converting {input_file.name}: {e}")
        return False
    except FileNotFoundError:
        print("[FAIL] ffmpeg not found. Please install ffmpeg on your system.")
        return False


def convert_directory(input_dir, output_dir, dry_run=False):
    """
    Convert all .au files in a directory to .wav format.
    Args:
        input_dir (Path): Directory containing .au files
        output_dir (Path): Directory to save .wav files
        dry_run (bool): If True, do not actually convert
    Returns:
        dict: {'converted': [...], 'skipped': [...], 'failed': [...]}
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    au_files = sorted(input_dir.glob("*.au"))
    results: Dict[str, List[str]] = {"converted": [], "skipped": [], "failed": []}
    for au_file in au_files:
        wav_file = output_dir / (au_file.stem + ".wav")
        result = convert_au_to_wav(au_file, wav_file, dry_run=dry_run)
        if result is True:
            results["converted"].append(au_file.name)
        elif result is None:
            results["skipped"].append(au_file.name)
        else:
            results["failed"].append(au_file.name)
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Convert .au audio files from legacy XBoing to .wav for Python port. Requires ffmpeg."
    )
    parser.add_argument(
        "--input",
        "-i",
        default="xboing2.4-clang/sounds",
        help="Input directory containing .au files (default: xboing2.4-clang/sounds)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="assets/sounds",
        help="Output directory for .wav files (default: assets/sounds)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be converted, but do not actually convert.",
    )
    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    output_path = Path(args.output).resolve()

    if not input_path.exists() or not input_path.is_dir():
        print(
            f"[ERROR] Input directory {input_path} does not exist or is not a directory."
        )
        return 1
    if not check_ffmpeg():
        print(
            "[ERROR] ffmpeg is not installed or not in PATH. Please install ffmpeg to use this script."
        )
        return 1

    print(f"Input:  {input_path}")
    print(f"Output: {output_path}")
    print(f"Mode:   {'DRY-RUN' if args.dry_run else 'CONVERT'}\n")

    results = convert_directory(input_path, output_path, dry_run=args.dry_run)
    print("\nSummary:")
    print(f"  Converted: {len(results['converted'])}")
    print(f"  Skipped:   {len(results['skipped'])}")
    print(f"  Failed:    {len(results['failed'])}")
    if results["failed"]:
        print("  Failed files:")
        for f in results["failed"]:
            print(f"    - {f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
