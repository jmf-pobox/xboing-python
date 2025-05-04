#!/usr/bin/env python3
"""
Simple AU to WAV converter

This script converts .au audio files to .wav format
without requiring any external dependencies.
"""

import argparse
import os
import sys
import wave


def convert_au_to_wav(input_file, output_file=None):
    """
    Convert an .au file to .wav format using a simple approach.

    Args:
        input_file (str): Path to the .au file
        output_file (str): Path for the output .wav file (optional)

    Returns:
        str: Path to the output file or None if failed
    """
    if output_file is None:
        # Create output filename by replacing .au with .wav
        output_file = os.path.splitext(input_file)[0] + ".wav"

    try:
        # Read the AU file and parse the header
        with open(input_file, "rb") as au_file:
            # Check magic number (.snd)
            magic = au_file.read(4)
            if magic != b".snd":
                print(f"Warning: {input_file} doesn't have a valid AU header")

            # Read header values
            data_offset = int.from_bytes(au_file.read(4), byteorder="big")
            data_size = int.from_bytes(au_file.read(4), byteorder="big")
            encoding = int.from_bytes(au_file.read(4), byteorder="big")
            sample_rate = int.from_bytes(au_file.read(4), byteorder="big")
            channels = int.from_bytes(au_file.read(4), byteorder="big")

            # Print file info for debugging
            print(f"AU File: {input_file}")
            print(f"  Data offset: {data_offset} bytes")
            print(f"  Data size: {data_size} bytes")
            print(f"  Encoding: {encoding} (1=μ-law)")
            print(f"  Sample rate: {sample_rate} Hz")
            print(f"  Channels: {channels}")

            # Default to 8kHz if not specified
            if sample_rate == 0:
                sample_rate = 8000
                print(f"  Using default sample rate: {sample_rate} Hz")

            # Seek to data section
            au_file.seek(data_offset)

            # Read the audio data (up to data_size bytes if specified)
            if data_size > 0:
                audio_data = au_file.read(data_size)
            else:
                # Read all remaining data if size not specified
                audio_data = au_file.read()

        # Enhanced WAV file creation with proper u-law conversion and volume boost
        with wave.open(output_file, "wb") as wav_file:
            # Set parameters from the AU file (converting to 16-bit PCM)
            channels = max(1, channels)  # Ensure at least 1 channel
            wav_file.setparams((channels, 2, sample_rate, 0, "NONE", "not compressed"))

            # Pre-compute u-law to linear conversion table
            # This is a standard algorithm used in telecommunications
            ulaw_table = [0] * 256
            for i in range(256):
                # Standard μ-law expansion algorithm
                u_val = i ^ 0xFF  # Invert (μ-law stores inverse)
                sign = 1 - 2 * ((u_val & 0x80) >> 7)  # 1 for positive, -1 for negative
                exponent = (u_val & 0x70) >> 4
                mantissa = u_val & 0x0F

                # Convert to linear PCM
                if exponent == 0:
                    sample = mantissa
                else:
                    sample = (0x10 | mantissa) << (exponent - 1)

                # Apply sign and bias adjustment
                linear = sign * sample

                # Store in table
                ulaw_table[i] = linear

            # Convert audio data using the table
            pcm_data = bytearray()
            for byte in audio_data:
                if isinstance(byte, str):  # Handle Python 2/3 compatibility
                    byte = ord(byte)

                # Get linear value from table
                value = ulaw_table[byte]

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

        print(f"Converted {input_file} to {output_file}")
        return output_file

    except Exception as e:
        print(f"Error converting {input_file}: {e}")
        return None


def batch_convert(source_dir, dest_dir, sound_list=None):
    """
    Convert all .au files in a directory to .wav format.

    Args:
        source_dir (str): Directory containing .au files
        dest_dir (str): Directory to save .wav files
        sound_list (list): Optional list of specific sounds to convert

    Returns:
        int: Number of successfully converted files
    """
    # Create output directory if it doesn't exist
    os.makedirs(dest_dir, exist_ok=True)

    # List of essential game sounds
    essential_sounds = [
        "boing",  # Ball collision
        "click",  # UI actions
        "bomb",  # Explosion
        "applause",  # Level complete
        "ballshot",  # Ball launched
        "balllost",  # Ball lost
        "bonus",  # Bonus collected
        "game_over",  # Game over
    ]

    # Filter for specific sounds if provided
    if sound_list:
        essential_sounds = sound_list

    # Check all .au files in the directory
    success_count = 0

    for sound_name in essential_sounds:
        au_path = os.path.join(source_dir, f"{sound_name}.au")
        if os.path.exists(au_path):
            wav_path = os.path.join(dest_dir, f"{sound_name}.wav")
            if convert_au_to_wav(au_path, wav_path):
                success_count += 1
        else:
            print(f"Warning: Could not find {sound_name}.au")

    return success_count


def main():
    parser = argparse.ArgumentParser(
        description="Convert .au audio files to .wav format"
    )
    parser.add_argument(
        "--input",
        "-i",
        default="../sounds",
        help="Input directory containing .au files",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="../src/assets/sounds",
        help="Output directory for .wav files",
    )
    parser.add_argument(
        "--sounds",
        "-s",
        nargs="+",
        help="Specific sound names to convert (without extension)",
    )

    args = parser.parse_args()

    # Resolve paths relative to script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.abspath(os.path.join(script_dir, args.input))
    output_path = os.path.abspath(os.path.join(script_dir, args.output))

    if not os.path.exists(input_path):
        print(f"Error: Input path {input_path} does not exist")
        return 1

    if os.path.isdir(input_path):
        # Convert files in directory
        count = batch_convert(input_path, output_path, args.sounds)
        print(f"Successfully converted {count} files")
    elif input_path.lower().endswith(".au"):
        # Convert single file
        output_file = os.path.join(
            output_path, os.path.splitext(os.path.basename(input_path))[0] + ".wav"
        )
        if convert_au_to_wav(input_path, output_file):
            print(f"Successfully converted {os.path.basename(input_path)}")
        else:
            print(f"Failed to convert {os.path.basename(input_path)}")
    else:
        print(f"Error: {input_path} is not an .au file or directory")

    return 0


if __name__ == "__main__":
    sys.exit(main())
