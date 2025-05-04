"""
Audio playback abstraction over SDL2/pygame.

This module provides sound loading and playback capabilities,
abstracting the underlying pygame mixer implementation.
"""

import os

import pygame


class AudioManager:
    """Manages sound loading and playback."""

    def __init__(self, sound_dir="assets/sounds"):
        """
        Initialize the audio manager.

        Args:
            sound_dir (str): Directory containing sound files
        """
        # Initialize pygame mixer
        pygame.mixer.init()

        self.sound_dir = sound_dir
        self.sounds = {}
        self.max_volume = 1.0
        self.enabled = True

    def load_sound(self, name, filename):
        """
        Load a sound file.

        Args:
            name (str): Reference name for the sound
            filename (str): Sound file path relative to sound_dir
        """
        if not self.enabled:
            return

        try:
            path = os.path.join(self.sound_dir, filename)
            sound = pygame.mixer.Sound(path)
            self.sounds[name] = sound
        except pygame.error as e:
            print(f"Error loading sound {filename}: {e}")

    def load_sounds(self):
        """Auto-load all sound files from the sound directory."""
        if not self.enabled or not os.path.exists(self.sound_dir):
            return

        for filename in os.listdir(self.sound_dir):
            if filename.endswith((".wav", ".ogg", ".mp3")):
                name = os.path.splitext(filename)[0]
                self.load_sound(name, filename)

    def play(self, name, volume=1.0, loop=0):
        """
        Play a sound.

        Args:
            name (str): Sound name
            volume (float): Volume level from 0.0 to 1.0
            loop (int): Number of times to loop (-1 for infinite)

        Returns:
            pygame.mixer.Channel: The channel playing the sound, or None if failed
        """
        if not self.enabled or name not in self.sounds:
            return None

        # Apply volume scaling
        adjusted_volume = volume * self.max_volume
        self.sounds[name].set_volume(min(1.0, adjusted_volume))

        # Play the sound
        return self.sounds[name].play(loop)

    def stop_sound(self, name):
        """Stop a specific sound."""
        if not self.enabled or name not in self.sounds:
            return

        self.sounds[name].stop()

    def stop_all(self):
        """Stop all sounds."""
        if not self.enabled:
            return

        pygame.mixer.stop()

    def set_max_volume(self, volume):
        """Set the maximum volume level (0.0 to 1.0)."""
        self.max_volume = max(0.0, min(1.0, volume))

    def toggle_audio(self):
        """Toggle audio on/off."""
        self.enabled = not self.enabled
        if not self.enabled:
            self.stop_all()

    def is_audio_enabled(self):
        """Check if audio is enabled."""
        return self.enabled

    def cleanup(self):
        """Clean up audio resources."""
        pygame.mixer.quit()
