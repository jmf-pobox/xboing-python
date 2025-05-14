# XBoing Python GUI Design & Architecture

## 1. Overview & Rationale

The XBoing Python GUI is designed around two core principles:
- **Faithful recreation of the original XBoing window layout and visual regions**
- **Modern, event-driven, component-based UI architecture for maintainability and testability**

This approach ensures the game looks and feels like the original, while making the codebase robust, extensible, and easy to test.

### Why Event-Driven, Component-Based UI?
- **Decoupling:** UI components react to events, not direct state changes, making them independent and reusable.
- **Testability:** Components can be tested in isolation by firing events.
- **Extensibility:** New UI features (overlays, menus, etc.) can be added as components without modifying core game logic.
- **Pygame Compatibility:** The design fits naturally with Pygame's event loop and rendering model.

---

## 2. Main Window Hierarchy & Layout

The game window is organized into a hierarchy of virtual windows, mimicking the original XBoing layout. The main window is subdivided into several regions, each with a specific purpose:

```
+------------------------------------------------------------+
|                      Main Game Window                      |
|   Top Bar View                                             |
|  +-------------------+---------------------------------+   |
|  |   Score Window    |         Level Window            |   |
|  +-------------------+---------------------------------+   |
|  |                                                     |   |
|  |                  Play Window                        |   |
|  |                                                     |   |
|  +-----------------------------------------------------+   |
|  |       Message               | Special | Time Window |   |
|  +-----------------------------------------------------+   |
|   Bottom Bar View                                          |
+------------------------------------------------------------+
```

### Updated Component Hierarchy

- **Main Window**: The root window, contains all other regions.
- **TopBarView**: A composite component that manages and draws all top bar UI elements:
  - **ScoreDisplay** (Score Window)
  - **LivesDisplayComponent** (Level Window)
  - **LevelDisplay** (Level Window)
- **MessageDisplay** (Message Window)
- **SpecialDisplay** (Special Window)
- **TimerDisplay** (Time Window)
- **ContentViewManager**: Manages the play window region, swapping between content views (GameView, InstructionsView, HighScoreView, etc.).
- **Play Window**: The main game area where blocks, paddle, and balls are rendered (via the current content view).

---

## 3. UI Component Structure & Event-Driven Architecture

Each UI region is implemented as a class/component that:
- Subscribes to relevant game events via the `EventBus` (from `src/engine/event_bus.py`)
- Maintains its own display state, updated in response to events
- Knows how to render itself in its assigned region (using `GameLayout` from `src/layout/`)

**Example Components:**
- `TopBarView` (owns and draws ScoreDisplay, LivesDisplayComponent, LevelDisplay, TimerDisplay, MessageDisplay, SpecialDisplay)
- `ScoreDisplay` (subscribes to `ScoreChangedEvent`)
- `LivesDisplayComponent` (subscribes to `LivesChangedEvent`)
- `LevelDisplay` (subscribes to `LevelChangedEvent`)
- `TimerDisplay` (subscribes to timer events)
- `MessageDisplay` (subscribes to `MessageChangedEvent`)
- `SpecialDisplay` (subscribes to special state events)
- `GameView`, `InstructionsView`, `GameOverView`, etc. (content views managed by UIManager)

### Event Flow
- Game logic fires events (using the `EventBus`).
- UI components update their internal state and redraw as needed in response to these events.
- The main loop simply calls `ui_manager.draw_all(window.surface)` after updating game state.

### UI Manager
- The `UIManager` (in `src/ui/ui_manager.py`) acts as the central manager for all UI components, content views, overlays, and bars.
- All content view management is now handled by `UIManager`.

### Integration with GameLayout
- UI components use `GameLayout` (from `src/layout/game_layout.py`) to determine their drawing regions.
- The window hierarchy remains unchanged; only the update/draw logic is refactored.

### 3.1. Class Diagram (Architecture Overview)

```
+-------------------+         +---------------------+
|   Game Logic      |         |    UIManager        |
+-------------------+         +---------------------+
| - event_bus       |<------->| - event_bus         |
| - game_state      |         | - views             |
|                   |         | - top_bar           |
| | fires events    |         | - bottom_bar        |
+-------------------+         | - draw_all()        |
         ^                    +---------------------+
         |                            ^
         |                            |
         |                            |
         |                    +---------------------+
         |                    |  UI Components      |
         |                    +---------------------+
         |                    | ScoreDisplay        |
         |                    | LivesDisplay        |
         |                    | LevelDisplay        |
         |                    | TimerDisplay        |
         |                    | MessageDisplay      |
         |                    | SpecialDisplay      |
         |                    | ...                 |
         |                    +---------------------+
         |                            ^
         |                            |
         |                    +---------------------+
         |                    |   Renderer(s)       |
         |                    +---------------------+
         |                            ^
         |                            |
         |                    +---------------------+
         |                    |   GameLayout        |
         |                    +---------------------+
         |
         |
+--------------------+         +---------------------+
| ControllerManager  |<------->|   Controller(s)     |
+--------------------+         +---------------------+
| - controllers      |         | GameController      |
| - active_controller|         | InstructionsCtrl    |
+--------------------+         | ...                 |
                               +---------------------+

+-------------------+
|    EventBus       |
+-------------------+
| subscribe()       |
| fire()            |
+-------------------+

+-------------------+
|   GameState       |
+-------------------+
| score, lives, ... |
| set_score(), ...  |
+-------------------+
```

### 3.2. Event Handling Sequence Diagram

```
Game Logic         EventBus         UI Component (e.g., ScoreDisplay)
    |                 |                        |
    | set_score()     |                        |
    |---------------->|                        |
    |  (fires         |                        |
    |  ScoreChanged)  |                        |
    |                 |                        |
    |                 |--fire(ScoreChanged)--> |
    |                 |                        | on_score_changed()
    |                 |                        | (updates state)
    |                 |                        |
    |                 |                        | draw(surface)
    |                 |                        | (renders new score)
    |                 |                        |
```

This sequence is similar for all UI components: game logic fires an event via the EventBus, the relevant UI component receives the event, updates its state, and redraws itself on the next frame.

---

## 4. Renderer Utilities and Packaging (2024 Refactor)

All stateless rendering utilities (e.g., for lives, digits, score, timer) are now located in the `src/renderers/` package. Each renderer is named `<Thing>Renderer` (e.g., `LivesRenderer`, `DigitRenderer`) and is responsible solely for drawing a specific visual element as a Pygame surface. UI components (in `src/ui/`) are stateful, subscribe to events, and use these renderers for their visual output.

This separation ensures clarity, reusability, and testability, and aligns with our MVC-inspired, event-driven architecture. When adding new renderers, place them in `src/renderers/` and follow the `<Thing>Renderer` naming convention. Update UI components to use these renderers for all visual output, keeping state and event logic in the component layer.

**Example:**
- `LivesRenderer` (in `src/renderers/lives_renderer.py`): Stateless, draws lives as ball images.
- `DigitRenderer` (in `src/renderers/digit_renderer.py`): Stateless, draws numbers/timers as digit sprites.
- `LivesDisplayComponent` (in `src/ui/lives_display.py`): Stateful, subscribes to events, uses `LivesRenderer` for drawing.

This approach replaces the previous pattern where some renderers were in `src/utils/` and clarifies the distinction between rendering logic and UI state/event management.

---

## 5. Content View Management

The play window region is managed by the `UIManager`, which is responsible for displaying one of several possible content views at any time. This enables the game to support multiple major UI screens, all occupying the same viewport:

- WelcomeView: Title, logo, and start prompt
- InstructionsView: Game instructions and rules
- DemoView: Autoplay demonstration with overlays
- LevelPreviewView: Shows the next level layout and info
- GameView: The main gameplay area (blocks, paddle, balls, etc.)
- GameKeysView: Shows game controls and key bindings
- HighScoresView: Displays high scores and player names

### Content View Responsibilities
- Each content view is a class/component that subscribes to relevant events (if needed), renders itself in the play window region, and handles its own state and logic.
- The `UIManager` manages which content view is active and handles view switching.

---

## 6. Asset Management
- All asset path helpers (in `src/utils/asset_paths.py`) resolve to the top-level `assets/` directory.
- No code references or loads assets from `src/assets/`.
- All images, sounds, and levels are loaded from the canonical `assets/` directory at the project root.

---

## 7. Layout Management
- All window/region layout logic is handled by `GameLayout`, `GameWindow`, and `Rect` in `src/layout/game_layout.py`.
- No layout logic remains in `src/utils/`.

---

## 8. Event System
- The event system (including `EventBus` and all event classes) is located in `src/engine/`.
- All UI and game logic components subscribe to and fire events using this system.

---

## 9. Controllers, UIManager, and Model Roles

### Overall Architecture

- **UIManager**: Owns and coordinates all UI components, content views, overlays, and manages which view is active. Provides a single `draw_all(surface)` method for rendering the UI.
- **ControllerManager**: (or as part of UIManager) Owns all controllers and switches the active controller based on the current view. Each controller handles input, updates, and transitions for its associated view.
- **Controllers**: Each major view has a corresponding controller (e.g., `GameController`, `InstructionsController`, `LevelCompleteController`). The active controller is responsible for:
  - Handling input/events
  - Updating the model (e.g., GameState)
  - Managing transitions (e.g., switching views)
- **GameState**: The central model for all gameplay-related state (score, lives, level, timer, specials, game over, etc.).
- **Other Models**: Specialized models (e.g., `LeaderBoard` for high scores) can be added as needed, either as properties of GameState or as separate classes.

### Data Flow
- Controllers read from and write to the model(s).
- Views render based on the model state and/or events.
- UIManager coordinates which view is active and handles all drawing.
- ControllerManager ensures the correct controller is active for the current view.

### Example Main Loop
```python
while running:
    events = pygame.event.get()
    controller_manager.active_controller.handle_events(events)
    controller_manager.active_controller.update(delta_time)
    ui_manager.draw_all(surface)
    window.update()
```

### Model Ownership Table

```
|-----------------|----------------------|-----------------------------|
| Data/Model      | Owner/Location       | Accessed by                 |
|-----------------|----------------------|-----------------------------|
| Game state      | `GameState`          | All controllers/views       |
| Level data      | `LevelManager`       | GameController, GameView    |
| High scores     | `LeaderBoard`        | HighScoresController/View   |
| Settings        | Settings model       | SettingsController/View     |
| Instructions    | Static or minimal    | InstructionsController/View |
|-----------------|----------------------|-----------------------------|
```
---

## 10. Event Routing: Unified Pygame Event System (2024 Redesign)

### Overview

- **All events** (user input, UI, game logic, custom game events) are routed through the Pygame event queue.
- **Custom events** are defined using `pygame.USEREVENT + n` and posted with `pygame.event.post`.
- **Handlers** (controllers, UI components, managers) implement a single `handle_events(events)` method and check for both built-in and custom event types.
- **No custom EventBus or protocol-based event handlers.**

### Example: Defining and Posting Custom Events

```python
MY_CUSTOM_EVENT = pygame.USEREVENT + 1
pygame.event.post(pygame.event.Event(MY_CUSTOM_EVENT, {"score": 100}))
```

### Example: Handling Events in a Controller or View

```python
def handle_events(self, events):
    for event in events:
        if event.type == pygame.KEYDOWN:
            ... # handle input
        elif event.type == MY_CUSTOM_EVENT:
            print("Custom event received! Score:", event.score)
```

### Updated Event Routing Table

| **Event**                | **Fired By (Class/Method)**         | **Handler(s) (Class/Method)**                | **Notes**                                                                 |
|--------------------------|-------------------------------------|----------------------------------------------|--------------------------------------------------------------------------|
| `BlockHitEvent`          | `GameController.update_balls_and_collisions` | `AudioManager.handle_events`, etc.           | Sound/UI update                                                          |
| `GameOverEvent`          | `GameState.lose_life`, `GameController.handle_life_loss` | `UIManager.handle_events`, etc.              | UI view switch, sound, etc.                                              |
| `BallLostEvent`          | `GameController.update_balls_and_collisions` | `GameController.handle_events`               | Life loss/game logic                                                     |
| `ScoreChangedEvent`      | `GameState.add_score`, `set_score`  | `ScoreDisplay.handle_events`                 | UI update                                                                |
| ...                      | ...                                 | ...                                         | ...                                                                      |
| **Pygame Events**        | User input, system events           | All controllers/views via `handle_events`    | Unified event loop                                                        |

### Handler Class/Method Key
- All handlers use `handle_events(events)` and check for both Pygame and custom event types.
- No protocol-based or function-based event subscriptions.

### Notes on Routing
- **All event subscriptions and handling are via the Pygame event queue.**
- **No custom EventBus or protocol-based handlers remain.**
- **UI components, controllers, and managers all use the same event loop.**

### Pygame Events
- **All events** (keyboard, mouse, custom) are handled in the same loop.

---

## 11. Migration Plan: Event System Simplification (2024)

### Step-by-Step Checklist

1. **Remove EventBus and EventHandlerProtocol from the codebase.**
2. **Update all event firing to use `pygame.event.post` with custom events.**
3. **Update all event handlers to use only `handle_events(events)` and check for both Pygame and custom event types.**
4. **Update UI components, controllers, and managers to subscribe to events via the Pygame event queue.**
5. **Update tests and documentation.**

### Migration Order (Class-by-Class)
- [ ] Remove EventBus and protocol-based code from all modules.
- [ ] Update GameController: move all event handling to `handle_events` and use Pygame custom events.
- [ ] Update LevelCompleteController, GameOverController, InstructionsController: same as above.
- [ ] Update UI components (ScoreDisplay, LivesDisplay, etc.): handle custom events in `handle_events`.
- [ ] Update AudioManager: handle sound-triggering events in `handle_events`.
- [ ] Update main loop: only use Pygame event queue.
- [ ] Update tests and documentation.

---

*This new design provides a single, unified event system for all game, UI, and input events, greatly simplifying the architecture and reducing confusion.*

*This document provides a unified overview of both the visual layout and the event-driven, component-based UI architecture of XBoing Python. It is intended to guide both current development and future extensions.* 