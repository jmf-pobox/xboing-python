# Paddle Features: XBoing Python vs. Original C Version

This document tracks the status and design of paddle-related features in the Python port of XBoing, with commentary on how each feature worked in the original C game and references to the relevant C code.

---

## 1. Sticky Paddle (Glue) Powerup
- **Description:** When active, the paddle "catches" the ball, which sticks to it until released by a mouse click or after a timeout.
- **Original C Game:**
  - Implemented in `paddle.c` (see `stickyOn`, `stickyOff`, and logic in `MovePaddle` and `ReleaseBall`).
  - The sticky state is toggled by hitting a sticky block; when active, balls stick to the paddle until the player clicks or a timer expires.
- **Python Status:** Missing (planned)
- **Feature Gap:** No sticky paddle logic or event yet. Needs event-driven state, UI feedback, and ball release logic.
- **Next Steps:** Implement sticky state, event, and UI feedback. Ensure correct ball release and auto-launch.

---

## 2. Paddle Animation/Visual Feedback
- **Description:** Paddle changes appearance (color, sprite, or animation) when special states (reverse, sticky, etc.) are active.
- **Original C Game:**
  - Paddle sprite changes in `paddle.c` and `draw.c` (see `DrawPaddle` and state checks).
  - Visual feedback for sticky, reverse, and gun states.
- **Python Status:** Partial (basic rendering only)
- **Feature Gap:** No visual feedback for special states.
- **Next Steps:** Update rendering logic to reflect paddle state and animate transitions.

---

## 3. Paddle "Guns"/Shooting Powerup
- **Description:** Paddle can shoot projectiles for a limited time after collecting a powerup.
- **Original C Game:**
  - Implemented in `paddle.c` and `gun.c` (see `gunOn`, `gunOff`, and projectile logic).
  - Paddle fires bullets upward; limited by timer or shots.
- **Python Status:** Missing
- **Feature Gap:** No gun state, firing, or projectile logic.
- **Next Steps:** Implement gun state, firing, projectile collisions, and events for UI/sound.

---

## 4. Paddle Movement Tweaks
- **Description:** Fine-tune paddle acceleration, deceleration, and max speed for a more "classic" feel.
- **Original C Game:**
  - Movement logic in `paddle.c` (`MovePaddle`, `SetPaddleDirection`).
  - Includes acceleration, deceleration, and speed limits.
- **Python Status:** Partial (basic movement, no acceleration)
- **Feature Gap:** No acceleration/deceleration or speed cap.
- **Next Steps:** Add movement physics and tests for edge cases.

---

## 5. Paddle Resizing/Window Resize Robustness
- **Description:** Paddle size and position should scale with the play area, supporting window resizing.
- **Original C Game:**
  - Paddle size is relative to window size; see `paddle.c` and `main.c` for resize handling.
- **Python Status:** Partial (fixed sizes, not robust to window resize)
- **Feature Gap:** Paddle size/position not updated on window resize.
- **Next Steps:** Express paddle size as a percentage of play area; update all logic to use relative sizes.

---

## 6. Sound Effects for Paddle Events
- **Description:** Play sounds for paddle size change, sticky/reverse activation, etc.
- **Original C Game:**
  - Sound triggers in `audio.c` and `paddle.c` (see `PlayPaddleSound`, `stickyOn`, `reverseOn`).
- **Python Status:** Missing
- **Feature Gap:** Done for grow, shrink, reverse, sticky
- **Next Steps:** Integrate with audio manager and add/expand tests for sound triggers.

---

## 7. UI Feedback for Paddle State
- **Description:** Show icons, text, or effects when paddle is in a special state (sticky, reverse, gun, etc.).
- **Original C Game:**
  - UI feedback in `special_display.c` and `draw.c` (see `DrawSpecials`, `DrawPaddle`).
- **Python Status:** Partial (basic UI, no special state feedback)
- **Feature Gap:** No UI feedback for paddle state.
- **Next Steps:** Update UI components to listen for paddle state events and display feedback.

---

## References
- `xboing2.4-clang/paddle.c`, `xboing2.4-clang/gun.c`, `xboing2.4-clang/draw.c`, `xboing2.4-clang/special_display.c`, `xboing2.4-clang/audio.c`, `xboing2.4-clang/main.c`
- See also: [docs/xboing2.4/README](README) 