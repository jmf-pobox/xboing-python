import os
from typing import Any, Dict, Optional, Type

from utils.event_bus import EventBus

try:
    import pygame
except ImportError:
    pygame = None  # For testability

class AudioManager:
    """
    Event-driven audio manager that subscribes to game events and plays sounds.
    """
    def __init__(self, event_bus: EventBus, sound_dir: str = "assets/sounds", event_sound_map: Optional[Dict[Type[Any], str]] = None):
        """
        Args:
            event_bus: The EventBus to subscribe to events.
            sound_dir: Directory containing sound files.
            event_sound_map: Optional mapping from event type to sound name.
        """
        self.event_bus = event_bus
        self.sound_dir = sound_dir
        self.sounds: Dict[str, Any] = {}  # str -> pygame.mixer.Sound
        self.volume: float = 0.25
        self.muted: bool = False
        self.event_sound_map = event_sound_map or {}
        self._subscribed_events = set()

        # Subscribe to all events in the event_sound_map
        for event_type in self.event_sound_map:
            self.subscribe_event(event_type)

    def subscribe_event(self, event_type: Type[Any]) -> None:
        if event_type not in self._subscribed_events:
            self.event_bus.subscribe(event_type, self._handle_event)
            self._subscribed_events.add(event_type)

    def _handle_event(self, event: Any) -> None:
        event_type = type(event)
        sound_name = self.event_sound_map.get(event_type)
        if sound_name and not self.muted:
            self.play_sound(sound_name)

    def load_sound(self, name: str, filename: str) -> None:
        """Load a sound file by name."""
        if pygame is None:
            return
        path = os.path.join(self.sound_dir, filename)
        if os.path.exists(path):
            self.sounds[name] = pygame.mixer.Sound(path)
            self.sounds[name].set_volume(self.volume)

    def play_sound(self, name: str) -> None:
        """Play a loaded sound by name."""
        if pygame is None:
            return
        sound = self.sounds.get(name)
        if sound:
            sound.set_volume(0 if self.muted else self.volume)
            sound.play()

    def set_volume(self, volume: float) -> None:
        """Set the playback volume (0.0 to 1.0)."""
        self.volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(0 if self.muted else self.volume)

    def mute(self) -> None:
        """Mute all sounds."""
        self.muted = True
        for sound in self.sounds.values():
            sound.set_volume(0)

    def unmute(self) -> None:
        """Unmute all sounds."""
        self.muted = False
        for sound in self.sounds.values():
            sound.set_volume(self.volume)

    def is_muted(self) -> bool:
        """Return True if muted."""
        return self.muted

    def cleanup(self) -> None:
        """Clean up audio resources (optional)."""
        if pygame is not None:
            pygame.mixer.stop()

    def load_sounds_from_map(self) -> None:
        """Load all sounds referenced in the event_sound_map."""
        for sound_name in set(self.event_sound_map.values()):
            filename = f"{sound_name}.wav"
            self.load_sound(sound_name, filename)

    def get_volume(self) -> float:
        """Return the current playback volume (0.0 to 1.0)."""
        return self.volume 