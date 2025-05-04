# AUDIO-DESIGN.md

## Status

- The event-driven AudioManager and event bus architecture are now fully integrated into the game.
- All sound triggers are now event-driven and decoupled from game logic.
- The old audio modules (`audio_player.py` and `audio.py`) have been removed as they are no longer used.
- All planned TODOs for the audio system refactor are complete.

---

## Overview

This document proposes a refactored, event-driven audio architecture for XBoing. The goal is to decouple game logic from audio playback, making the system more maintainable, testable, and extensible. The design leverages an event bus pattern, allowing game objects to fire events that are handled by an `AudioManager`. This same event system can be extended for GUI updates and other MVC-style decoupling.

---

## Key Design Goals

- **Decoupling:** Game objects do not directly play sounds; they fire events.
- **Testability:** The `AudioManager` and event system are easy to mock and unit test.
- **Extensibility:** The event system can be used for more than just audio (e.g., GUI updates).
- **Pygame Compatibility:** The design fits naturally with pygame's event loop and patterns.
- **OO Principles:** Follows SOLID, especially the Dependency Inversion Principle.

---

## Architecture

### 1. Event System

- **EventBus:**  
  A singleton or injectable class that allows objects to subscribe to and fire events.
- **Event Classes:**  
  Each event is a simple data class (e.g., `BallLostEvent`, `BlockHitEvent`, `ScoreChangedEvent`).

### 2. AudioManager

- **Responsibilities:**
  - Subscribes to relevant game events.
  - Maps events to sound effects.
  - Manages volume, mute/unmute, and sound resource loading.
- **API:**
  - `set_volume(float)`
  - `mute()`
  - `unmute()`
  - `is_muted()`
  - `cleanup()`
- **Testability:**  
  The event bus and sound playback can be mocked for unit tests.

### 3. Game Objects

- **Interaction:**  
  Game objects fire events (e.g., `event_bus.fire(BallLostEvent())`) instead of calling audio code directly.

### 4. Integration with Pygame

- The event bus can be polled or can use pygame's own event queue (with custom event types), but a pure-Python event bus is often simpler and more testable.
- The main game loop processes events and updates the game state/UI accordingly.

---

## Example Class Diagram

```
+----------------+         +-----------------+
|  Game Objects  |         |   AudioManager  |
+----------------+         +-----------------+
| - event_bus    |<------->| - event_bus     |
|                |         | - sounds        |
| fire(event)    |         | on_event(event) |
+----------------+         +-----------------+
         ^                          ^
         |                          |
         +--------------------------+
                    |
              +-------------+
              |  EventBus   |
              +-------------+
              | subscribe() |
              | fire()      |
              +-------------+
```

---

## Example Usage

### EventBus

```python
class EventBus:
    def __init__(self):
        self._subscribers = defaultdict(list)

    def subscribe(self, event_type, handler):
        self._subscribers[event_type].append(handler)

    def fire(self, event):
        for handler in self._subscribers[type(event)]:
            handler(event)
```

### AudioManager

```python
class AudioManager:
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.sounds = {...}
        self.volume = 1.0
        self.muted = False
        event_bus.subscribe(BallLostEvent, self.on_ball_lost)
        # ...subscribe to other events...

    def on_ball_lost(self, event):
        if not self.muted:
            self.sounds['ball_lost'].play()

    def set_volume(self, volume):
        self.volume = volume
        for sound in self.sounds.values():
            sound.set_volume(volume)

    def mute(self):
        self.muted = True
        for sound in self.sounds.values():
            sound.set_volume(0)

    def unmute(self):
        self.muted = False
        for sound in self.sounds.values():
            sound.set_volume(self.volume)
```

### Game Object Example

```python
class Ball:
    def __init__(self, event_bus):
        self.event_bus = event_bus

    def lose(self):
        self.event_bus.fire(BallLostEvent())
```

---

## Pygame Integration Notes

- The event bus can be polled or processed in the main loop, or handlers can be called immediately.
- For GUI updates, the same event bus can be used to fire events like `ScoreChangedEvent`, which the UI layer subscribes to.

---

## Benefits

- **Loose coupling:** Game logic, audio, and UI are independent.
- **Testability:** You can unit test each component in isolation.
- **Extensibility:** Add new event types and handlers without changing existing code.

---

## Next Steps

1. Implement a simple `EventBus` in `src/utils/event_bus.py`.
2. Refactor `AudioManager` to subscribe to events and manage sound playback.
3. Update game objects to fire events instead of playing sounds directly.
4. Extend the event system for GUI updates if desired.
5. Write unit tests for the event bus and audio manager.

---

## Integration Plan: Event-Driven AudioManager

### 1. Define Event Classes
For each sound trigger in the game (e.g., "boing", "click", "powerup", etc.), define a corresponding event class. Example event classes:
- BlockHitEvent
- UIButtonClickEvent
- PowerUpCollectedEvent
- GameOverEvent
- BallShotEvent
- BallLostEvent
- BombExplodedEvent
- ApplauseEvent
- BonusCollectedEvent
- PaddleHitEvent

These event classes can be simple dataclasses or empty classes, depending on whether you need to pass extra data.

### 2. Create EventBus and AudioManager
- Instantiate a single `EventBus` at the top of `main.py`.
- Define an `event_sound_map` that maps each event class to the appropriate sound name (e.g., `BlockHitEvent: "boing"`).
- Instantiate `AudioManager` with the event bus and mapping, and call `audio_manager.load_sounds_from_map()`.

### 3. Refactor Sound Triggers
- Replace each `play_sound("soundname")` call with `event_bus.fire(EventClass())`.
- For special cases (e.g., wall hit with reduced volume), use a custom event or extend the event class with parameters.

### 4. Remove Old Sound Logic
- Remove the `sounds` dictionary, `sound_files`, and the `play_sound` function from `main.py`.
- Remove all direct `pygame.mixer.Sound` usage from `main.py`.

### 5. Volume and Mute Controls
- Refactor volume and mute controls to call `audio_manager.set_volume()` and `audio_manager.mute()/unmute()`.

### 6. Example Event-to-Sound Mapping
```python
from engine.audio_manager import AudioManager
from utils.event_bus import EventBus

# Example event classes
event_sound_map = {
    BlockHitEvent: "boing",
    UIButtonClickEvent: "click",
    PowerUpCollectedEvent: "powerup",
    GameOverEvent: "game_over",
    BallShotEvent: "ballshot",
    BallLostEvent: "balllost",
    BombExplodedEvent: "bomb",
    ApplauseEvent: "applause",
    BonusCollectedEvent: "bonus",
    PaddleHitEvent: "paddle",
}

# Usage in main.py
event_bus = EventBus()
audio_manager = AudioManager(event_bus, event_sound_map=event_sound_map)
audio_manager.load_sounds_from_map()
```

### 7. Refactoring Example
- Old: `play_sound("boing")`
- New: `event_bus.fire(BlockHitEvent())`

---

This plan ensures all sound triggers are event-driven, decouples audio from game logic, and makes the system extensible and testable. The mapping and event classes can be easily extended as new sounds or events are added to the game. 