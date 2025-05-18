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
  - **Block explosion animations:** Each block type explodes with its own animation (e.g., purple blocks use `expurp[1-3].png`). In the Python port, the same animation is used for both ball and bullet hits. See [GitHub Issue #6](https://github.com/jmf-pobox/xboing-python/issues/6).
- **Python Status:**
  - **Ammo state, events, UI, and sound effects:** Complete.
  - **Bullet creation, movement, and removal:** Complete.
  - **Bullet rendering (with sprite):** Complete.
  - **Bullet-block collision detection:** Complete and integrated.
  - **DI/registry pattern and architecture:** Complete.
  - **Tests:** Implemented for most logic; coverage can be improved.
  - **Block explosion animations:** Currently, the same animation is used for both ball and bullet hits. Custom per-block-type explosion animations (as in the C version) are not yet implemented ([issue #6](https://github.com/jmf-pobox/xboing-python/issues/6)).
  - **Machine gun powerup:** Not yet implemented.
- **Next Steps:**
  - Implement custom block explosion animations for bullet and ball hits (see [issue #6](https://github.com/jmf-pobox/xboing-python/issues/6)).
  - Implement the machine gun powerup (state, UI, firing logic).
  - Increase test coverage for all paddle gun logic and edge cases.

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
- Add ammo (bullet count) state to paddle/player. **[Done]**
- Implement events for ammo collected (e.g., Max Ammo block) and ammo used (shot fired). **[Done]**
- Create a UI component to display current ammo count; update in response to state/events. **[Done]**
- Play sound effects for ammo collection and shot fired (even if no bullet is created yet). **[Done]**
- Add unit tests for all of the above. **[Done]**

### Phase 2: Machine Gun Block State and UI (No Bullets Yet)
- Add machine gun mode state (boolean/timer). **[Not started]**
- Add logic to activate/deactivate machine gun mode.
- Add UI indicator for machine gun mode.
- Add unit tests for all of the above.

### Phase 3: Bullet/Projectile Logic
- Implement bullet creation, movement, and removal. **[Done]**
- Integrate bullet updates into the game loop. **[Done]**
- Implement bullet collision with blocks, balls, and enemies. **[Done for blocks; not needed for balls/enemies yet]**
- Add unit tests for all of the above. **[Partial; needs more coverage]**

### Phase 4: Integration and Polish
- Integrate all features and ensure smooth interaction between state, UI, sound, and bullet logic. **[In progress]**
- Add/expand integration tests. **[Next step]**

---

## References
- `xboing2.4-clang/paddle.c`, `xboing2.4-clang/gun.c`, `xboing2.4-clang/draw.c`, `xboing2.4-clang/special_display.c`, `xboing2.4-clang/audio.c`, `xboing2.4-clang/main.c`
- See also: [docs/xboing2.4/README](README)
- [GitHub Issue #6: Exloding blocks do not use custom animations as per original C version.](https://github.com/jmf-pobox/xboing-python/issues/6) 