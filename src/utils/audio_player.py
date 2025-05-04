"""
Direct audio player for XBoing.

This module provides direct playback of audio files for the game,
supporting both .au and .wav file formats.
"""

import io
import math
import os
import struct
import wave

import pygame


class DirectAudioPlayer:
    """Audio player that can play both .au and .wav files directly."""

    def __init__(self):
        """Initialize the audio player."""
        # Initialize pygame mixer
        pygame.mixer.init(frequency=22050, size=-16, channels=1)

        self.xboing_path = self._find_xboing_root()
        self.sounds = {}  # Cache for loaded sounds

    def _find_xboing_root(self):
        """Find the root xboing directory."""
        current_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )

        # Look for sounds directory which indicates the xboing root
        parent_dir = os.path.dirname(current_dir)
        if os.path.exists(os.path.join(parent_dir, "sounds")):
            return parent_dir

        # If not found, use the current project directory
        return current_dir

    def _load_file(self, filename, volume=0.7):
        """
        Load an audio file (.au or .wav) and return a pygame.mixer.Sound.

        Args:
            filename (str): Filename (without extension)
            volume (float): Volume level from 0.0 to 1.0

        Returns:
            pygame.mixer.Sound: The loaded sound, or None if failed
        """
        print(f"Loading sound: {filename}")

        # First try to find the WAV version
        paths_to_try = [
            # Look in xboing-py/src/assets/sounds
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "assets",
                "sounds",
                f"{filename}.wav",
            ),
            # Look in project assets
            os.path.join(self.xboing_path, "assets", "sounds", f"{filename}.wav"),
            # Look in original xboing sounds
            os.path.join(self.xboing_path, "sounds", f"{filename}.au"),
        ]

        # Try each path
        for path in paths_to_try:
            print(f"  Trying path: {path}")
            if os.path.exists(path):
                print(f"  File exists: {path}")
                try:
                    if path.endswith(".wav"):
                        # Load WAV file directly
                        print(f"  Loading WAV file: {path}")
                        sound = pygame.mixer.Sound(path)
                        sound.set_volume(volume)
                        print(f"  Successfully loaded WAV: {path}")
                        return sound
                    elif path.endswith(".au"):
                        # Convert .au file to WAV in memory
                        print(f"  Converting AU file: {path}")
                        wav_data = self._convert_au_to_wav_data(path)
                        if wav_data:
                            print("  Converting successful, creating sound object")
                            sound = pygame.mixer.Sound(io.BytesIO(wav_data))
                            sound.set_volume(volume)
                            print(f"  Successfully loaded converted AU: {path}")
                            return sound
                        else:
                            print(f"  Conversion failed for: {path}")
                except Exception as e:
                    print(f"  Failed to load {path}: {e}")
                    continue
            else:
                print(f"  File does not exist: {path}")

        # If we get here, no sound could be loaded - return a simple beep
        print(f"  No sound file found for {filename}, creating beep")
        return self._create_beep(volume)

    def _convert_au_to_wav_data(self, au_path):
        """
        Convert an .au file to WAV format in memory with appropriate conversion
        to match the original XBoing sound characteristics.

        Args:
            au_path (str): Path to the .au file

        Returns:
            bytes: WAV data as bytes, or None if conversion failed
        """
        try:
            # Read the .au file
            with open(au_path, "rb") as f:
                # Check the magic number (.snd)
                magic = f.read(4)
                if magic != b".snd":
                    print(f"Warning: {au_path} does not appear to be a valid .au file")

                # Read the header
                data_offset = int.from_bytes(f.read(4), byteorder="big")
                data_size = int.from_bytes(f.read(4), byteorder="big")
                encoding = int.from_bytes(f.read(4), byteorder="big")
                sample_rate = int.from_bytes(f.read(4), byteorder="big")
                channels = int.from_bytes(f.read(4), byteorder="big")

                # Default to 8kHz if not specified
                if sample_rate == 0:
                    sample_rate = 8000

                # Default to mono if not specified
                if channels == 0:
                    channels = 1

                # Seek to data section
                f.seek(data_offset)

                # Read the audio data
                au_data = f.read(data_size)

            # Create a WAV file in memory
            wav_io = io.BytesIO()
            with wave.open(wav_io, "wb") as wav_file:
                # Set parameters for 16-bit PCM, mono, original sample rate
                wav_file.setparams(
                    (channels, 2, sample_rate, 0, "NONE", "not compressed")
                )

                # For u-law encoding (most common in .au files)
                if encoding == 1:  # 8-bit ISDN u-law
                    # Basic u-law to linear table
                    # This is a simplified version based on standard μ-law expansion
                    ulaw_table = [0] * 256
                    for i in range(256):
                        # Standard μ-law expansion algorithm
                        u_val = i ^ 0xFF  # Invert (μ-law stores inverse)
                        sign = (u_val & 0x80) >> 7
                        exponent = (u_val & 0x70) >> 4
                        mantissa = u_val & 0x0F

                        # Compute linear value with bias of 33
                        linear = mantissa << (exponent + 3)
                        linear += (1 << (exponent + 3)) - (1 << 3)

                        # Set appropriate sign
                        if sign == 0:
                            linear = -linear

                        # Store in table
                        ulaw_table[i] = linear

                    # Convert audio data using the table
                    pcm_data = bytearray()
                    for byte in au_data:
                        # Get linear value from table
                        value = ulaw_table[byte]

                        # Apply volume boost (4x as in the original C code)
                        value *= 4

                        # Clamp to 16-bit range
                        if value > 32767:
                            value = 32767
                        elif value < -32768:
                            value = -32768

                        # Pack as 16-bit little-endian
                        pcm_data.append(value & 0xFF)
                        pcm_data.append((value >> 8) & 0xFF)

                    wav_file.writeframes(pcm_data)
                else:
                    # For other encodings, just convert each byte to a 16-bit sample
                    # This is a fallback that won't sound right but avoids errors
                    pcm_data = bytearray()
                    for byte in au_data:
                        # Convert 8-bit unsigned to 16-bit signed
                        value = (byte - 128) * 4 * 256 // 128

                        # Clamp to 16-bit range
                        if value > 32767:
                            value = 32767
                        elif value < -32768:
                            value = -32768

                        # Pack as 16-bit little-endian
                        pcm_data.append(value & 0xFF)
                        pcm_data.append((value >> 8) & 0xFF)

                    wav_file.writeframes(pcm_data)

            # Get the WAV data
            wav_io.seek(0)
            return wav_io.read()

        except Exception as e:
            print(f"Error converting {au_path}: {e}")
            return None

    def _create_beep(self, volume=0.5, freq=440, duration_ms=200):
        """
        Create a simple beep sound as fallback.

        Args:
            volume (float): Volume level from 0.0 to 1.0
            freq (int): Frequency in Hz
            duration_ms (int): Duration in milliseconds

        Returns:
            pygame.mixer.Sound: The beep sound
        """
        duration_s = duration_ms / 1000.0
        sample_rate = 22050
        num_samples = int(duration_s * sample_rate)

        # Create WAV file in memory
        wav_io = io.BytesIO()
        with wave.open(wav_io, "wb") as wav_file:
            wav_file.setparams(
                (1, 2, sample_rate, num_samples, "NONE", "not compressed")
            )

            # Write sine wave data
            for i in range(num_samples):
                t = float(i) / sample_rate
                value = int(32767 * volume * 0.5 * math.sin(2 * 3.14159 * freq * t))
                packed_value = struct.pack("h", value)
                wav_file.writeframes(packed_value)

        # Convert to pygame sound
        wav_io.seek(0)
        return pygame.mixer.Sound(wav_io)

    def get_sound(self, name, volume=0.7):
        """
        Get a sound by name.

        Args:
            name (str): Sound name (without extension)
            volume (float): Volume level from 0.0 to 1.0

        Returns:
            pygame.mixer.Sound: The sound object
        """
        # Check if sound is already cached
        cache_key = f"{name}_{volume}"
        if cache_key in self.sounds:
            return self.sounds[cache_key]

        # Load the sound
        sound = self._load_file(name, volume)

        # Cache for later use
        self.sounds[cache_key] = sound
        return sound

    def play_sound(self, name, volume=0.7):
        """
        Play a sound by name.

        Args:
            name (str): Sound name (without extension)
            volume (float): Volume level from 0.0 to 1.0

        Returns:
            pygame.mixer.Channel: The channel playing the sound, or None if failed
        """
        sound = self.get_sound(name, volume)
        if sound:
            return sound.play()
        return None
