"""
Sound management module for XBoing.

This module loads and manages the original XBoing sound files
that have been converted to WAV format.
"""

import pygame
import os

class SoundGenerator:
    """Sound manager for XBoing."""
    
    def __init__(self):
        """Initialize the sound generator."""
        pygame.mixer.init()
        
        # Sound directory
        self.sound_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                    "assets", "sounds")
        
        # Make sure the directory exists
        os.makedirs(self.sound_dir, exist_ok=True)
        
        # Print info about available sounds
        self._check_sounds()
        
    def _check_sounds(self):
        """Check which sounds are available and print information."""
        sound_files = ["boing.wav", "click.wav", "bomb.wav", "ballshot.wav", 
                      "balllost.wav", "applause.wav", "game_over.wav", "bonus.wav"]
        
        missing = []
        available = []
        
        for sound in sound_files:
            path = os.path.join(self.sound_dir, sound)
            if os.path.exists(path):
                available.append(sound)
            else:
                missing.append(sound)
                
        print(f"XBoing: Found {len(available)} sound files.")
        
        if missing:
            print(f"XBoing: Missing {len(missing)} sound files.")
            print("Run the converter tool to add original sound files:")
            print("  cd xboing-py && ./tools/simple_au_convert.py --input ../../sounds")
        
    def _get_sound_path(self, name):
        """Get the path to a sound file, with fallback."""
        primary = os.path.join(self.sound_dir, f"{name}.wav")
        
        if os.path.exists(primary):
            return primary
            
        # If the specific sound isn't available, try to find a substitute
        fallbacks = {
            "powerup": ["bonus.wav", "applause.wav", "whoosh.wav"],
            "click": ["key.wav", "stamp.wav", "weeek.wav"]
        }
        
        if name in fallbacks:
            for fallback in fallbacks[name]:
                fallback_path = os.path.join(self.sound_dir, fallback)
                if os.path.exists(fallback_path):
                    return fallback_path
        
        # Final fallback - if we have a boing sound, use it for everything
        boing_path = os.path.join(self.sound_dir, "boing.wav")
        if os.path.exists(boing_path):
            return boing_path
            
        # If we're here, we have no sounds at all - create a simple beep
        empty_path = os.path.join(self.sound_dir, f"{name}.wav")
        self._create_simple_beep(empty_path)
        return empty_path
    
    def _create_simple_beep(self, filepath, freq=440, duration_ms=200):
        """Create a simple WAV file with a single tone as fallback."""
        import wave
        import math
        import struct
        
        duration_s = duration_ms / 1000.0
        sample_rate = 22050
        num_samples = int(duration_s * sample_rate)
        
        with wave.open(filepath, 'w') as wav_file:
            # Set parameters
            wav_file.setparams((1, 2, sample_rate, num_samples, 'NONE', 'not compressed'))
            
            # Write sine wave data
            for i in range(num_samples):
                t = float(i) / sample_rate  # Time in seconds
                value = int(32767 * 0.5 * math.sin(2 * math.pi * freq * t))  # 50% volume
                packed_value = struct.pack('h', value)  # 'h' for 16-bit
                wav_file.writeframes(packed_value)
                
        print(f"Created fallback sound: {filepath}")
        
    def create_boing_sound(self):
        """Get the boing sound."""
        return pygame.mixer.Sound(self._get_sound_path("boing"))
    
    def create_click_sound(self):
        """Get the click sound."""
        return pygame.mixer.Sound(self._get_sound_path("click"))
    
    def create_powerup_sound(self):
        """Get the powerup sound."""
        return pygame.mixer.Sound(self._get_sound_path("powerup"))
    
    def create_game_over_sound(self):
        """Get the game over sound."""
        return pygame.mixer.Sound(self._get_sound_path("game_over"))