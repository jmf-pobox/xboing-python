"""Audio manager module for XBoing."""

import logging
import os
from typing import Dict, Sequence

import pygame

from xboing.engine.events import XBoingEvent


class AudioManager:
    """Event-driven audio manager that listens for game events and plays sounds.

    Only handles custom events posted as pygame.USEREVENT with an 'event' attribute (XBoingEvent instance).
    """

    def __init__(
        self,
        sound_dir: str = "assets/sounds",
    ):
        """Initialize the audio manager.

        Args:
        ----
            sound_dir: Directory containing sound files.

        """
        self.logger = logging.getLogger("xboing.AudioManager")
        self.sound_dir = sound_dir
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.volume: float = 0.75
        self.muted: bool = False

    def handle_events(self, events: Sequence[pygame.event.Event]) -> None:
        """Handle a sequence of events, playing sounds for mapped custom events.

        Args:
        ----
            events: A sequence of pygame events to process.

        """
        for event in events:
            if event.type == pygame.USEREVENT:
                event_data = getattr(event, "event", None)
                sound_name = (
                    getattr(event_data, "sound_effect", None) if event_data else None
                )
                if sound_name and not self.muted:
                    self.logger.debug(
                        f"Handling event: {type(event.event).__name__}, playing sound: {sound_name}"
                    )
                    self.play_sound(sound_name)

    def load_sound(self, name: str, filename: str) -> None:
        """Load a sound file by name."""
        if pygame is None:
            return
        path = os.path.join(self.sound_dir, filename)
        if os.path.exists(path):
            self.sounds[name] = pygame.mixer.Sound(path)
            self.sounds[name].set_volume(self.volume)
            self.logger.debug(f"Loaded sound: {name} from {path}")
        else:
            self.logger.warning(f"Sound file not found: {path}")

    def play_sound(self, name: str) -> None:
        """Play a loaded sound by name."""
        if pygame is None:
            return
        sound = self.sounds.get(name)
        if sound:
            sound.set_volume(0 if self.muted else self.volume)
            sound.play()
            self.logger.debug(f"Played sound: {name}")
        else:
            self.logger.warning(f"Sound not loaded: {name}")

    def set_volume(self, volume: float) -> None:
        """Set the playback volume (0.0 to 1.0)."""
        self.volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(0 if self.muted else self.volume)
        self.logger.info(f"Volume set to: {self.volume}")

    def mute(self) -> None:
        """Mute all sounds."""
        self.muted = True
        for sound in self.sounds.values():
            sound.set_volume(0)
        self.logger.info("Audio muted")

    def unmute(self) -> None:
        """Unmute all sounds."""
        self.muted = False
        for sound in self.sounds.values():
            sound.set_volume(self.volume)
        self.logger.info("Audio unmuted")

    def is_muted(self) -> bool:
        """Return True if muted."""
        return self.muted

    def cleanup(self) -> None:
        """Clean up audio resources (optional)."""
        if pygame is not None:
            pygame.mixer.stop()
        self.logger.info("AudioManager cleanup called")

    def load_sounds_from_events(self) -> None:
        """Load all sounds referenced by XBoingEvent subclasses."""
        sound_names = set()
        for cls in XBoingEvent.__subclasses__():
            sound = getattr(cls, "sound_effect", None)
            if sound:
                sound_names.add(sound)
        for sound_name in sound_names:
            filename = f"{sound_name}.wav"
            self.load_sound(sound_name, filename)

    def get_volume(self) -> float:
        """Return the current playback volume (0.0 to 1.0)."""
        return self.volume
