import logging
import os
from typing import Dict, Optional, Sequence, Type

import pygame

from engine.events import XBoingEvent


class AudioManager:
    """
    Event-driven audio manager that listens for game events and plays sounds.
    """

    def __init__(
        self,
        sound_dir: str = "assets/sounds",
        event_sound_map: Optional[Dict[Type[XBoingEvent], str]] = None,
    ):
        """
        Args:
            sound_dir: Directory containing sound files.
            event_sound_map: Optional mapping from event type to sound name.
        """
        self.logger = logging.getLogger("xboing.AudioManager")
        self.sound_dir = sound_dir
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.volume: float = 0.05
        self.muted: bool = False
        self.event_sound_map: Dict[Type[XBoingEvent], str] = event_sound_map or {}

    def handle_events(self, events: Sequence[pygame.event.Event]) -> None:
        """
        Handle a sequence of events, playing sounds for mapped custom events.

        Args:
            events: A sequence of pygame events to process.
        """
        for event in events:
            # Check if this is a pygame event with our custom event attribute
            if hasattr(event, "event") and event.type == pygame.USEREVENT:
                event_type = type(event.event)
                sound_name = self.event_sound_map.get(event_type)
                if sound_name and not self.muted:
                    self.logger.debug(
                        f"Handling event: {event_type.__name__}, playing sound: {sound_name}"
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

    def load_sounds_from_map(self) -> None:
        """Load all sounds referenced in the event_sound_map."""
        for sound_name in set(self.event_sound_map.values()):
            filename = f"{sound_name}.wav"
            self.load_sound(sound_name, filename)

    def get_volume(self) -> float:
        """Return the current playback volume (0.0 to 1.0)."""
        return self.volume
