#!/usr/bin/env python3
"""
Convert the paddle.au sound file to WAV format
"""

import os
import wave
import math

def convert_au_to_wav(input_file, output_file):
    """
    Convert an .au file to WAV format using the proper conversion technique.
    
    Args:
        input_file (str): Path to the .au file
        output_file (str): Path for the output .wav file
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Read the AU file and parse header
        with open(input_file, 'rb') as f:
            # Check magic number (.snd)
            magic = f.read(4)
            if magic != b'.snd':
                print(f"Warning: {input_file} doesn't have a valid AU header")
                
            # Read header values
            data_offset = int.from_bytes(f.read(4), byteorder='big')
            data_size = int.from_bytes(f.read(4), byteorder='big')
            encoding = int.from_bytes(f.read(4), byteorder='big')
            sample_rate = int.from_bytes(f.read(4), byteorder='big')
            channels = int.from_bytes(f.read(4), byteorder='big')
            
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
            f.seek(data_offset)
            
            # Read the audio data (up to data_size bytes if specified)
            if data_size > 0 and data_size < 1000000:  # Sanity check
                audio_data = f.read(data_size)
            else:
                # Read all remaining data if size not specified or invalid
                audio_data = f.read()
        
        # Create a WAV file with the converted data
        with wave.open(output_file, 'wb') as wav_file:
            # Set parameters from the AU file (converting to 16-bit PCM)
            channels = max(1, channels)  # Ensure at least 1 channel
            wav_file.setparams((channels, 2, sample_rate, 0, 'NONE', 'not compressed'))
            
            # Create lookup table for μ-law to linear conversion
            ulaw_table = [0] * 256
            for i in range(256):
                # Standard μ-law expansion algorithm
                u_val = i ^ 0xFF  # Invert (μ-law stores inverse)
                sign = 1 - 2 * ((u_val & 0x80) >> 7)  # 1 for positive, -1 for negative
                exponent = ((u_val & 0x70) >> 4)
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
            
        print(f"Successfully converted {input_file} to {output_file}")
        return True
        
    except Exception as e:
        print(f"Error converting {input_file}: {e}")
        return False

if __name__ == "__main__":
    # Set paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    source_dir = os.path.abspath(os.path.join(script_dir, '../../sounds'))
    target_dir = os.path.abspath(os.path.join(script_dir, '../src/assets/sounds'))
    
    # Make sure target directory exists
    os.makedirs(target_dir, exist_ok=True)
    
    # Convert paddle.au file
    input_file = os.path.join(source_dir, 'paddle.au')
    output_file = os.path.join(target_dir, 'paddle.wav')
    
    if os.path.exists(input_file):
        convert_au_to_wav(input_file, output_file)
    else:
        print(f"Error: Could not find {input_file}")