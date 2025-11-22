# Level Complete View - Pixel-Perfect Requirements

**Document Status:** Active Requirements
**Original Reference:** `xboing2.4-clang/bonus.c` (906 lines), `bonus.h` (123 lines)
**Current Implementation:** `src/xboing/ui/level_complete_view.py` (416 lines)
**Fidelity Status:** 60-70% functional, 40-50% visual fidelity
**Target:** 100% pixel-perfect recreation of original XBoing 2.4 bonus screen

---

## Executive Summary

The level complete (bonus) screen is a critical moment in the player experience - it provides reward feedback, score progression visibility, and transition between levels. The original XBoing 2.4 implementation features animated elements, conditional displays, real-time score updates, and precise timing that creates a satisfying, arcade-style feel.

**Current Gaps:**
- Missing ball border animation (major visual element)
- Missing small title pixmap (brand identity)
- No shadow text rendering (depth/polish)
- Incorrect timing (millisecond-based vs frame-based)
- Static score display (no real-time updates)
- No conditional skip logic (shows all content always)
- Hardcoded positions (not dynamic based on font metrics)

**Priorities:**
- **P1 (Must Have):** Visual elements, dynamic positioning, state machine, timing
- **P2 (Should Have):** Conditional logic, save level features, audio volumes
- **P3 (Nice to Have):** Font matching, color precision, window effects

---

## Configuration Constants

### Original XBoing 2.4 Values

```python
# Screen Dimensions
MAIN_WIDTH = 70
MAIN_HEIGHT = 130
PLAY_WIDTH = 495
PLAY_HEIGHT = 580
TOTAL_WIDTH = MAIN_WIDTH + PLAY_WIDTH  # 565
TOTAL_HEIGHT = MAIN_HEIGHT + PLAY_HEIGHT  # 710

# Border Specifications
BORDER_LEFT = 55
BORDER_RIGHT = 515  # (PLAY_WIDTH + MAIN_WIDTH) - 50
BORDER_TOP = 73
BORDER_BOTTOM = 625  # (PLAY_HEIGHT + MAIN_HEIGHT) - 85
BALL_SPACING = 22  # pixels between border balls

# Layout
GAP = 30  # vertical spacing unit
INITIAL_YPOS = 180  # starting y-coordinate for content

# Timing (at 60 FPS)
LINE_DELAY = 100  # frames (~1666ms)
LINE_DELAY_FAST = 5  # frames (~83ms)
LINE_DELAY_DOUBLE = 200  # frames (~3333ms)

# Bonus Scoring
BONUS_COIN_SCORE = 3000
SUPER_BONUS_SCORE = 50000
BULLET_SCORE = 500
LEVEL_SCORE = 100
TIME_BONUS_MULTIPLIER = 100
MAX_BONUS_COINS = 8  # threshold for super bonus
SAVE_LEVEL_INTERVAL = 5  # show save icon every Nth level

# Visual Assets
SMALL_TITLE_WIDTH = 237
SMALL_TITLE_HEIGHT = 37
SMALL_TITLE_X = 282  # TOTAL_WIDTH // 2
SMALL_TITLE_Y = 120
BONUS_COIN_WIDTH = 27
BONUS_COIN_SPACING = 10
BULLET_WIDTH = 7
BULLET_SPACING = 3
PRESS_SPACE_Y = 568  # PLAY_HEIGHT - 12
FLOPPY_ICON_SIZE = 32
FLOPPY_ICON_X = 465  # TOTAL_WIDTH - 100
FLOPPY_ICON_Y = 580  # PLAY_HEIGHT
```

**Source:** `bonus.c` lines 40-67, `misc.h` lines 25-41

---

## Feature 1: Ball Border Animation

### Original XBoing Behavior

The bonus screen features an animated border of bouncing balls around the entire screen perimeter. This creates a dynamic, arcade-style frame that reinforces the game's identity and provides visual interest during score tallying.

**Implementation:** `DrawBallBorder()` function in `bonus.c` lines 194-232

```c
// Draws balls at 22-pixel intervals along four edges
// Each ball animates through BALL_SLIDES frames
// Top: y=73, x from 55 to 515
// Bottom: y=625, x from 55 to 515
// Left: x=55, y from 73 to 625
// Right: x=515, y from 73 to 625
```

### Visual Specification

- **Position:** Four edges at BORDER_LEFT (55), BORDER_RIGHT (515), BORDER_TOP (73), BORDER_BOTTOM (625)
- **Size:** Standard ball size (exact pixels from ball sprite)
- **Spacing:** 22 pixels center-to-center between balls
- **Colors:** Standard ball sprite colors (multi-colored animated)
- **Animation:** Each ball cycles through BALL_SLIDES frames continuously
- **Z-Order:** Drawn first (background layer)

### Functional Requirements

1. Calculate ball positions along each edge with 22px spacing
2. Maintain separate animation frame counter for each ball
3. Advance each ball's frame on every update cycle
4. Wrap frame counter back to 0 after reaching BALL_SLIDES
5. Draw balls in order: top edge, bottom edge, left edge, right edge
6. Use standard ball sprite pixmaps for rendering
7. Animation runs continuously throughout bonus screen display

### Acceptance Criteria

- [ ] Balls appear along all four edges at correct positions
- [ ] Balls are spaced exactly 22 pixels apart (center-to-center)
- [ ] Each ball animates independently through all frames
- [ ] Animation is smooth and continuous at 60 FPS
- [ ] Border matches visual appearance of original XBoing 2.4 screenshots
- [ ] No gaps or overlaps in ball placement
- [ ] Animation starts immediately when bonus screen appears

### Dependencies

- **Prerequisite:** Ball sprite assets loaded and available
- **Prerequisite:** BALL_SLIDES constant defined (number of animation frames)
- **Enables:** Complete visual frame for bonus content

### Implementation Notes

```python
class LevelCompleteView:
    def __init__(self, ...):
        self.border_balls = []
        self._init_border_balls()

    def _init_border_balls(self) -> None:
        """Calculate positions for all border balls."""
        # Top edge
        for x in range(BORDER_LEFT, BORDER_RIGHT + 1, BALL_SPACING):
            self.border_balls.append({'x': x, 'y': BORDER_TOP, 'frame': 0})

        # Bottom edge
        for x in range(BORDER_LEFT, BORDER_RIGHT + 1, BALL_SPACING):
            self.border_balls.append({'x': x, 'y': BORDER_BOTTOM, 'frame': 0})

        # Left edge (excluding corners already covered)
        for y in range(BORDER_TOP + BALL_SPACING, BORDER_BOTTOM, BALL_SPACING):
            self.border_balls.append({'x': BORDER_LEFT, 'y': y, 'frame': 0})

        # Right edge (excluding corners already covered)
        for y in range(BORDER_TOP + BALL_SPACING, BORDER_BOTTOM, BALL_SPACING):
            self.border_balls.append({'x': BORDER_RIGHT, 'y': y, 'frame': 0})

    def update(self, delta_ms: float) -> None:
        # Advance animation frame for each ball
        for ball in self.border_balls:
            ball['frame'] = (ball['frame'] + 1) % BALL_SLIDES

    def draw_ball_border(self, surface: pygame.Surface) -> None:
        for ball in self.border_balls:
            frame_pixmap = self.ball_sprites[ball['frame']]
            surface.blit(frame_pixmap, (ball['x'], ball['y']))
```

### Testing Strategy

1. **Visual Test:** Compare screenshot with original XBoing 2.4 bonus screen
2. **Position Test:** Measure pixel positions of corner balls - should match exactly
3. **Spacing Test:** Verify 22px spacing between all adjacent balls
4. **Animation Test:** Verify each ball cycles through all frames
5. **Performance Test:** Verify smooth animation at 60 FPS with no stutter

---

## Feature 2: Small Title Pixmap

### Original XBoing Behavior

The XBoing logo/title pixmap displays at the top-center of the bonus screen, reinforcing brand identity and providing visual hierarchy. This is the smaller version of the intro screen title.

**Implementation:** `DrawSmallIntroTitle()` function in `bonus.c` lines 235-250

```c
// Draws titleSmall_xpm pixmap centered at top
// Position: (TOTAL_WIDTH/2, 120) = (282, 120)
// Size: 237 x 37 pixels
// Pixmap: titleSmall
```

### Visual Specification

- **Position:** x = 282 (TOTAL_WIDTH // 2), y = 120
- **Size:** 237 x 37 pixels
- **Colors:** From titleSmall.xpm asset
- **Animation:** Static (no animation)
- **Z-Order:** Drawn after ball border, before content text

### Functional Requirements

1. Load titleSmall pixmap asset at initialization
2. Center pixmap horizontally at x = TOTAL_WIDTH // 2
3. Position pixmap at y = 120
4. Draw pixmap on every frame render
5. Handle missing asset gracefully (log warning, continue without)

### Acceptance Criteria

- [ ] Title pixmap displays at exact position (282, 120)
- [ ] Title is horizontally centered on screen
- [ ] Title matches original XBoing logo appearance
- [ ] Title visible throughout bonus screen display
- [ ] No visual glitches or artifacts

### Dependencies

- **Prerequisite:** titleSmall asset file (PNG converted from XPM)
- **Prerequisite:** Asset loading system
- **Enables:** Professional, branded appearance

### Implementation Notes

```python
class LevelCompleteView:
    def __init__(self, asset_loader: AssetLoader, ...):
        try:
            self.small_title = asset_loader.load_image('titleSmall.png')
        except FileNotFoundError:
            logger.warning("titleSmall.png not found, bonus screen will lack title")
            self.small_title = None

    def draw_small_title(self, surface: pygame.Surface) -> None:
        if self.small_title:
            x = SMALL_TITLE_X - (SMALL_TITLE_WIDTH // 2)  # Center horizontally
            y = SMALL_TITLE_Y
            surface.blit(self.small_title, (x, y))
```

**Asset Conversion:** Convert `xboing2.4-clang/bitmaps/titleSmall.xpm` to PNG format

### Testing Strategy

1. **Visual Test:** Compare with original - logo should match exactly
2. **Position Test:** Measure pixel position - should be (282, 120) centered
3. **Missing Asset Test:** Verify graceful handling if file not found

---

## Feature 3: Shadow Text Rendering

### Original XBoing Behavior

All text on the bonus screen renders with a drop shadow effect, creating depth and improving readability against the animated background. Shadow is drawn at offset (+2, +2) in black, then text drawn at (0, 0) in color.

**Implementation:** `DrawShadowCentredText()` function in `misc.c`

```c
// Two-pass rendering:
// 1. Draw text at (x+2, y+2) in black (shadow)
// 2. Draw text at (x, y) in specified color
// Always centered horizontally based on text width
```

### Visual Specification

- **Shadow Offset:** (+2, +2) pixels from text position
- **Shadow Color:** Black (0, 0, 0)
- **Text Position:** Variable based on content
- **Colors:** See per-element specifications below
- **Centering:** Based on TOTAL_WIDTH (565px) for horizontal center

### Functional Requirements

1. Render all text with shadow effect (no exceptions)
2. Shadow offset must be exactly (+2, +2) pixels
3. Shadow color must be pure black (0, 0, 0)
4. Text must be centered on TOTAL_WIDTH, not play window width
5. Shadow must render first (below text layer)
6. Support both centered and left-aligned shadow text

### Acceptance Criteria

- [ ] All text has visible shadow offset by 2px diagonally
- [ ] Shadow is pure black color
- [ ] Text is properly centered on 565px width
- [ ] Shadow does not interfere with text readability
- [ ] Matches original XBoing shadow text appearance

### Dependencies

- **Prerequisite:** Pygame font rendering system
- **Prerequisite:** TOTAL_WIDTH constant defined
- **Enables:** Professional text appearance with depth

### Implementation Notes

```python
def draw_shadow_text(
    surface: pygame.Surface,
    text: str,
    x: int,
    y: int,
    font: pygame.font.Font,
    color: Tuple[int, int, int]
) -> None:
    """Draw text with drop shadow effect."""
    shadow_color = (0, 0, 0)

    # Render shadow
    shadow_surface = font.render(text, True, shadow_color)
    surface.blit(shadow_surface, (x + 2, y + 2))

    # Render text
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, (x, y))

def draw_shadow_centered_text(
    surface: pygame.Surface,
    text: str,
    y: int,
    font: pygame.font.Font,
    color: Tuple[int, int, int],
    width: int = TOTAL_WIDTH
) -> None:
    """Draw centered text with shadow."""
    text_surface = font.render(text, True, color)
    text_width = text_surface.get_width()
    x = (width - text_width) // 2
    draw_shadow_text(surface, text, x, y, font, color)
```

### Testing Strategy

1. **Visual Test:** Verify shadow visible on all text elements
2. **Offset Test:** Measure shadow offset - should be exactly (+2, +2)
3. **Color Test:** Verify shadow is pure black (0, 0, 0)
4. **Centering Test:** Verify text centered on 565px, not 495px

---

## Feature 4: Dynamic Y-Positioning

### Original XBoing Behavior

The bonus screen calculates text positions dynamically based on font metrics (ascent) and a fixed spacing constant (GAP = 30). This ensures proper spacing regardless of font size and allows content to flow naturally.

**Implementation:** Throughout `bonus.c`, pattern:
```c
ypos += (font->ascent + GAP);        // Normal spacing
ypos += (font->ascent + GAP * 1.5);  // 1.5x spacing
ypos += (font->ascent + GAP * 2);    // 2x spacing
```

Starting position: `ypos = 180` (line 903)

### Visual Specification

- **Initial Y:** 180 pixels from top
- **Increment:** `font.get_ascent() + GAP` where GAP = 30
- **Multipliers:** 1.0x, 1.5x, 2.0x based on content spacing needs
- **Final Position:** Calculated dynamically, never exceeds 600px

### Functional Requirements

1. Initialize ypos = INITIAL_YPOS (180) at start of bonus screen
2. After drawing each element, increment ypos by font ascent + GAP × multiplier
3. Multiplier values:
   - After title: 1.0x (font.ascent + 30)
   - After congratulations: 1.0x
   - After coin section: 1.5x (font.ascent + 45)
   - After level bonus: 1.5x
   - After bullets: 0.5x (font.ascent + 15)
   - After time bonus: 0.5x
   - After ranking: 0.5x
4. Each element draws at current ypos before incrementing
5. Press space message uses fixed position PRESS_SPACE_Y (568)

### Acceptance Criteria

- [ ] No hardcoded y-position array
- [ ] Spacing adjusts if font size changes
- [ ] Elements never overlap
- [ ] Spacing matches original visual appearance
- [ ] Press space message at exact y=568

### Dependencies

- **Prerequisite:** Font loading system with ascent metrics
- **Prerequisite:** GAP constant defined
- **Enables:** Font-independent layout, easier maintenance

### Implementation Notes

```python
class LevelCompleteView:
    def render_bonus_screen(self, surface: pygame.Surface) -> None:
        ypos = INITIAL_YPOS

        # Draw title
        self.draw_shadow_centered_text(surface, f"- Level {level} -", ypos,
                                       title_font, RED)
        ypos += title_font.get_ascent() + GAP

        # Draw congratulations
        self.draw_shadow_centered_text(surface, "Congratulations...", ypos,
                                       text_font, WHITE)
        ypos += text_font.get_ascent() + GAP

        # Draw coins (if any)
        if has_coins:
            self.draw_coin_section(surface, ypos)
            ypos += text_font.get_ascent() + int(GAP * 1.5)

        # Continue pattern...
```

### Testing Strategy

1. **Visual Test:** Compare element spacing with original screenshot
2. **Font Change Test:** Change font size, verify no overlaps
3. **Gap Test:** Measure spacing between elements - should match calculated values

---

## Feature 5: Frame-Based Timing System

### Original XBoing Behavior

The original bonus screen uses frame-based delays (counting frames at ~60 FPS) rather than millisecond timers. This ensures consistent timing across different system speeds and matches the arcade feel of the original game.

**Implementation:** `LINE_DELAY` constant = 100 frames throughout `bonus.c`

```c
#define LINE_DELAY 100  // Standard delay between states

// State transitions wait for frame counter:
if (frame > LINE_DELAY) {
    BonusState = NEXT_STATE;
}
```

**Timing Conversions** (at 60 FPS):
- 5 frames = ~83ms
- 100 frames = ~1666ms (1.67 seconds)
- 200 frames = ~3333ms (3.33 seconds)

### Visual Specification

N/A - This is a timing/behavior feature

### Functional Requirements

1. Maintain frame counter that increments each update cycle (assuming 60 FPS)
2. Replace all millisecond-based delays with frame-based delays
3. State transition delays:
   - BONUS_TEXT → BONUS_SCORE: 5 frames (~83ms)
   - BONUS_SCORE → BONUS_BONUS: 100 frames (~1666ms)
   - BONUS_BONUS → BONUS_LEVEL: 100 frames
   - BONUS_LEVEL → BONUS_BULLET: 100 frames
   - BONUS_BULLET → BONUS_TIME: 100 frames
   - BONUS_TIME → BONUS_HSCORE: 100 frames
   - BONUS_HSCORE → BONUS_END_TEXT: 100 frames
   - BONUS_END_TEXT → BONUS_FINISH: 200 frames (~3333ms)
4. Calculate frames from delta_ms: `frames_elapsed = (delta_ms / 1000.0) * 60.0`
5. Accumulate fractional frames for accuracy

### Acceptance Criteria

- [ ] All delays converted from milliseconds to frames
- [ ] Timing matches original feel (not too fast/slow)
- [ ] State transitions occur at correct frame counts
- [ ] No timing drift over extended display
- [ ] Consistent timing regardless of system performance

### Dependencies

- **Prerequisite:** Update cycle running at stable rate
- **Prerequisite:** Accurate delta_ms from game loop
- **Enables:** Authentic arcade timing feel

### Implementation Notes

```python
class LevelCompleteView:
    def __init__(self, ...):
        self.frame_counter = 0.0  # Use float for accuracy
        self.wait_until_frame = 0.0
        self.current_state = BonusState.BONUS_TEXT

    def update(self, delta_ms: float) -> None:
        # Convert milliseconds to frames (at 60 FPS)
        frames_elapsed = (delta_ms / 1000.0) * 60.0
        self.frame_counter += frames_elapsed

        if self.current_state == BonusState.BONUS_WAIT:
            if self.frame_counter >= self.wait_until_frame:
                self.current_state = self.next_state
                self.frame_counter = 0.0
        else:
            self._process_current_state()

    def transition_after_delay(self, next_state: BonusState,
                              delay_frames: int) -> None:
        self.next_state = next_state
        self.wait_until_frame = delay_frames
        self.current_state = BonusState.BONUS_WAIT
        self.frame_counter = 0.0
```

### Testing Strategy

1. **Timing Test:** Measure actual time between state transitions
2. **Feel Test:** Compare with original - should feel identical pace
3. **Drift Test:** Display bonus screen 10 times, verify consistent timing
4. **Frame Rate Test:** Test at different frame rates, verify correct scaling

---

## Feature 6: State Machine with Skip Logic

### Original XBoing Behavior

The bonus screen implements a state machine that conditionally skips states based on game conditions (no coins, timer expired, super bonus, etc.). This ensures only relevant content displays and provides appropriate feedback for different outcomes.

**Implementation:** `enum BonusStates` in `bonus.h` lines 35-46, state handlers throughout `bonus.c`

**State Flow:**
```
BONUS_TEXT
  ↓ (5 frames)
BONUS_SCORE
  ↓ (100 frames)
BONUS_BONUS → [skip if no coins / timer out / super bonus]
  ↓ (100 frames)
BONUS_LEVEL → [skip if timer out]
  ↓ (100 frames)
BONUS_BULLET → [skip if no bullets]
  ↓ (100 frames)
BONUS_TIME
  ↓ (100 frames)
BONUS_HSCORE
  ↓ (100 frames)
BONUS_END_TEXT
  ↓ (200 frames)
BONUS_FINISH
```

### Visual Specification

N/A - This is a behavior/logic feature

### Functional Requirements

1. Implement 10 bonus screen states: TEXT, SCORE, BONUS, LEVEL, BULLET, TIME, HSCORE, END_TEXT, WAIT, FINISH
2. BONUS_WAIT state pauses between other states for timing
3. Conditional transitions:
   - **BONUS_BONUS state:**
     - If timer = 0: Show "Bonus coins void - Timer ran out!" in BLUE, play "Doh4", skip to BONUS_LEVEL
     - If numCoins = 0: Show "Sorry, no bonus coins collected." in BLUE, play "Doh1", skip to BONUS_LEVEL
     - If numCoins > MAX_BONUS_COINS (8): Show "Super Bonus - 50000" in BLUE with titleFont, play "supbons", add 50k points, skip to BONUS_LEVEL
     - Otherwise: Animate each coin, add 3000 points each, play "bonus" sound
   - **BONUS_LEVEL state:**
     - If timer = 0: Show "No level bonus - Timer ran out." in YELLOW, play "Doh2"
     - Otherwise: Show "Level bonus - level X x 100 = Y points" in YELLOW, add bonus
   - **BONUS_BULLET state:**
     - If numBullets = 0: Show "You have used all your bullets. No bonus!" in BLUE, play "Doh3", skip to BONUS_TIME
     - Otherwise: Animate each bullet, add 500 points each, play "key" sound (volume 50)
   - **BONUS_TIME state:**
     - If timer = 0: Show "No time bonus - not quick enough!" in YELLOW, play "Doh4"
     - Otherwise: Show "Time bonus - X seconds x 100 = Y points" in YELLOW, add bonus
   - **BONUS_HSCORE state:**
     - If rank > 0: Show "You are ranked Xth. Well done!" in RED
     - Otherwise: Show "Keep on trying!" in RED
4. Each state handler draws appropriate content and decides next state
5. State transitions always go through BONUS_WAIT for timing

### Acceptance Criteria

- [ ] State machine implements all 10 states correctly
- [ ] Conditional skips work for all scenarios
- [ ] Appropriate messages display for each condition
- [ ] Correct sounds play for each outcome
- [ ] Score updates correctly in real-time
- [ ] No states display that should be skipped
- [ ] State transitions respect frame-based delays

### Dependencies

- **Prerequisite:** Frame-based timing system
- **Prerequisite:** Game state access (coins, bullets, timer, score)
- **Prerequisite:** Sound system
- **Enables:** Dynamic, condition-appropriate bonus display

### Implementation Notes

```python
class BonusState(Enum):
    BONUS_TEXT = "text"
    BONUS_SCORE = "score"
    BONUS_BONUS = "bonus"
    BONUS_LEVEL = "level"
    BONUS_BULLET = "bullet"
    BONUS_TIME = "time"
    BONUS_HSCORE = "hscore"
    BONUS_END_TEXT = "end_text"
    BONUS_WAIT = "wait"
    BONUS_FINISH = "finish"

class LevelCompleteView:
    def _process_bonus_bonus_state(self) -> None:
        """Handle coin bonus state with conditional logic."""
        if self.game_state.timer_seconds == 0:
            self.show_message("Bonus coins void - Timer ran out!", BLUE)
            self.play_sound("Doh4", volume=80)
            self.transition_after_delay(BonusState.BONUS_LEVEL, LINE_DELAY)
        elif self.game_state.num_coins == 0:
            self.show_message("Sorry, no bonus coins collected.", BLUE)
            self.play_sound("Doh1", volume=80)
            self.transition_after_delay(BonusState.BONUS_LEVEL, LINE_DELAY)
        elif self.game_state.num_coins > MAX_BONUS_COINS:
            self.show_message("Super Bonus - 50000", BLUE, title_font)
            self.play_sound("supbons", volume=80)
            self.add_score(SUPER_BONUS_SCORE)
            self.transition_after_delay(BonusState.BONUS_LEVEL, LINE_DELAY)
        else:
            self.start_coin_animation()

    # Similar handlers for other states...
```

### Testing Strategy

1. **No Coins Test:** Complete level with 0 coins, verify skip logic and message
2. **Timer Expired Test:** Let timer run out, verify all timeout messages
3. **Super Bonus Test:** Collect >8 coins, verify super bonus display
4. **No Bullets Test:** Use all bullets, verify skip logic and message
5. **Full Bonus Test:** Complete with all bonuses, verify all sections display
6. **Ranking Test:** Test with different scores for different ranking messages

---

## Feature 7: Real-Time Score Updates

### Original XBoing Behavior

As each bonus is awarded (coins, bullets, level, time), the score display updates immediately and visibly. This provides real-time feedback and creates satisfying reward moments during the bonus sequence.

**Implementation:** `DisplayScore(score)` called after each bonus addition throughout `bonus.c` (lines 411, 426, 441, 488, 536, 564, 606)

### Visual Specification

N/A - This is a behavior feature affecting score display

### Functional Requirements

1. Update displayed score immediately after adding each bonus:
   - After each coin awarded (every 3000 points)
   - After super bonus awarded (50000 points)
   - After level bonus calculated (level × 100)
   - After each bullet awarded (every 500 points)
   - After time bonus calculated (seconds × 100)
2. Score display must refresh/redraw to show new value
3. No delay between bonus addition and score update
4. Score updates visible during animation sequences
5. Final score reflects all bonuses at end of sequence

### Acceptance Criteria

- [ ] Score updates visible during coin animation (not after)
- [ ] Score updates visible during bullet animation (not after)
- [ ] Each bonus addition immediately reflected in score display
- [ ] Player can watch score incrementally increase
- [ ] Final score matches sum of all bonuses
- [ ] Score display refreshes smoothly without flicker

### Dependencies

- **Prerequisite:** Score display component accessible from view
- **Prerequisite:** Real-time rendering system
- **Enables:** Satisfying reward feedback, arcade feel

### Implementation Notes

```python
class LevelCompleteView:
    def add_score_and_update_display(self, points: int) -> None:
        """Add points to score and immediately update display."""
        self.game_state.add_score(points)
        # Trigger immediate score display refresh
        self.score_display.update_score(self.game_state.score)

    def animate_coins(self) -> None:
        """Animate coins with real-time score updates."""
        for _ in range(self.game_state.num_coins):
            self.draw_next_coin()
            self.add_score_and_update_display(BONUS_COIN_SCORE)
            self.play_sound("bonus", volume=50)
            yield  # Return control for frame rendering

    def animate_bullets(self) -> None:
        """Animate bullets with real-time score updates."""
        for _ in range(self.game_state.num_bullets):
            self.draw_next_bullet()
            self.add_score_and_update_display(BULLET_SCORE)
            self.play_sound("key", volume=50)
            yield  # Return control for frame rendering
```

**Note:** Consider coroutine or generator pattern to yield control between bonus additions for smooth rendering.

### Testing Strategy

1. **Visual Test:** Watch score display during coin animation - should increment
2. **Timing Test:** Verify score updates immediately, not at end of animation
3. **Accuracy Test:** Verify final score equals starting score + all bonuses
4. **Display Test:** Verify score display doesn't flicker or glitch during updates

---

## Feature 8: Floppy Disk Save Icon

### Original XBoing Behavior

On levels that are multiples of 5 (save levels), a floppy disk icon displays in the bottom-right corner, indicating that the player's progress can be saved at this point.

**Implementation:** `bonus.c` lines 299-308

```c
if (((level - GetStartingLevel() + 1) % SAVE_LEVEL) == 0) {
    RenderShape(display, bonusWindow, floppy,
                TOTAL_WIDTH - 100, PLAY_HEIGHT,
                32, 32, False);
}
```

### Visual Specification

- **Position:** x = 465 (TOTAL_WIDTH - 100), y = 580 (PLAY_HEIGHT)
- **Size:** 32 x 32 pixels
- **Asset:** floppy.xpm (floppy disk icon)
- **Color:** From pixmap asset
- **Display Condition:** Only on levels where (level % 5) == 0
- **Z-Order:** Drawn with text elements (mid-layer)

### Functional Requirements

1. Calculate adjusted level: `adjusted_level = current_level - starting_level + 1`
2. Check if `adjusted_level % SAVE_LEVEL_INTERVAL == 0`
3. If true, load and draw floppy icon at (465, 580)
4. Icon displays throughout bonus screen
5. Icon does not display on non-save levels

### Acceptance Criteria

- [ ] Icon appears on levels 5, 10, 15, 20, etc.
- [ ] Icon does not appear on levels 1-4, 6-9, 11-14, etc.
- [ ] Icon position exactly (465, 580)
- [ ] Icon size exactly 32x32 pixels
- [ ] Icon matches original floppy disk appearance

### Dependencies

- **Prerequisite:** floppy.xpm asset converted to PNG
- **Prerequisite:** Level tracking system
- **Prerequisite:** Starting level configuration
- **Enables:** Save feature visibility

### Implementation Notes

```python
class LevelCompleteView:
    def __init__(self, asset_loader: AssetLoader, ...):
        try:
            self.floppy_icon = asset_loader.load_image('floppy.png')
        except FileNotFoundError:
            logger.warning("floppy.png not found")
            self.floppy_icon = None

    def is_save_level(self) -> bool:
        """Check if current level is a save level."""
        adjusted_level = (self.game_state.level -
                         self.game_state.starting_level + 1)
        return (adjusted_level % SAVE_LEVEL_INTERVAL) == 0

    def draw_floppy_icon(self, surface: pygame.Surface) -> None:
        if self.floppy_icon and self.is_save_level():
            surface.blit(self.floppy_icon, (FLOPPY_ICON_X, FLOPPY_ICON_Y))
```

**Asset Conversion:** Convert `xboing2.4-clang/bitmaps/floppy.xpm` to PNG format

### Testing Strategy

1. **Level Test:** Test levels 1-20, verify icon only on 5, 10, 15, 20
2. **Position Test:** Measure icon position - should be (465, 580)
3. **Size Test:** Verify icon is 32x32 pixels
4. **Visual Test:** Compare with original appearance

---

## Implementation Approach

### Phase 1: Foundation (Week 1, Days 1-3)
**Goal:** Establish core infrastructure for pixel-perfect rendering

**Tasks:**
1. Add all configuration constants to codebase
2. Implement shadow text rendering utilities
3. Implement dynamic y-positioning system
4. Adjust horizontal centering to TOTAL_WIDTH
5. Convert titleSmall.xpm and floppy.xpm assets to PNG

**Acceptance:** Text renders with shadows, positions calculate dynamically

### Phase 2: Visual Elements (Week 1-2, Days 4-7)
**Goal:** Add major missing visual components

**Tasks:**
6. Implement ball border rendering system
7. Add ball border animation logic
8. Add small title pixmap display
9. Add floppy disk icon for save levels
10. Verify all visual elements position correctly

**Acceptance:** Screen has animated border, title pixmap, and save icon

### Phase 3: State Machine (Week 2, Days 8-11)
**Goal:** Implement conditional display logic

**Tasks:**
11. Refactor to state machine architecture (10 states)
12. Implement skip logic for all conditions
13. Add conditional messages (timer out, no coins, etc.)
14. Implement super bonus special handling
15. Test all conditional paths thoroughly

**Acceptance:** Bonus screen shows correct content based on game state

### Phase 4: Timing & Score (Week 2-3, Days 12-14)
**Goal:** Match original timing and feedback feel

**Tasks:**
16. Convert all delays to frame-based timing
17. Implement real-time score updates during animation
18. Adjust all state transition timings
19. Test and tune timing to match original feel

**Acceptance:** Timing matches original, score updates in real-time

### Phase 5: Polish & Validation (Week 3, Days 15-18)
**Goal:** Achieve pixel-perfect fidelity

**Tasks:**
20. Visual comparison testing with original screenshots
21. Audio volume adjustments
22. Font metric fine-tuning
23. Performance optimization
24. Final bug fixes and edge case handling

**Acceptance:** All tests pass, matches original appearance and behavior

---

## Testing Requirements

### Visual Regression Testing
1. Capture screenshots of bonus screen with original XBoing 2.4
2. Capture screenshots of Python implementation
3. Overlay and diff images - zero pixel differences (except unavoidable font variations)
4. Test all conditional states (8 screenshots minimum)

### Functional Test Matrix

| Test Case | Coins | Timer | Bullets | Expected Display | Expected Sounds |
|-----------|-------|-------|---------|------------------|-----------------|
| Full Bonus | 5 | Active | 10 | All sections animate | bonus, key, applause |
| No Coins | 0 | Active | 10 | "Sorry, no bonus..." | Doh1, key, applause |
| Timer Out | 5 | 0 | 10 | "Timer ran out" x3 | Doh4, Doh2, Doh4 |
| Super Bonus | 10 | Active | 10 | "Super Bonus - 50000" | supbons, key, applause |
| No Bullets | 5 | Active | 0 | Coin section, "No bullets" | bonus, Doh3, applause |
| Full Timeout | 0 | 0 | 0 | All timeout messages | Doh1, Doh4, Doh2, Doh3, Doh4 |
| Save Level (5) | 3 | Active | 5 | Floppy icon visible | bonus, key, applause |
| Non-Save (4) | 3 | Active | 5 | No floppy icon | bonus, key, applause |

### Timing Validation Tests
1. Measure time from screen start to first text: Should be ~83ms (5 frames)
2. Measure time between state transitions: Should be ~1666ms (100 frames)
3. Measure total bonus screen duration: Should match original feel
4. Verify animations don't speed up/slow down over time

### Audio Tests
1. Verify correct sound plays for each event
2. Verify sound volumes match specifications:
   - bonus: volume 50
   - key: volume 50
   - Doh1-4: volume 80
   - supbons: volume 80
   - applause: volume 80

### Performance Tests
1. Verify 60 FPS maintained throughout bonus screen
2. Verify no frame drops during animations
3. Verify memory stable (no leaks during repeated bonus screens)

---

## Open Questions

1. **Ball Animation Frames:** How many BALL_SLIDES frames exist in the ball sprite sequence? (Need to count frames in ball.xpm or similar)

2. **Font Metrics:** What are exact ascent/descent values for original X11 fonts? May need to measure from screenshots or test multiple font sizes.

3. **Window Fade Algorithm:** What is exact implementation of `WindowFadeEffect()`? Need to study stage.c or implement similar visual effect.

4. **Actual Frame Rate:** Is original XBoing exactly 60 FPS or variable? May affect timing conversions.

5. **Asset Availability:** Are all required assets (titleSmall.xpm, floppy.xpm) present in xboing2.4-clang/bitmaps/ directory?

---

## Success Criteria

**Definition of Done:**
- All Priority 1 features implemented and tested
- Visual comparison tests show <1% pixel difference (accounting for font variations)
- All functional test matrix cases pass
- Timing matches original feel (validated by manual comparison)
- All audio cues correct and at proper volumes
- 60 FPS maintained throughout bonus screen
- Code passes all quality checks (lint, type, test)
- Zero known bugs or regressions

**User Experience Goal:**
A player familiar with original XBoing should not be able to distinguish the Python implementation from the original based on the bonus screen alone.
