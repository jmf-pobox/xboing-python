# XBoing Python Paddle Guide Animation Design & Requirements

## Overview

The paddle "arc" animation in XBoing is implemented as a sequence of pre-rendered guide images ("guides") that appear above the ball when it is stuck to the paddle and ready to launch. This animation visually indicates the direction in which the ball will be fired, allowing the player to aim the initial trajectory. The animation and logic are implemented in the original C code (`ball.c`), not as a drawn arc but as a cycling set of guide images.

## Purpose

- Visually indicate the current launch direction of the ball while it is "stuck" to the paddle (before launch).
- Allow the player to adjust the launch angle using input (keyboard or mouse) before firing.
- Provide feedback and anticipation for the launch event.

## Animation & Behavior

- The guide animation is a sequence of 11 pre-rendered images ("guide1.png" to "guide11.png") that are displayed above the ball.
- The current guide image is selected by the `guidePos` variable, which ranges from 0 (far left) to 10 (far right), with 5 or 6 as the center.
- The guide image is cycled left and right (ping-pong) to create a pulsing/animated effect, controlled by a frame counter and the `inc` variable (direction of cycling).
- The guide is only visible when the ball is in the `BALL_READY` state (i.e., stuck to the paddle and waiting for launch).
- The guide disappears immediately when the ball is launched.

## Visual Details

- Each guide image is a small PNG (see `assets/images/guides/`) representing a possible launch direction.
- The guide is rendered above the ball, offset by a fixed amount (typically 16 pixels above the ball's center).
- The guide images are visually distinct and indicate the direction the ball will travel when launched.
- The animation cycles through the images to create a "bouncing" or "pulsing" effect.

## User Interaction

- **Note:** In the original C game (and this Python port), the guide is animated only. User input (left/right keys or mouse) does **not** affect the guide position or launch angle. The launch direction is determined by the current animated guide position at the moment of launch.
- The guide image updates in real time to reflect the current aim.
- When the player launches the ball (e.g., by pressing space or clicking), the guide disappears and the ball is fired at the chosen angle.
- The launch direction is determined by the current `guidePos`, which maps to a specific (dx, dy) velocity for the ball (see `ChangeBallDirectionToGuide` in `ball.c`).

## Animation & Timing

- The guide animation cycles every 8 frames (see `MoveGuides` in `ball.c`).
- The cycling is ping-pong: when the guide reaches the far left (0) or far right (10), the direction reverses.
- The guide is cleared and redrawn every frame while visible.
- The guide is always centered horizontally on the ball and offset vertically above it.

## Asset Requirements

- **Guide images:** 11 PNGs (`guide1.png` to `guide11.png`) in `assets/images/guides/`, each representing a different launch direction.

## Implementation Notes

- The guide animation should be managed as part of the ball or paddle view/component.
- The current `guidePos` is updated only by the animation logic, not by user input.
- The guide image should be blitted above the ball only when the ball is in the ready-to-launch state.
- The launch direction mapping (from `guidePos` to (dx, dy)) should match the table in `ChangeBallDirectionToGuide` in `ball.c`.
- The animation should be faithful to the original, including the ping-pong cycling and frame timing.

## References

- Original C implementation: `xboing2.4-clang/ball.c` (see `MoveGuides`, `ChangeBallDirectionToGuide`, and related logic)
- Guide images: `src/xboing/assets/images/guides/`

## Technical Breakdown & Key Code

### State Machine & Animation Logic

- **States:**
    - Guide is only visible when the ball is in the `BALL_READY` state.
    - When the ball is launched, the guide is hidden.
- **Guide Animation:**
    - `guidePos` (int, 0-10) determines which guide image to show.
    - `inc` (int, +1 or -1) determines the direction of cycling.
    - Every 8 frames, `guidePos` is incremented or decremented by `inc`.
    - When `guidePos` reaches 0 or 10, `inc` reverses direction (ping-pong effect).
    - The guide image is always drawn at a fixed offset above the ball's center.

#### Pseudocode for Animation Cycle

```python
# Called every frame while ball is BALL_READY
def update_guide_animation():
    global guidePos, inc, frame
    if frame % 8 == 0:
        guidePos += inc
        if guidePos == 10:
            inc = -1
        elif guidePos == 0:
            inc = 1
```

#### Drawing the Guide

```python
def draw_guide(surface, ball_x, ball_y, guide_images, guidePos):
    # Offset the guide above the ball
    guide_img = guide_images[guidePos]
    guide_rect = guide_img.get_rect(center=(ball_x, ball_y - 16))
    surface.blit(guide_img, guide_rect)
```

#### User Input Handling

```python
def handle_input(event):
    global guidePos
    if event.type == KEYDOWN:
        if event.key == K_LEFT and guidePos > 0:
            guidePos -= 1
        elif event.key == K_RIGHT and guidePos < 10:
            guidePos += 1
    # Optionally handle mouse movement for aiming
```

#### Launch Direction Mapping

- When the ball is launched, the current `guidePos` determines the (dx, dy) velocity:

| guidePos | dx  | dy  |
|----------|-----|-----|
| 0        | -5  | -1  |
| 1        | -4  | -2  |
| 2        | -3  | -3  |
| 3        | -2  | -4  |
| 4        | -1  | -5  |
| 5        |  0  | -5  |
| 6        |  1  | -5  |
| 7        |  2  | -4  |
| 8        |  3  | -3  |
| 9        |  4  | -2  |
| 10       |  5  | -1  |

```python
def get_launch_velocity(guidePos):
    mapping = [(-5, -1), (-4, -2), (-3, -3), (-2, -4), (-1, -5),
               (0, -5), (1, -5), (2, -4), (3, -3), (4, -2), (5, -1)]
    return mapping[guidePos]
```

### Integration Points

- The guide animation logic should be integrated into the ball or paddle update/draw loop.
- The guide images should be preloaded and stored in a list.
- The current `guidePos` and `inc` should be part of the game or ball state.
- The launch direction should be set when the player launches the ball, using the mapping above.

## OOP DESIGN (Refined for Current Codebase)

### Ball
- **State:**  
  - Add `guide_pos` (int, 0–10) and `guide_inc` (+1/-1) as attributes to the `Ball` class.
  - Add a boolean `show_guide` or similar, set to `True` when `stuck_to_paddle` is `True`.
- **Animation Logic:**  
  - In the `Ball.update()` method, if `self.stuck_to_paddle` is `True`, update `guide_pos` every 8 frames, ping-ponging between 0 and 10.
- **Input Handling:**  
  - No user input for guide_pos: matches C game.
- **Launch Logic:**  
  - When `release_from_paddle()` is called, set the ball's velocity `(vx, vy)` using the mapping for the current `guide_pos`, and set `show_guide` to `False`.

### BallManager
- **State/Access:**  
  - No major changes needed, but may add helper methods to get the currently "ready" ball (i.e., `stuck_to_paddle` is `True`).
- **Integration:**  
  - Used by `GameController` to access and update the ball(s) for guide animation and input.

### Paddle
- **Input Handling:**  
  - The current `Paddle` class does not handle input or aiming logic directly. Input is handled by the controller, so no changes are needed here for the guide.

### GameController
- **Input Routing:**  
  - No user input for guide_pos: matches C game.
  - On launch (space or mouse), call the ball's `release_from_paddle()`, which will use the current `guide_pos` for launch direction.
- **State Management:**  
  - When creating a new ball (e.g., after life loss), initialize its `guide_pos` to 5 or 6 (center) and `guide_inc` to +1.

### GameView
- **Drawing:**  
  - In the `draw()` method, after drawing the ball, if the ball is `stuck_to_paddle` and `show_guide` is `True`, blit the correct guide image above the ball using `guide_pos` as the index.
  - Preload the guide images at startup and make them available to the view.

### Tests
- **Test Cases:**  
  - Add or update tests to verify:
    - Guide animates correctly (cycles, ping-pongs) when the ball is stuck.
    - User input changes the guide and launch direction.
    - Guide is hidden after launch.
    - Launch direction matches the mapping.

---

This design ensures the paddle guide animation is a responsive, visually clear, and faithful recreation of the original, using the correct assets and animation logic. 