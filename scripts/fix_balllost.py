#!/usr/bin/env python3
"""Fix and convert the balllost.au file with a corrupted header to .wav format.

Usage:
  python fix_balllost.py [--input INPUT_FILE] [--output OUTPUT_FILE]
  (Defaults: input=xboing2.4-clang/sounds/balllost.au, output=assets/sounds/balllost.wav)
"""

import argparse
import logging
from pathlib import Path
import wave

logger = logging.getLogger("xboing.scripts.fix_balllost")


def fix_balllost_au(input_path: str, output_path: str) -> bool:
    """Fix and convert the balllost.au file that has a corrupted header.

    Args:
    ----
        input_path (str): Path to the balllost.au file
        output_path (str): Path for the output .wav file

    Returns:
    -------
        bool: True if successful, False otherwise

    """
    try:
        # Read the entire file
        with open(input_path, "rb") as f:
            data = f.read()

        # Verify it's an AU file by checking magic number
        if data[0:4] != b".snd":
            logger.warning(
                f"Warning: {input_path} does not appear to be a valid .au file"
            )
            return False

        # Skip header entirely - just use a fixed offset of 32 bytes
        # Most .au files in XBoing use either 32 or 40 byte headers
        header_size = 32  # Try with standard header size
        audio_data = data[header_size:]

        # Create a WAV file for the converted data
        with wave.open(output_path, "wb") as wav_file:
            wav_file: wave.Wave_write  # type: ignore
            # Set parameters - assuming 8-bit µ-law, mono, 8000Hz (standard for AU)
            wav_file.setparams((1, 2, 8000, 0, "NONE", "not compressed"))

            # Create lookup table for µ-law to linear conversion
            ulaw_table = [0] * 256
            for i in range(256):
                # Standard µ-law expansion algorithm
                u_val = i ^ 0xFF  # Invert (µ-law stores inverse)
                sign = 1 - 2 * ((u_val & 0x80) >> 7)  # 1 for positive, -1 for negative
                exponent = (u_val & 0x70) >> 4
                mantissa = u_val & 0x0F

                # Convert to linear PCM
                sample = (
                    mantissa if exponent == 0 else (0x10 | mantissa) << (exponent - 1)
                )

                # Apply sign
                linear = sign * sample

                # Store in table
                ulaw_table[i] = linear

            # Convert audio data using the table
            pcm_data = bytearray()
            for byte in audio_data:
                byte_val = byte if isinstance(byte, int) else ord(byte)

                # Get linear value from table
                value = ulaw_table[byte_val]

                # Apply volume boost (4x as in the original C code)
                value *= 4

                # Scale to 16-bit range and clamp
                value = int(value * 16)  # Scale to appropriate range
                if value > 32767:
                    value = 32767
                elif value < -32768:
                    value = -32768

                # Pack as 16-bit little-endian
                pcm_data.append(value & 0xFF)
                pcm_data.append((value >> 8) & 0xFF)

            wav_file.writeframes(pcm_data)

        logger.info(f"Successfully converted {input_path} to {output_path}")
        return True

    except Exception as e:
        logger.error(f"Error converting {input_path}: {e}")
        return False


def main() -> int:
    """Convert the balllost.au file with a corrupted header to .wav format.

    Returns
    -------
        int: Exit code (0 for success, 1 for error)

    """
    parser = argparse.ArgumentParser(
        description="Fix and convert the balllost.au file to .wav format."
    )
    parser.add_argument(
        "--input",
        "-i",
        default="xboing2.4-clang/sounds/balllost.au",
        help="Input .au file (default: xboing2.4-clang/sounds/balllost.au)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="assets/sounds/balllost.wav",
        help="Output .wav file (default: assets/sounds/balllost.wav)",
    )
    args = parser.parse_args()
    input_path = Path(args.input).resolve()
    output_path = Path(args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not input_path.exists():
        logger.error(f"Error: Could not find {input_path}")
        return 1
    if fix_balllost_au(str(input_path), str(output_path)):
        return 0

    return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
