#!/usr/bin/env python3
# pylint: disable=duplicate-code

"""
XBoing Audio Normalization Script.

This script normalizes the loudness of all .wav files in a directory using ffmpeg's loudnorm filter.

Purpose:
    Ensures consistent audio volume for all game sounds by applying EBU R128 normalization.
    This script should be run after converting or adding new audio files to the project.

Usage:
    python scripts/normalize_audio.py --input <input_dir> --output <output_dir>
    (Defaults: input=assets/sounds, output=assets/sounds/normalized)

Dependencies:
    - Python 3.7+
    - ffmpeg (must be installed and available in your PATH)

Notes:
    - Only .wav files in the input directory are processed.
    - Output files will be written to the specified output directory.
    - Run this script after converting or adding new audio files to ensure all sounds are normalized.

"""
import argparse
import logging
from pathlib import Path
import subprocess

from xboing.scripts.utils import (
    print_conversion_summary,
    run_cli_conversion,
)

logger = logging.getLogger("xboing.scripts.normalize_audio")


def normalize_wav(input_file: Path, output_file: Path) -> bool:
    """Normalize a .wav file using ffmpeg's loudnorm filter."""
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(input_file),
                "-af",
                "loudnorm=I=-16:TP=-1.5:LRA=11",
                str(output_file),
            ],
            check=True,
            capture_output=True,
        )
        logger.info(f"Normalized {input_file.name} -> {output_file.name}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to normalize {input_file.name}: {e}")
        return False


def normalize_directory(input_path, output_path, dry_run=False):
    """Normalize all .wav files in the input directory and return a results dict."""
    output_path.mkdir(parents=True, exist_ok=True)
    converted = []
    skipped = []
    failed = []
    for wav_file in input_path.glob("*.wav"):
        out_file = output_path / wav_file.name
        if dry_run:
            skipped.append(str(wav_file))
            continue
        try:
            normalize_wav(wav_file, out_file)
            converted.append(str(wav_file))
        except Exception:
            failed.append(str(wav_file))
    return {"converted": converted, "skipped": skipped, "failed": failed}


def main() -> int:
    """Parse arguments and normalize all .wav files in the input directory."""
    parser = argparse.ArgumentParser(
        description="Normalize loudness of .wav files in a directory."
    )

    def conversion_func(input_path, output_path, dry_run=False):
        return normalize_directory(input_path, output_path, dry_run=dry_run)

    return run_cli_conversion(
        parser,
        "assets/sounds",
        "assets/sounds/normalized",
        logger,
        conversion_func,
        print_conversion_summary,
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
