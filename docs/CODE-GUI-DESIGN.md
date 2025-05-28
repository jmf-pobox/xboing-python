# XBoing Python GUI Design & Architecture

## 1. Architectural Principles

- **Faithful recreation** of the original XBoing layout and feel.
- **Modern, event-driven, component-based UI** for maintainability and testability.
- **Polymorphic, DRY game object design** using a unified shape hierarchy.
- **All events** (game, UI, input) are routed through the Pygame event queue.
- **Stateless, modular renderer pattern** for all UI content views, ensuring separation of state and rendering logic, and enabling pixel-perfect, testable UI.

---

## 2. Main Concepts & System Structure

### 2.1. Window & Layout

- The main window is subdivided into:
  - **TopBarView**: Score, lives, level, timer, messages, specials.
  - **Play Window**: Main gameplay area (blocks, paddle, balls, etc.).
  - **BottomBarView**: Messages, specials, timer.
- **GameLayout** and related classes manage all region and pixel alignment logic.

### 2.2. UI Components & Content Views

- Each UI region is a class/component that:
  - Subscribes to relevant events.
  - Maintains its own display state.
  - Renders itself in its assigned region.
- **UIManager**: Central manager for all UI components, content views, overlays, and bars. Handles view switching and event routing.
- **Content Views**: GameView, InstructionsView, GameOverView, LevelCompleteView, etc. Each is a class/component managed by UIManager.
- **Content View Rendering**: All major content views use a stateless, modular renderer pattern (see 2.3 below) for layout and display, ensuring maintainability and pixel-perfect alignment.

### 2.3. Renderer Utilities

- Stateless rendering utilities (e.g., for lives, digits, bullets, text, logos) are in `src/xboing/renderers/` as `<Thing>Renderer` classes.
- All major UI content views (e.g., `GameOverView`, `LevelCompleteView`, `InstructionsView`) use a modular, stateless renderer pattern:
    - Each row or element is rendered by a `RowRenderer` protocol implementation (`TextRowRenderer`, `BulletRowRenderer`, `LogoRenderer`, etc.).
    - A `CompositeRenderer` orchestrates the layout and reveal/animation of these rows, using explicit y-coordinates for pixel-perfect alignment.
    - This approach ensures modularity, testability, and faithful recreation of the original UI layout.
- Renderer and protocol methods are fully type-annotated (PEP 484), and code is PEP 8/257 compliant.
- The renderer protocol is unified, making it easy to add new row renderers or composite layouts.

### 2.4. Asset Management

- All asset path helpers resolve to the canonical `src/xboing/assets/` directory.
- All images, sounds, and levels are loaded from this directory.

---

## 3. Event-Driven Architecture

### 3.1. Event System

- **All events** (user input, UI, game logic, custom game events) are routed through the Pygame event queue.
- **Custom events** are defined using `pygame.USEREVENT` and posted with `pygame.event.post`.
- **GameState and other models** return a list of typed event instances representing state changes.
- **Controllers** are responsible for posting these returned events to the Pygame event queue.
- **Handlers** (controllers, UI components, managers) implement `handle_events(events)` and check for both built-in and custom event types.

### 3.2. Event Routing Table

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

_All event subscriptions and handling are via the Pygame event queue. All UI components, controllers, and managers use the same event loop and check for their relevant events in `handle_events(events)`._

### 3.3. Adding a New Event: End-to-End Guide

1. **Define the Event Class** in `src/engine/events.py`.
2. **Fire the Event**: Return from model methods, post from controllers.
3. **Handle the Event**: Add logic to `handle_events(events)` in any interested component.
4. **(Optional) Add to AudioManager or UI**: Use a `sound_effect` attribute for automatic sound mapping.
5. **Test the Event**: Run the game and trigger the event.

---

## 4. Controllers, UIManager, and Model Roles

- **UIManager**: Owns and coordinates all UI components, content views, overlays, and manages which view is active. Provides a single `draw_all(surface)` method for rendering the UI.
- **ControllerManager**: Owns all controllers and switches the active controller based on the current view.
- **Controllers**: Each major view has a corresponding controller (e.g., `GameController`, `InstructionsController`, etc.). The active controller handles input, updates, and transitions for its associated view. **Controllers are responsible for posting events returned by model methods.**
- **GameState**: The central model for all gameplay-related state (score, lives, level, timer, specials, game over, etc.). **GameState methods return a list of event instances representing state changes, but do not post events directly.**
- **Other Models**: Specialized models (e.g., `LeaderBoard` for high scores) can be added as needed.

---

## 5. GameShape Abstraction and Shape Hierarchy

- **All core game objects** (Ball, Block, Paddle, Bullet, etc.) now inherit from a unified `GameShape` base class hierarchy.
- **Class Hierarchy:**
  - `GameShape` (abstract base class for all objects with a rect and position)
    - `CircularGameShape` (adds radius and circular logic)
      - `Ball` (inherits from `CircularGameShape`)
    - `Block`, `Paddle`, `Bullet` (inherit directly from `GameShape`)
- **Rationale:**
  - Eliminates code duplication for position, rect, and collision logic.
  - Enables polymorphic collision and drawing methods.
  - Makes it easy to add new shapes (e.g., power-ups, enemies) in the future.
- **Collision and Drawing:**
  - Each shape implements its own `collides_with` and `draw` methods, using polymorphism.
  - Collision systems and renderers now use the base class interface, reducing special cases.
- **Maintainability:**
  - Centralizes shared logic, making future changes and bugfixes easier.
  - All type hints and instantiations have been updated to use the new base classes.
- **See also:** [docs/GAME-SHAPES.md](GAME-SHAPES.md) for technical details, migration steps, and extensibility notes.

---

## 6. Dependency Injection & Construction

- **Dependency injection** is used via the `injector` library.
- The `XBoingModule` (in `src/di_module.py`) provides all bindings for controllers, views, UIManager, and other core objects.
- **UIFactory and ControllerFactory logic** is implemented as DI providers in `XBoingModule`.
- **AppCoordinator**: Synchronizes UIManager and ControllerManager, ensuring the correct controller is active for the current view.
- All construction and wiring of controllers, views, and managers is handled in `xboing.py` using DI providers in `XBoingModule`.
- No direct instantiation of UI or controller classes occurs outside these providers or DI modules.

---

## 7. Main Loop & View-Controller Pattern

- **Main loop** routes events to WindowController (always active) and the active controller for the current view.
- **Per-View Controllers** only receive events when their view is active, and only take the dependencies they need.
- **Global/system events** are always handled by WindowController.
- **UIManager** manages the active view.
- **ControllerManager** manages the active controller, which is swapped in/out as views change.

**Example Main Loop:**
```python
while running:
    events = pygame.event.get()
    input_manager.update(events)
    window_controller.handle_events(events)  # Always active
    controller_manager.active_controller.handle_events(events)  # Only active view's controller
    audio_manager.handle_events(events)
    ui_manager.handle_events(events)
    controller_manager.active_controller.update(delta_time * 1000)
    layout.draw(window.surface)
    ui_manager.draw_all(window.surface)
    window.update()
```

---

## 8. Layout & UI Details

### 8.1. Top Bar Layout

- **Right edge of lives and ammo displays:** Aligned to x = 475.
- **Level display:** Immediately to the right of the lives/ammo group, with no gap.
- **Lives display y-offset:** Fixed at `LIVES_TOP_Y = 12`.
- **Ammo display y-offset:** `lives_y + lives_height + 2`.
- **Grouping:** Lives, ammo, and level displays are visually grouped in the top bar, with no large gaps.
- **Rationale:** Ensures the UI is visually compact, grouped, and matches the reference implementation. All calculations are dynamic based on the rendered width of the lives display.
- **Content views** (e.g., GameOverView, LevelCompleteView, InstructionsView) use explicit y-coordinates for each row renderer, ensuring pixel-perfect vertical alignment as in the original C version.

---

## 9. Extensibility & Best Practices

- **Adding new shapes or events** is straightforward due to the polymorphic, event-driven, and DI-based architecture.
- **All code is PEP 8, PEP 257, and PEP 484 compliant.**
- **Renderer protocol is unified and strictly type-annotated,** making it easy to add new row renderers or composite layouts.
- **Tests and linters** are run before and after every change to ensure quality and maintainability.
- **Renderer and UI code** must pass mypy strict mode and linter checks before merging.

---

## 10. References

- [docs/GAME-SHAPES.md](GAME-SHAPES.md): Technical details on the shape hierarchy and migration.
- [src/layout/game_layout.py](../src/layout/game_layout.py): Layout logic.
- [src/engine/events.py](../src/engine/events.py): Event definitions.
- [src/di_module.py](../src/di_module.py): Dependency injection setup.

---

This conceptual organization should make the architecture, event flow, and extensibility of XBoing Python clear for both maintainers and new contributors.

---
