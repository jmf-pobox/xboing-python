#!/usr/bin/env python3
"""
Special converter for the balllost.au file which has a corrupted header.
"""

import os
import wave


def fix_balllost_au(input_path, output_path):
    """
    Fix and convert the balllost.au file that has a corrupted header.

    Args:
        input_path (str): Path to the balllost.au file
        output_path (str): Path for the output .wav file

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Read the entire file
        with open(input_path, "rb") as f:
            data = f.read()

        # Verify it's an AU file by checking magic number
        if data[0:4] != b".snd":
            print(f"Warning: {input_path} does not appear to be a valid .au file")
            return False

        # Skip header entirely - just use a fixed offset of 32 bytes
        # Most .au files in XBoing use either 32 or 40 byte headers
        header_size = 32  # Try with standard header size
        audio_data = data[header_size:]

        # Create a WAV file for the converted data
        with wave.open(output_path, "wb") as wav_file:
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
                if exponent == 0:
                    sample = mantissa
                else:
                    sample = (0x10 | mantissa) << (exponent - 1)

                # Apply sign
                linear = sign * sample

                # Store in table
                ulaw_table[i] = linear

            # Convert audio data using the table
            pcm_data = bytearray()
            for byte in audio_data:
                if isinstance(byte, int):
                    byte_val = byte
                else:
                    byte_val = ord(byte)

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

        print(f"Successfully converted {input_path} to {output_path}")
        return True

    except Exception as e:
        print(f"Error converting {input_path}: {e}")
        return False


if __name__ == "__main__":
    # Set paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    source_dir = os.path.abspath(os.path.join(script_dir, "../../sounds"))
    target_dir = os.path.abspath(os.path.join(script_dir, "../src/assets/sounds"))

    # Make sure target directory exists
    os.makedirs(target_dir, exist_ok=True)

    # Convert balllost.au file
    input_file = os.path.join(source_dir, "balllost.au")
    output_file = os.path.join(target_dir, "balllost.wav")

    if os.path.exists(input_file):
        fix_balllost_au(input_file, output_file)
    else:
        print(f"Error: Could not find {input_file}")
