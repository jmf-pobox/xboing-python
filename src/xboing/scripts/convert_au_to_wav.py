#!/usr/bin/env python3
# pylint: disable=duplicate-code
"""Convert .au audio files from the legacy XBoing C codebase to .wav format for the Python port.

- Default input: xboing2.4-clang/sounds/
- Default output: assets/sounds/
- Uses ffmpeg for conversion (must be installed and in PATH)
- Works on Linux and Mac OS X
- Prints a summary of converted, skipped, and failed files

Usage:
  python convert_audio.py [--input INPUT_DIR] [--output OUTPUT_DIR] [--dry-run]
"""

import argparse
import logging
from pathlib import Path
import subprocess
import sys
from typing import Dict, List, Optional

from xboing.scripts.utils import (
    print_conversion_summary,
    run_cli_conversion,
)

logger = logging.getLogger("xboing.scripts.convert_au_to_wav")


def check_ffmpeg() -> bool:
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


def convert_au_to_wav(
    input_file: Path, output_file: Optional[Path] = None, dry_run: bool = False
) -> Optional[bool]:
    """Convert an .au file to .wav format using ffmpeg.

    Args:
    ----
        input_file (Path): Path to the .au file
        output_file (Path): Path for the output .wav file (optional)
        dry_run (bool): If True, do not convert
    Returns:
        bool: True if converted, False if failed, None if skipped

    """
    if output_file is None:
        output_file = input_file.with_suffix(".wav")
    if output_file.exists():
        logger.info(f"[SKIP] {output_file.name} already exists.")
        return None  # Skipped
    if dry_run:
        logger.info(f"[DRY-RUN] Would convert {input_file.name} -> {output_file.name}")
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
        logger.info(f"[OK] Converted {input_file.name} -> {output_file.name}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"[FAIL] Error converting {input_file.name}: {e}")
        return False
    except FileNotFoundError:
        logger.error("[FAIL] ffmpeg not found. Please install ffmpeg on your system.")
        return False


def convert_directory(
    input_dir: Path, output_dir: Path, dry_run: bool = False
) -> Dict[str, List[str]]:
    """Convert all .au files in a directory to .wav format.

    Args:
    ----
        input_dir (Path): Directory containing .au files
        output_dir (Path): Directory to save .wav files
        dry_run (bool): If True, do not convert
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


def main() -> int:
    """Convert .au audio files from the legacy XBoing C codebase to .wav format for the Python port.

    Returns
    -------
        int: Exit code (0 for success, 1 for error)

    """
    parser = argparse.ArgumentParser(
        description="Convert .au audio files from legacy XBoing to .wav for Python port. Requires ffmpeg."
    )

    def conversion_func(input_path, output_path, dry_run=False):
        if not check_ffmpeg():
            logger.error(
                "[ERROR] ffmpeg is not installed or not in PATH. Please install ffmpeg to use this script."
            )
            return {"converted": [], "skipped": [], "failed": ["ffmpeg missing"]}
        return convert_directory(input_path, output_path, dry_run=dry_run)

    return run_cli_conversion(
        parser,
        "xboing2.4-clang/sounds",
        "assets/sounds",
        logger,
        conversion_func,
        print_conversion_summary,
    )


if __name__ == "__main__":
    sys.exit(main())
