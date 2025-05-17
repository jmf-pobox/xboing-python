# AUDIO-DESIGN.md

## Overview

This document describes the event-driven audio architecture for XBoing. The goal is to decouple game logic from audio playback, making the system more maintainable, testable, and extensible. The design leverages the Pygame event queue, allowing game objects and controllers to post custom events that are handled by an `AudioManager`. Each event class that triggers a sound now declares its sound name as a `sound_effect` class attribute. This same event system is used for GUI updates and other MVC-style decoupling.

---

## Key Design Goals

- **Decoupling:** Game objects and controllers do not directly play sounds; they post events to the Pygame event queue.
- **Testability:** The `AudioManager` and event system are easy to mock and unit test.
- **Extensibility:** The event system is used for both audio and GUI updates.
- **Pygame Compatibility:** The design fits naturally with Pygame's event loop and patterns.
- **OO Principles:** Follows SOLID, especially the Dependency Inversion Principle.

---

## Architecture

### 1. Event System (Pygame Event Queue)

- **Custom Events:**
  - All custom game events (e.g., `BallLostEvent`, `BlockHitEvent`, etc.) inherit from `XBoingEvent`.
  - Events that trigger a sound define a `sound_effect` class attribute with the sound name (e.g., `sound_effect = "boing"`).
  - These are posted to the Pygame event queue as `pygame.event.Event(pygame.USEREVENT, {"event": XBoingEventInstance})`.
  - **Strict contract:** All handlers (including AudioManager) expect that any event with `type == pygame.USEREVENT` will have an `event` attribute containing an `XBoingEvent` instance. If not, an AttributeError will be raised (fail fast).
- **Event Posting:**
  - Controllers and game logic post events to the queue using `pygame.event.post`.
- **Event Handling:**
  - The main loop and all interested components (including `AudioManager`) process the event queue and handle relevant events by directly accessing `event.event`.

### 2. AudioManager

- **Responsibilities:**
  - Listens for custom events in the Pygame event queue.
  - For each event, checks for a `sound_effect` class attribute on the event instance.
  - If present, plays the corresponding sound.
  - Manages volume, mute/unmute, and sound resource loading.
- **API:**
  - `set_volume(float)`
  - `mute()`
  - `unmute()`
  - `is_muted()`
  - `cleanup()`
- **Testability:**
  - The event queue and sound playback can be mocked for unit tests.
- **Dependency Injection:**
  - `AudioManager` is constructed and injected via DI (see `di_module.py` and `xboing.py`).

### 3. Game Objects and Controllers

- **Interaction:**
  - Game objects and controllers post custom events to the Pygame event queue instead of calling audio code directly.
  - Example: `pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"event": BallLostEvent()}))`

### 4. Integration with Pygame

- The main game loop processes the Pygame event queue and passes all events to the `AudioManager` and other interested components.
- No custom EventBus is used; the Pygame event system is the single source of truth for all events.

---

## Example Class Diagram

```
+----------------+         +-----------------+
|  Game Objects  |         |   AudioManager  |
+----------------+         +-----------------+
|                |         | - sounds        |
| post(event)    |         | handle_events() |
+----------------+         +-----------------+
         |                          ^
         |                          |
         +--------------------------+
                    |
              +-------------------+
              | Pygame Event Queue|
              +-------------------+
```

---

## Example Usage

### Posting a Custom Event

```python
from engine.events import BallLostEvent
import pygame

# Post a custom event to the Pygame event queue
pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"event": BallLostEvent()}))
```

### Event Class with Sound Effect

```python
class BlockHitEvent(XBoingEvent):
    sound_effect = "boing"

class BallLostEvent(XBoingEvent):
    sound_effect = "balllost"
```

### AudioManager Event Handling

```python
class AudioManager:
    def handle_events(self, events: Sequence[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.USEREVENT:
                sound_name = getattr(event.event, "sound_effect", None)
                if sound_name and not self.muted:
                    self.play_sound(sound_name)
```

### Sound Loading

```python
def load_sounds_from_events(self) -> None:
    sound_names = set()
    for cls in XBoingEvent.__subclasses__():
        sound = getattr(cls, "sound_effect", None)
        if sound:
            sound_names.add(sound)
    for sound_name in sound_names:
        filename = f"{sound_name}.wav"
        self.load_sound(sound_name, filename)
```

### Main Loop Integration

```python
while running:
    events = pygame.event.get()
    input_manager.update(events)
    controller_manager.active_controller.handle_events(events)
    audio_manager.handle_events(events)
    ui_manager.handle_events(events)
    controller_manager.active_controller.update(delta_time * 1000)
    layout.draw(window.surface)
    ui_manager.draw_all(window.surface)
    window.update()
```

---

## Benefits

- **Loose coupling:** Game logic, audio, and UI are independent.
- **Testability:** You can unit test each component in isolation.
- **Extensibility:** Add new event types and handlers without changing existing code.
- **Unified event system:** All events (input, game, audio, UI) use the same Pygame event queue.

---

## Integration Plan: Event-Driven AudioManager with Pygame Events

### 1. Define Event Classes
For each sound trigger in the game (e.g., "boing", "click", "powerup", etc.), define a corresponding event class inheriting from `XBoingEvent` and set its `sound_effect` class attribute.

### 2. Create AudioManager and Load Sounds
- Instantiate `AudioManager`.
- Call `audio_manager.load_sounds_from_events()` to load all referenced sounds.
- Use dependency injection for setup (see `di_module.py` and `xboing.py`).

### 3. Refactor Sound Triggers
- Replace each direct sound trigger with posting a custom event to the Pygame event queue.
- For special cases (e.g., wall hit with reduced volume), use a custom event or extend the event class with parameters.

### 4. Remove Old Sound Logic
- Remove all direct `pygame.mixer.Sound` usage from game logic and controllers.

### 5. Volume and Mute Controls
- Use `audio_manager.set_volume()` and `audio_manager.mute()/unmute()` for volume control.

---

This design ensures all sound triggers are event-driven, decouples audio from game logic, and makes the system extensible and testable. The mapping and event classes can be easily extended as new sounds or events are added to the game. All event handling is unified through the Pygame event queue, and AudioManager is set up via dependency injection for maintainability. 