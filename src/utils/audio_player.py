"""
Direct audio player for XBoing.

This module provides a simple, thread-safe audio player for .wav files used in the game.

Usage example:
    from utils.audio_player import DirectAudioPlayer
    player = DirectAudioPlayer()
    player.play_sound("boing")

Testing:
    - Use dependency injection for sounds_dir to point to a test directory.
    - Mock pygame.mixer.Sound for unit tests if needed.

Thread safety:
    - The sound cache is protected by a threading.Lock for safe use in multi-threaded contexts.
"""

import logging
import os
import threading
from typing import Dict, Optional

import pygame

logger = logging.getLogger("xboing.audio_player")


class DirectAudioPlayer:
    """
    Simple, thread-safe audio player for .wav files in XBoing.

    Args:
        sounds_dir (str): Directory containing .wav sound files. Defaults to 'assets/sounds'.

    Example:
        player = DirectAudioPlayer()
        player.play_sound("boing")

    Thread safety:
        All cache accesses are protected by a threading.Lock.
    """

    def __init__(self, sounds_dir: str = "assets/sounds"):
        """
        Initialize the audio player and pygame mixer.

        Args:
            sounds_dir (str): Directory containing .wav sound files.
        """
        pygame.mixer.init(frequency=22050, size=-16, channels=1)
        self.sounds_dir = sounds_dir
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self._lock = threading.Lock()

    def get_sound(self, name: str, volume: float = 0.7) -> pygame.mixer.Sound:
        """
        Get a sound by name, loading it if necessary.

        Args:
            name (str): Sound name (without extension)
            volume (float): Volume level from 0.0 to 1.0

        Returns:
            pygame.mixer.Sound: The sound object

        Raises:
            FileNotFoundError: If the sound file does not exist.
            Exception: If loading the sound fails for another reason.
        """
        cache_key = f"{name}_{volume}"
        with self._lock:
            if cache_key in self.sounds:
                return self.sounds[cache_key]

        sound_path = os.path.join(self.sounds_dir, f"{name}.wav")
        if not os.path.exists(sound_path):
            logger.error(f"Sound file not found: {sound_path}")
            raise FileNotFoundError(f"Sound file not found: {sound_path}")
        try:
            sound = pygame.mixer.Sound(sound_path)
            sound.set_volume(volume)
            with self._lock:
                self.sounds[cache_key] = sound
            logger.debug(f"Loaded sound: {sound_path} at volume {volume}")
            return sound
        except Exception as e:
            logger.error(f"Failed to load sound {sound_path}: {e}")
            raise

    def play_sound(
        self, name: str, volume: float = 0.7
    ) -> Optional[pygame.mixer.Channel]:
        """
        Play a sound by name.

        Args:
            name (str): Sound name (without extension)
            volume (float): Volume level from 0.0 to 1.0

        Returns:
            pygame.mixer.Channel: The channel playing the sound, or None if failed
        """
        try:
            sound = self.get_sound(name, volume)
            return sound.play()
        except Exception as e:
            logger.warning(f"Could not play sound '{name}': {e}")
            return None

    def clear_cache(self) -> None:
        """
        Clear the cached sounds. Useful for memory management or reloading sounds.
        Thread-safe.
        """
        with self._lock:
            self.sounds.clear()
        logger.info("AudioPlayer sound cache cleared.")
