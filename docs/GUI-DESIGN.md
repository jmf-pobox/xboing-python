# XBoing Python GUI Design & Architecture

## 1. Overview

- **Faithful recreation** of the original XBoing window layout and visual regions.
- **Modern, event-driven, component-based UI architecture** for maintainability and testability.
- **All events** (game, UI, input) are routed through the Pygame event queue.

---

## 2. Main Window Hierarchy & Layout

- The main window is subdivided into regions: TopBarView, Play Window, BottomBarView.
- **TopBarView**: ScoreDisplay, LivesDisplayComponent, LevelDisplay, TimerDisplay, MessageDisplay, SpecialDisplay.
- **Play Window**: Main gameplay area (blocks, paddle, balls, etc.), managed by UIManager as a content view.
- **BottomBarView**: MessageDisplay, SpecialDisplay, TimerDisplay.

---

## 3. UI Component Structure & Event-Driven Architecture

- Each UI region is a class/component that:
  - Subscribes to relevant game events via the Pygame event queue.
  - Maintains its own display state, updated in response to events.
  - Renders itself in its assigned region (using `GameLayout`).
- **UIManager**: Central manager for all UI components, content views, overlays, and bars. Handles view switching and event routing.
- **All event handling** is via `handle_events(events)` methods, which process both Pygame and custom events.

---

## 4. Renderer Utilities

- Stateless rendering utilities (e.g., for lives, digits) are in `src/renderers/` as `<Thing>Renderer` classes.
- UI components in `src/ui/` are stateful, subscribe to events, and use these renderers for visual output.

---

## 5. Content View Management

- The play window region is managed by `UIManager`, which displays one of several content views:
  - GameView, InstructionsView, GameOverView, LevelCompleteView, etc.
- Each content view is a class/component that may subscribe to events, renders itself, and handles its own state/logic.
- `UIManager` manages which content view is active and handles view switching.

---

## 6. Asset Management

- All asset path helpers (in `src/utils/asset_paths.py`) resolve to the top-level `assets/` directory.
- All images, sounds, and levels are loaded from the canonical `assets/` directory at the project root.

---

## 7. Layout Management

- All window/region layout logic is handled by `GameLayout`, `GameWindow`, and `Rect` in `src/layout/game_layout.py`.

---

## 8. Event System

- **All events** (user input, UI, game logic, custom game events) are routed through the Pygame event queue.
- **Custom events** are defined using `pygame.USEREVENT` and posted with `pygame.event.post`.
- **GameState and other models** return a list of typed event instances representing state changes.
- **Controllers** (e.g., `GameController`) are responsible for posting these returned events to the Pygame event queue, using a helper method (e.g., `post_game_state_events`).
- **Handlers** (controllers, UI components, managers) implement `handle_events(events)` and check for both built-in and custom event types.

---

## 9. Controllers, UIManager, and Model Roles

- **UIManager**: Owns and coordinates all UI components, content views, overlays, and manages which view is active. Provides a single `draw_all(surface)` method for rendering the UI.
- **ControllerManager**: Owns all controllers and switches the active controller based on the current view.
- **Controllers**: Each major view has a corresponding controller (e.g., `GameController`, `InstructionsController`, `LevelCompleteController`, `GameOverController`). The active controller handles input, updates, and transitions for its associated view. **Controllers are now responsible for posting events returned by model methods to the Pygame event queue.**
- **GameState**: The central model for all gameplay-related state (score, lives, level, timer, specials, game over, etc.). **GameState methods return a list of event instances representing state changes, but do not post events directly.**
- **Other Models**: Specialized models (e.g., `LeaderBoard` for high scores) can be added as needed.

---

## 10. Dependency Injection & Factories

- **Dependency injection** is used via the `injector` library.
- The `XBoingModule` (in `src/di_module.py`) provides all bindings for controllers, views, UIManager, and other core objects.
- **UIFactory and ControllerFactory logic is now implemented as DI providers in `XBoingModule`, not as separate factory classes.**
- **AppCoordinator**: Synchronizes UIManager and ControllerManager, ensuring the correct controller is active for the current view.

---

## 11. Main Loop

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

## 12. Event Routing Table (Current)

All events are posted as `pygame.event.Event(pygame.USEREVENT, {"event": <EventInstance>})` and handled by checking `event.type == pygame.USEREVENT` and the event type in `handle_events(events)` methods. **Events representing model state changes are now returned by model methods and posted by controllers.**

| **Event**                    | **Fired By**                        | **Handled By**                        | **Notes**                                 |
|------------------------------|-------------------------------------|---------------------------------------|--------------------------------------------|
| ApplauseEvent                | GameController                      | AudioManager, UI                      | Applause sound, UI update                  |
| BallLostEvent                | GameController                      | GameController, AudioManager, UI      | Life loss/game logic, sound, UI            |
| BallShotEvent                | GameController                      | AudioManager, UI                      | Ball launch sound, UI update               |
| BlockHitEvent                | GameController                      | AudioManager, UI                      | Block sound, UI update                     |
| BombExplodedEvent            | GameController                      | AudioManager, UI                      | Bomb sound, UI update                      |
| BonusCollectedEvent          | (not shown, but likely GameController) | AudioManager, UI                   | Bonus sound, UI update                     |
| GameOverEvent                | GameController (from GameState)     | UIManager, AudioManager, UI           | Switch to game over view, sound            |
| LevelChangedEvent            | GameController (from GameState)     | LevelDisplay, UI                      | UI update                                  |
| LevelCompleteEvent           | GameController, LevelCompleteController | UIManager, AudioManager, UI        | Switch to level complete view, sound        |
| LivesChangedEvent            | GameController (from GameState)     | LivesDisplayComponent, UI             | UI update                                  |
| MessageChangedEvent          | GameController, GameState, etc.     | MessageDisplay, UI                    | UI update                                  |
| PaddleHitEvent               | GameController                      | AudioManager, UI                      | Paddle sound, UI update                    |
| PowerUpCollectedEvent        | GameController                      | AudioManager, UI                      | Power-up sound, UI update                  |
| ScoreChangedEvent            | GameController (from GameState)     | ScoreDisplay, UI                      | UI update                                  |
| Special*ChangedEvent         | GameController (from GameState)     | SpecialDisplay, UI                    | UI update                                  |
| TimerUpdatedEvent            | GameController (from GameState)     | TimerDisplay, UI                      | UI update                                  |
| UIButtonClickEvent           | LevelCompleteController, UI         | AudioManager, UI                      | Button click sound, UI update              |
| WallHitEvent                 | GameController                      | AudioManager, UI                      | Wall sound, UI update                      |
| **Pygame Events**            | User input, system events           | InputManager, controllers, UIManager  | Unified event loop                         |

All event subscriptions and handling are via the Pygame event queue. All UI components, controllers, and managers use the same event loop and check for their relevant events in `handle_events(events)`.

---

## 13. Construction-Time Code

- All construction and wiring of controllers, views, and managers is handled in `xboing.py` using DI providers in `XBoingModule`.
- No direct instantiation of UI or controller classes occurs outside these providers or DI modules.

---

## 14. Adding a New Event: End-to-End Guide

To add a new event to XBoing and handle it throughout the system, follow these steps:

### 1. Define the Event Class
Create a new class in `src/engine/events.py`:
```python
class MyCustomEvent:
    def __init__(self, value):
        self.value = value
```

### 2. Fire the Event
**If the event is a result of a model state change (e.g., in GameState):**
- Return the event instance from the model method (e.g., `return [MyCustomEvent(value)]`).
- In the controller, call the model method, then post the returned events using a helper:
```python
changes = game_state.some_method()
for event in changes:
    pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"event": event}))
```

**If the event is a pure controller/UI event:**
- Post the event directly from the controller or UI component as before.

### 3. Handle the Event
In any component, controller, or manager that should respond to the event, add logic to its `handle_events(events)` method:
```python
def handle_events(self, events):
    for event in events:
        if event.type == pygame.USEREVENT and isinstance(event.event, MyCustomEvent):
            # Handle the event (e.g., update state, UI, play sound)
            print(f"Received MyCustomEvent with value: {event.event.value}")
```

### 4. (Optional) Add to AudioManager or UI
If the event should trigger a sound, **add a `sound_effect` class attribute to the event class** (property-based mapping). AudioManager will automatically load and play the sound for any event with this attribute. Ensure the sound file exists.
If the event should update the UI, update the relevant UI component to handle the event as above.

### 5. Test the Event
Run the game and trigger the event to ensure it is fired and handled as expected.

### Sequence Diagram

```
Controller/Model         Pygame Event Queue         UI/Manager/Component
     |                          |                          |
     |  model_method()          |                          |
     |------------------------->|                          |
     |  [returns event]         |                          |
     |------------------------->|                          |
     |  post(event)             |                          |
     |------------------------->|                          |
     |                          |  [event in queue]        |
     |                          |------------------------->|
     |                          |                          | handle_events(events):
     |                          |                          |   if isinstance(event.event, MyCustomEvent):
     |                          |                          |     ...handle...
     |                          |                          |
```

This flow applies to all custom events in XBoing: define, return from model if appropriate, post from controller, and handle using the unified Pygame event system.

---

## 15. View-Controller Pair Pattern (Current Architecture)

XBoing now uses a design where each active view has a corresponding active controller, and only that controller receives events and updates. A persistent WindowController (formerly BaseController) always receives global/system events (quit, volume, etc.).

### Key Points
- **UIManager** manages the active view.
- **ControllerManager** manages the active controller, which is swapped in/out as views change.
- **WindowController** is always active and handles global events.
- **Per-View Controllers** (GameController, InstructionsController, etc.) only receive events when their view is active, and only take the dependencies they need.
- **Main loop** routes events to WindowController and the active controller for the current view.

### Example Main Loop
```python
while running:
    # Process Events
    events = pygame.event.get()
    input_manager.update(events)
    window_controller.handle_events(events)  # Always active
    controller_manager.active_controller.handle_events(events)  # Only active view's controller
    audio_manager.handle_events(events)
    ui_manager.handle_events(events)
    
    # Update for time and re-render
    controller_manager.active_controller.update(delta_time * 1000)
    layout.draw(window.surface)
    ui_manager.draw_all(window.surface)
    window.update()
```

### Benefits
- Each controller only takes the dependencies it needs.
- No unnecessary event handling by inactive controllers.
- Global/system events are always handled.
- Clean separation of concerns and easier testing.

This architecture improves maintainability, testability, and clarity of the event-driven design.
