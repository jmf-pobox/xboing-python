# Paddle Features: XBoing Python vs. Original C Version

This document tracks the status and design of paddle-related features in the Python port of XBoing, with commentary on how each feature worked in the original C game and references to the relevant C code.

---

## 1. Sticky Paddle (Glue) Powerup
- **Description:** When active, the paddle "catches" the ball, which sticks to it until released by a mouse click or after a timeout.
- **Original C Game:**
  - Implemented in `paddle.c` (see `stickyOn`, `stickyOff`, and logic in `MovePaddle` and `ReleaseBall`).
  - The sticky state is activated by hitting a sticky block; when active, balls stick to the paddle until the player loses the ball or finishes the level (original C behavior: sticky is lost on ball loss or level completion).
- **Python Status:** Done

---

## 2. Reverse Powerup
- **Description:** When active, the paddle's movement on the x-axis is reversed, adding to the challenge for the player.
- **Original C Game:**
  - The reverse state is toggled by hitting a reverse block
- **Python Status:** Done

---

## 3. Paddle Shrink / Grow Powerup
- **Description:** Paddle size and position should scale with the play area, supporting window resizing.
- **Original C Game:**
  - Paddle size is relative to window size; see `paddle.c` and `main.c` for resize handling.
- **Python Status:** Done
- **Next Steps:** Consider implications for enabling game resizing.

---

## 4. Paddle "Guns"/Shooting Powerup
- **Description:** Paddle can shoot projectiles for a limited time after collecting a powerup.
- **Original C Game:**
  - Implemented in `paddle.c` and `gun.c` (see `gunOn`, `gunOff`, and projectile logic).
  - Paddle fires bullets upward from its position; firing is limited by a timer or number of shots, depending on the powerup.
- **Python Status:** Missing
- **Feature Gap:** Gun state, firing logic, projectile collisions, and related UI/sound events are not yet implemented.
- **Next Steps:** Implement gun state, firing, projectile collisions, and events for UI/sound. **This is the next major paddle feature to implement.**

---

## 5. Paddle Movement Tweaks
- **Description:** Fine-tune paddle acceleration, deceleration, and max speed for a more "classic" feel.
- **Original C Game:**
  - Movement logic in `paddle.c` (`MovePaddle`, `SetPaddleDirection`).
  - Includes acceleration, deceleration, and speed limits.
- **Python Status:** Partial (basic movement, no acceleration)
- **Feature Gap:** No acceleration/deceleration or speed cap.
- **Next Steps:** Add movement physics and tests for edge cases.

---

## 6. Sound Effects for Paddle Events
- **Description:** Play sounds for paddle size change, sticky/reverse activation, etc.
- **Original C Game:**
  - Sound triggers in `audio.c` and `paddle.c` (see `PlayPaddleSound`, `stickyOn`, `reverseOn`).
- **Python Status:** Implemented for size change, sticky, and reverse.
- **Feature Gap:** Missing for gun-related sound effects (activation, firing, etc.).

---

## 7. UI Feedback for Paddle State
- **Description:** Show icons, text, or effects when paddle is in a special state (sticky, reverse, gun, etc.).
- **Original C Game:**
  - UI feedback in `special_display.c` and `draw.c` (see `DrawSpecials`, `DrawPaddle`).
- **Python Status:** Partial (specials area shows sticky and reverse states; no feedback yet for gun or other specials)
- **Feature Gap:** Done for reverse, sticky.
- **Next Steps:** Update UI components to listen for paddle state events and display feedback for gun and other specials.

---

## Implementation Plan (Phased Approach)

### Phase 1: Ammo State, Events, UI, and Sound Effects (No Bullets Yet)
- Add ammo (bullet count) state to paddle/player.
- Implement events for ammo collected (e.g., Max Ammo block) and ammo used (shot fired).
- Create a UI component to display current ammo count; update in response to state/events.
- Play sound effects for ammo collection and shot fired (even if no bullet is created yet).
- Add unit tests for all of the above.

### Phase 2: Machine Gun Block State and UI (No Bullets Yet)
- Add machine gun mode state (boolean/timer).
- Add logic to activate/deactivate machine gun mode.
- Add UI indicator for machine gun mode.
- Add unit tests for all of the above.

### Phase 3: Bullet/Projectile Logic
- Implement bullet creation, movement, and removal.
- Integrate bullet updates into the game loop.
- Implement bullet collision with blocks, balls, and enemies.
- Add unit tests for all of the above.

### Phase 4: Integration and Polish
- Integrate all features and ensure smooth interaction between state, UI, sound, and bullet logic.
- Add/expand integration tests.

---

## References
- `xboing2.4-clang/paddle.c`, `xboing2.4-clang/gun.c`, `xboing2.4-clang/draw.c`, `xboing2.4-clang/special_display.c`, `xboing2.4-clang/audio.c`, `xboing2.4-clang/main.c`
- See also: [docs/xboing2.4/README](README) 