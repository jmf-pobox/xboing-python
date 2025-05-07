# XBoing Python GUI Design & Architecture

This document describes the graphical user interface (GUI) architecture and window layout of the XBoing Python port. It covers both the visual structure (window regions, layout) and the underlying event-driven, component-based UI system that powers all user interface elements. The goal is to provide a clear, maintainable, and extensible foundation for both developers and designers.

---

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

#### Window Hierarchy Table

| Window         | Parent      | Component/Manager      |
|----------------|------------|------------------------|
| Main Window    | (root)     |                        |
| TopBarView     | Main Window| TopBarView             |
| Score Window   | TopBarView | ScoreDisplay           |
| Level Window   | TopBarView | LevelDisplay, LivesDisplayComponent |
| Message Window | TopBarView | MessageDisplay         |
| Special Window | TopBarView | SpecialDisplay         |
| Time Window    | TopBarView | TimerDisplay           |
| Play Window    | Main Window| ContentViewManager     |

---

## 3. UI Component Structure & Event-Driven Architecture

Each UI region is implemented as a class/component that:
- Subscribes to relevant game events via the `EventBus`
- Maintains its own display state, updated in response to events
- Knows how to render itself in its assigned region (using `GameLayout`)

**Example Components:**
- `TopBarView` (owns and draws ScoreDisplay, LivesDisplayComponent, LevelDisplay, TimerDisplay, MessageDisplay, SpecialDisplay)
- `ScoreDisplay` (subscribes to `ScoreChangedEvent`)
- `LivesDisplayComponent` (subscribes to `LivesChangedEvent`)
- `LevelDisplay` (subscribes to `LevelChangedEvent`)
- `TimerDisplay` (subscribes to timer events)
- `MessageDisplay` (subscribes to `MessageChangedEvent`)
- `SpecialDisplay` (subscribes to special state events)
- `ContentViewManager` (manages play window content views)

### Event Flow
- Game logic fires events (using the `EventBus`).
- UI components update their internal state and redraw as needed in response to these events.
- The main loop simply calls `content_view_manager.draw(window.surface)` for the play window and `top_bar_view.draw(window.surface)` for the top bar after updating game state.

### UI Manager
- The `TopBarView` acts as the UI manager for all top bar elements.
- The `ContentViewManager` manages the play window content views.

### Integration with GameLayout
- UI components use `GameLayout` to determine their drawing regions.
- The window hierarchy remains unchanged; only the update/draw logic is refactored.

---

## 4. Content View Management (ContentViewManager)

The play window region is managed by a `ContentViewManager`, which is responsible for displaying one of several possible content views at any time. This enables the game to support multiple major UI screens, all occupying the same viewport:

- WelcomeView: Title, logo, and start prompt
- InstructionsView: Game instructions and rules
- DemoView: Autoplay demonstration with overlays
- LevelPreviewView: Shows the next level layout and info
- GameView: The main gameplay area (blocks, paddle, balls, etc.)
- GameKeysView: Shows game controls and key bindings
- HighScoresView: Displays high scores and player names

### ContentViewManager Responsibilities
- Maintains a registry of all available content views.
- Listens for events (e.g., ShowWelcomeEvent, ShowInstructionsEvent, etc.) to swap the active view.
- Delegates rendering and (optionally) input handling to the active view.
- Provides a draw(surface) method called by the main loop/UIManager.

### Content View Classes
Each content view is a class/component that:
- Subscribes to relevant events (if needed)
- Renders itself in the play window region
- Handles its own state and logic

### Event Flow
- Game logic or menu navigation fires an event (e.g., ShowInstructionsEvent)
- ContentViewManager receives the event and swaps in the appropriate view
- The new view handles its own rendering and (if needed) input/events

### Extensibility
- New content views can be added by creating a new class and registering it with the manager
- Overlays (e.g., pause, game over) can be layered on top of the current content view if needed

---

## 5. Implementation & Migration Plan

The following step-by-step migration plan was used to refactor the XBoing Python UI to this event-driven, component-based architecture. Each step included guidance for adding or updating tests to ensure correctness and maintainability.

### Step 1: Create the `src/ui/` Package
- Add a new `src/ui/` directory to house all UI components.
- Add an `__init__.py` file.
- **Test:** Ensure the package is importable and visible to the rest of the codebase.

### Step 2: Move/Refactor UI Code into Components
- Identify all UI-related code in `main.py` and `utils/` (score, lives, timer, overlays, menus).
- For each UI region, create a component class in `src/ui/` (e.g., `ScoreDisplay`, `LivesDisplay`, `TimerDisplay`, `MessageDisplay`, `Menu`).
- Move rendering logic and state into these classes.
- **Test:** Add unit tests for each component's rendering (e.g., correct display for given state).

### Step 3: Define UI Events
- In `src/engine/events.py`, define events for UI state changes (e.g., `ScoreChangedEvent`, `LivesChangedEvent`, `LevelChangedEvent`, `TimerUpdatedEvent`, `ShowOverlayEvent`).
- **Test:** Add unit tests for event creation and event bus subscription/dispatch.

### Step 4: Update Game Logic to Fire UI Events
- Refactor game logic to fire UI events when state changes (e.g., after scoring, losing a life, changing level, timer updates, game over, etc.).
- Remove direct UI state mutation from game logic.
- **Test:** Add integration tests to verify that firing a game event results in the correct UI event being fired.

### Step 5: Implement Event-Driven UI Components
- Update each UI component to subscribe to relevant events via the `EventBus`.
- Components update their internal state in response to events and redraw as needed.
- **Test:** Add unit tests to verify that components update correctly in response to events.

### Step 6: Implement `UIManager`
- Create a `UIManager` class that owns all UI components and provides a `draw_all(surface)` method.
- The manager is responsible for drawing all UI components in the correct order each frame.
- **Test:** Add integration tests to verify that the manager draws all components and that updates propagate correctly.

### Step 7: Refactor Main Loop
- Remove direct UI rendering from the main loop in `main.py`.
- Replace with event firing for state changes and a single call to `ui_manager.draw_all(surface)`.
- **Test:** Add end-to-end tests to verify that UI updates correctly in response to gameplay (e.g., scoring, losing lives, level transitions).

### Step 8: Add/Update Documentation
- Update this document and developer docs to describe the new architecture and usage patterns.
- **Test:** Peer review and/or documentation tests (e.g., docstring checks, Sphinx build if used).

### Step 9: Continuous Testing
- Ensure all new code is covered by unit and integration tests.
- Run the full test suite after each migration step to catch regressions early.

---

## 6. References
- `src/ui/top_bar_view.py` — Top bar UI manager
- `src/utils/layout.py` — Window and layout management
- `src/utils/digit_display.py` — Score and timer rendering
- `src/utils/lives_display.py` — Lives display (ball images)
- `src/main.py` — Main game loop and rendering logic
- `src/game/level_manager.py` — Level backgrounds and play area management

---

## 7. Proposed UIManager Component

To further unify and simplify UI management, we propose introducing a `UIManager` class. This class would:

- Own and coordinate all UI components (top bar, bottom bar, overlays, and content views).
- Provide a single `draw_all(surface)` method to render all UI elements in the correct order.
- Handle overlay stacking (e.g., pause, notifications) if needed.
- Route events to the correct UI components or overlays.
- Optionally, manage transitions and animations between views.

### Responsibilities
- Register and own all UI components (ScoreDisplay, LivesDisplay, etc.), bars, and content views.
- Register overlays and manage their display order.
- Provide a unified interface for drawing and updating the UI.
- Serve as the main point of contact for the main loop regarding UI rendering and event routing.

### Integration Points
- The main loop would instantiate a `UIManager` and call `ui_manager.draw_all(surface)` each frame.
- ContentViewManager and overlays would be managed by the UIManager.
- All UI event subscriptions would be handled within the UIManager or delegated to its components.

### Benefits
- Centralizes all UI logic, making the main loop even cleaner.
- Makes it easier to add overlays, modals, or new UI regions.
- Facilitates testing and future refactoring.

---

## 8. View Extraction Progress (as of current refactor)

| View/Component         | Extracted? | File/Status                        |
|------------------------|:----------:|------------------------------------|
| GameView               |    Yes     | `src/ui/game_view.py`              |
| InstructionsView       |    Yes     | `src/ui/instructions_view.py`      |
| GameOverView           |    Yes     | `src/ui/game_over_view.py`         |
| LevelCompleteView      |    Yes     | `src/ui/level_complete_view.py`    |
| WelcomeView            |     No     | Not implemented                    |
| DemoView               |     No     | Not implemented                    |
| LevelPreviewView       |     No     | Not implemented                    |
| GameKeysView           |     No     | Not implemented                    |
| HighScoresView         |     No     | Not implemented                    |
| Score/Lives/Level/Timer/Message/Special | Yes | `src/ui/` components         |
| TopBarView/BottomBarView | Yes      | `src/ui/top_bar_view.py`, etc.     |
| ContentViewManager     |    Yes     | `src/ui/content_view_manager.py`   |

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
| Data/Model      | Owner/Location         | Accessed by           |
|-----------------|-----------------------|-----------------------|
| Game state      | `GameState`           | All controllers/views |
| Level data      | `LevelManager`        | GameController, GameView |
| High scores     | `LeaderBoard` (subclass or separate) | HighScoresController/View |
| Settings        | (optional) Settings model | SettingsController/View |
| Instructions    | Static or minimal     | InstructionsController/View |

---

## 10. Implementation Plan: UIManager and Controllers

### Step 1: UIManager
- Create a `UIManager` class that owns all UI components, content views, overlays, and manages which view is active.
- Move all UI registration and drawing logic from `main.py` into `UIManager`.
- Provide a `draw_all(surface)` method to render the entire UI.
- Refactor the main loop to use `ui_manager.draw_all(surface)`.

### Step 2: Controller Base and ControllerManager
- Define a `BaseController` class with `handle_events(events)` and `update(delta_time)` methods.
- Create a `ControllerManager` (or add to UIManager) to own all controllers and switch the active controller based on the current view.
- Refactor the main loop to delegate input and update logic to the active controller.

### Step 3: Implement Initial Controllers
- **GameController**: Handles gameplay input, updates, and transitions.
- **LevelCompleteController**: Handles input and transitions for the level complete view.
- **InstructionsController**: Handles input and transitions for the instructions view.
- Each controller should be responsible for its own logic, removing conditional logic from the main loop.

### Step 4: Integration
- When a view is activated via UIManager, the corresponding controller is also activated.
- Controllers interact with GameState and other models as needed.
- Views remain focused on rendering and do not handle input or state changes directly.

### Step 5: Testing and Documentation
- Add/extend unit and integration tests for UIManager, controllers, and transitions.
- Update documentation to reflect the new architecture and flow.

---

*This document provides a unified overview of both the visual layout and the event-driven, component-based UI architecture of XBoing Python. It is intended to guide both current development and future extensions.* 