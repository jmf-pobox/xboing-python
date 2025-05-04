# XBoing Python GUI Layout & Window Design

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

*This document will be expanded to include sprite and object documentation in the future.* 