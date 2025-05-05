# XBoing Python GUI Layout & Window Design

**Status Summary (2024-05-05):**
- The play window is now managed by a ContentViewManager, which swaps between content views (currently GameView and InstructionsView).
- The main loop delegates all play window rendering to ContentViewManager.
- Top bar UI (score, lives, timer, message, specials) remains visible and is not affected by content view swaps.
- InstructionsView and GameView are implemented and fully integrated.
- Additional content views (WelcomeView, DemoView, LevelPreviewView, GameKeysView, HighScoresView) and overlays (Game Over, Level Complete, etc.) are planned.
- Event-driven view switching (e.g., ShowWelcomeEvent) is a next step.
- See TODO.md for detailed action items.

This document describes the window and layout structure of the XBoing Python port, focusing on the containers and UI regions that make up the game's graphical interface. This is intended for developers and designers working on the game's UI, not for documenting individual sprites or game objects (which will be covered separately).

---

## 1. Main Window Hierarchy

The game window is organized into a hierarchy of virtual windows, mimicking the original XBoing layout. The main window is subdivided into several regions, each with a specific purpose.

```
+------------------------------------------------------------+
|                      Main Game Window                      |
|                                                            |
|  +-------------------+---------------------------------+   |
|  |   Score Window    |         Level Window            |   |
|  +-------------------+---------------------------------+   |
|  |                                                     |   |
|  |                  Play Window                        |   |
|  |                                                     |   |
|  +-----------------------------------------------------+   |
|  | Message | Special | Time Window                     |   |
|  +-----------------------------------------------------+   |
+------------------------------------------------------------+
```

### Window Regions
- **Main Window**: The root window, contains all other regions.
- **Score Window**: Displays the player's score using LED-style digits. (Parent: Main Window)
- **Level Window**: Shows the current level number and lives display (ball images). (Parent: Main Window)
- **Play Window**: The main game area where blocks, paddle, and balls are rendered. (Parent: Main Window)
- **Message Window**: Displays level names or status messages. (Parent: Main Window)
- **Special Window**: Reserved for bonus displays or special effects. (Parent: Main Window)
- **Time Window**: Shows the level timer in MM:SS format. (Parent: Main Window)

#### Window Hierarchy Table

|---------------|---------------|
| Window        | Parent        |
|---------------|---------------|
| Main Window   | (root)        |
| Score Window  | Main Window   |
| Level Window  | Main Window   |
| Play Window   | Main Window   |
| Message Window| Main Window   |
| Special Window| Main Window   |
| Time Window   | Main Window   |
|---------------|---------------|

---

## 2. Layout Details (from `GameLayout`)

- **Window Sizes (pixels, matching original XBoing):**
  - Main Window: 565 x 710
  - Play Window: 495 x 580
  - Score Window: 224 x 42
  - Level Window: (dynamic width, 52 high)
  - Message Window: (half play width, 30 high)
  - Special Window: 180 x 35
  - Time Window: (1/8 play width, 35 high)

- **Positioning:**
  - The Score and Level windows are at the top.
  - The Play window is centered below them.
  - The Message, Special, and Time windows are at the bottom.

---

## 3. What Each Region Displays

### Score Window
- **Displays:** Player's score using LED-style digits (see `DigitDisplay`).
- **Rendering:**
  - Uses digit sprites for a classic LED look.
  - Right-aligned or left-aligned as per original game.

### Level Window
- **Displays:**
  - Current level number (LED digits).
  - Number of lives left (ball images, see `LivesDisplay`).
- **Rendering:**
  - Lives are always shown as 3 slots, with invisible balls on the left for lost lives.

### Play Window
- **Displays:**
  - The main game area: blocks, paddle, balls, and all gameplay action.
- **Background:**
  - Cycles through different backgrounds per level (see `level_manager.py`).

### Message Window
- **Displays:**
  - Level name or status messages (e.g., "Genesis", "Level Complete!").
- **Rendering:**
  - Text is left-aligned, green for level names.

### Special Window
- **Displays:**
  - Reserved for bonus or special effects (not always used).

### Time Window
- **Displays:**
  - Level timer in MM:SS format, using LED-style digits and a yellow colon.
  - When time is low, background behind timer turns red.

---

## 4. Rendering Flow (from `main.py`)

- Each frame, the main loop:
  1. Clears the window and draws the layout backgrounds.
  2. Draws blocks, paddle, and balls in the play area.
  3. Draws the score, level, and lives in the top bar.
  4. Draws the level name and timer in the bottom bar.
  5. Handles overlays for game over, level complete, etc.

---

## 5. Extending the Layout

- The layout is managed by `GameLayout` and can be extended by adding new `GameWindow` regions.
- Each region can have its own background (color or image), children, and draw logic.
- The current design is modular and matches the original game's UI structure.

---

## 6. References
- `src/utils/layout.py` — Window and layout management
- `src/utils/digit_display.py` — Score and timer rendering
- `src/utils/lives_display.py` — Lives display (ball images)
- `src/main.py` — Main game loop and rendering logic
- `src/game/level_manager.py` — Level backgrounds and play area management

---

## 7. Event-Driven, Component-Based UI Architecture (Proposed)

### Overview

To improve maintainability, testability, and extensibility, the XBoing Python port will migrate to an event-driven, component-based UI architecture. This approach separates game state (logic) from UI rendering, using the Observer pattern (via the existing `EventBus`) to decouple state changes from UI updates. This is both idiomatic for Pygame and aligns with modern MVC principles.

### Rationale
- **Decoupling:** UI components do not query or mutate game state directly; they react to events.
- **Testability:** UI logic can be tested in isolation by firing events.
- **Extensibility:** New UI features (e.g., overlays, menus) can be added as components without modifying core game logic.
- **Pygame Compatibility:** The design fits naturally with Pygame's event loop and rendering model.

### UI Component Structure
- Each UI region (score, lives, timer, overlays, menus) is implemented as a class/component.
- Components:
  - Subscribe to relevant game events via the `EventBus`.
  - Maintain their own display state, updated in response to events.
  - Know how to render themselves in their assigned region (using `GameLayout`).

**Example Components:**
- `ScoreDisplay` (subscribes to `ScoreChangedEvent`)
- `LivesDisplay` (subscribes to `LifeLostEvent` or similar)
- `LevelDisplay` (subscribes to `LevelChangedEvent`)
- `TimerDisplay` (subscribes to timer events)
- `MessageOverlay` (subscribes to `GameOverEvent`, `LevelCompleteEvent`, etc.)
- `Menu` (subscribes to UI navigation events)

### Event Flow
- Game logic fires events (using the existing `EventBus`).
- UI components update their internal state and redraw as needed in response to these events.
- The main loop simply calls `ui_manager.draw_all(window.surface)` after updating game state.

### UI Manager
- A `UIManager` class owns all UI components and handles drawing them in the correct order.
- Optionally, it can route UI-specific events (e.g., menu navigation).

### Integration with GameLayout
- UI components use `GameLayout` to determine their drawing regions.
- The window hierarchy remains unchanged; only the update/draw logic is refactored.

### Migration Plan Outline
1. **Create `src/ui/` Package:** Move or refactor UI-related code (score, lives, timer, overlays, menus) into this package.
2. **Implement UI Components:** Refactor each UI region into a component class that subscribes to relevant events.
3. **Introduce UI Events:** Define events such as `ScoreChangedEvent`, `LifeLostEvent`, `LevelChangedEvent`, etc., in `events.py`.
4. **Add UIManager:** Implement a manager to own and draw all UI components.
5. **Refactor Main Loop:** Remove direct UI rendering from the main loop; fire events for state changes and call `ui_manager.draw_all(surface)`.
6. **Test and Iterate:** Ensure all UI updates are event-driven and components are decoupled from game logic.

---

*This section describes the planned migration to an event-driven, component-based UI for XBoing Python. See the migration plan for step-by-step details.*

---

*This document will be expanded to include sprite and object documentation in the future.*

---

## 8. Migration Plan: Event-Driven, Component-Based UI

This section details the step-by-step migration plan for refactoring the XBoing Python UI to an event-driven, component-based architecture. Each step includes guidance for adding or updating tests to ensure correctness and maintainability.

### Step 1: Create the `src/ui/` Package
- Add a new `src/ui/` directory to house all UI components.
- Add an `__init__.py` file.
- **Test:** Ensure the package is importable and visible to the rest of the codebase.

### Step 2: Move/Refactor UI Code into Components
- Identify all UI-related code in `main.py` and `utils/` (score, lives, timer, overlays, menus).
- For each UI region, create a component class in `src/ui/` (e.g., `ScoreDisplay`, `LivesDisplay`, `TimerDisplay`, `MessageOverlay`, `Menu`).
- Move rendering logic and state into these classes.
- **Test:** Add unit tests for each component's rendering (e.g., correct display for given state).

### Step 3: Define UI Events
- In `src/engine/events.py`, define events for UI state changes (e.g., `ScoreChangedEvent`, `LifeLostEvent`, `LevelChangedEvent`, `TimerUpdatedEvent`, `ShowOverlayEvent`).
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
- Update `GUI-DESIGN.md` and developer docs to describe the new architecture and usage patterns.
- **Test:** Peer review and/or documentation tests (e.g., docstring checks, Sphinx build if used).

### Step 9: Continuous Testing
- Ensure all new code is covered by unit and integration tests.
- Run the full test suite after each migration step to catch regressions early.

---

*This migration plan ensures a smooth, test-driven transition to an event-driven, component-based UI for XBoing Python. Each step is designed to be incremental and verifiable.*

# Play Window Content Management (ContentViewManager)

The play window region is managed by a ContentViewManager, which is responsible for displaying one of several possible content views at any time. This enables the game to support multiple major UI screens, all occupying the same viewport:

- WelcomeView: Title, logo, and start prompt
- InstructionsView: Game instructions and rules
- DemoView: Autoplay demonstration with overlays
- LevelPreviewView: Shows the next level layout and info
- GameView: The main gameplay area (blocks, paddle, balls, etc.)
- GameKeysView: Shows game controls and key bindings
- HighScoresView: Displays high scores and player names

## ContentViewManager Responsibilities
- Maintains a registry of all available content views.
- Listens for events (e.g., ShowWelcomeEvent, ShowInstructionsEvent, etc.) to swap the active view.
- Delegates rendering and (optionally) input handling to the active view.
- Provides a draw(surface) method called by the main loop/UIManager.

## Content View Classes
Each content view is a class/component that:
- Subscribes to relevant events (if needed)
- Renders itself in the play window region
- Handles its own state and logic

## Event Flow
- Game logic or menu navigation fires an event (e.g., ShowInstructionsEvent)
- ContentViewManager receives the event and swaps in the appropriate view
- The new view handles its own rendering and (if needed) input/events

## Extensibility
- New content views can be added by creating a new class and registering it with the manager
- Overlays (e.g., pause, game over) can be layered on top of the current content view if needed

## Example Usage
- The main loop or UIManager calls content_view_manager.draw(surface) each frame
- To switch to the Instructions screen: event_bus.fire(ShowInstructionsEvent())
- To return to gameplay: event_bus.fire(ShowGameEvent()) 