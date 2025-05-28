# XBoing Python Welcome Screen Design & Requirements

## Overview

The Welcome screen is a heavily animated, non-interactive introduction shown only once at game launch. It features a single background with a picture of the planet Earth, an Australian flag, and a sequence of animated text and images, all accompanied by sound effects. The animation sequence is inspired by the original C implementation in `presents.c`.

## Animation Sequence

The Welcome screen proceeds through the following animated stages:

1. **Background and Flag**
    - The background is displayed, featuring a large image of the planet Earth.
    - The Australian flag is shown at the top of the screen.
    - The text "Made in Australia" is displayed below the flag.
    - A copyright message is shown at the bottom.
    - Sound: Intro sound effect ("intro").

2. **Animated Text: Author Credits**
    - Three large text images are animated in sequence:
        1. "Justin" (bitmap/png)
        2. "Kibell" (bitmap/png)
        3. "Presents" (bitmap/png)
    - Each appears with a short delay and may fade in or slide in.
    - Sound: None or subtle effect.

3. **Animated Title: X B O I N G II**
    - The letters "X B O I N G" are displayed one at a time, each as a large PNG image, spaced across the screen.
    - After all letters are shown, the "I" is duplicated to form "II" (the sequel indicator), animated below the main title.
    - Sound: "stamp" sound effect for each letter.
    - After the title is complete, a sparkle animation appears on the "G" (animated star/sparkle PNG sequence, with a "ping" sound).

4. **Animated Welcome Messages**
    - Three lines of text are animated, with each letter appearing one at a time:
        1. `Welcome <player>, prepare for battle.` (player name or system user)
        2. `The future of the planet Earth is in your hands!`
        3. `More instructions will follow within game zone - out.`
    - Each line is centered and appears below the title, with a short delay between lines.
    - Sound: "key" sound effect for each letter.

5. **Screen Clear Animation**
    - The screen is cleared with a vertical wipe (lines/rectangles from top and bottom toward the center), with a "whoosh" sound.

6. **Transition to Game**
    - After the animation completes (or if the user presses space), the game transitions to the main intro/game view.

## Asset Requirements

- **Background image**: Large PNG of the planet Earth.
- **Australian flag**: PNG image.
- **Text images**: PNGs for "Justin", "Kibell", "Presents".
- **Title letters**: PNGs for each of X, B, O, I, N, G (and I for II).
- **Sparkle animation**: Sequence of PNGs for the sparkle effect.
- **Fonts**: For animated text lines (should match or closely resemble the original).
- **Sound effects**: "intro", "stamp", "ping", "key", "whoosh".

## Animation & Timing

- Each stage and sub-step has a specific delay, closely following the original C implementation (see below for details).
- Letter-by-letter text animation should have a short delay per letter (e.g., 30 ms).
- All animations should be interruptible by pressing space, which immediately transitions to the game.
- All sound effects should be synchronized with their respective animations.

### Detailed Timing and Sound Triggers

1. **Background and Flag**
    - Show flag and "Made in Australia" text: **800 ms**
    - Play "intro" sound at the start of this stage.

2. **Animated Text: Author Credits**
    - Show "Justin": **300 ms** after previous step
    - Show "Kibell": **500 ms** after "Justin"
    - Show "Presents": **750 ms** after "Kibell"
    - (No sound for these steps in the original, but subtle fade/slide-in is allowed)

3. **Animated Title: X B O I N G II**
    - Each letter (X, B, O, I, N, G) appears one at a time, spaced by **300 ms** per letter.
    - For each letter, play the "stamp" sound effect.
    - After all letters, wait **200 ms** and then show the two "I" letters for "II" (sequel indicator), with the same "stamp" sound for each.
    - After the title is complete, wait **200 ms** and then play the sparkle animation on the "G" (sequence of 11 frames, **35 ms** per frame, total ~385 ms), with a "ping" sound at the start.

4. **Animated Welcome Messages**
    - For each line:
        - Animate each letter with a **30 ms** delay per letter.
        - Play the "key" sound for each letter as it appears.
        - After the line is complete, wait **700 ms** before starting the next line.
    - Three lines in total:
        1. `Welcome <player>, prepare for battle.`
        2. `The future of the planet Earth is in your hands!`
        3. `More instructions will follow within game zone - out.`

5. **Screen Clear Animation**
    - Vertical wipe clears the screen from top and bottom toward the center, in **10 px** steps every **20 ms**.
    - Play the "whoosh" sound at the start of the wipe.
    - Total duration depends on screen height, but typically ~500 ms.

6. **Transition to Game**
    - After the animation completes, or if the user presses space at any time, immediately transition to the main game view.

## User Interaction

- The Welcome screen is non-interactive except for the ability to skip the animation by pressing space.
- After the Welcome screen, it cannot be shown again in the same session.

## Implementation Notes

- Use a state machine or sequence of timed steps to manage the animation flow.
- Use Pygame surfaces for images and text, and Pygame's event/timer system for animation timing.
- Ensure all assets are preloaded for smooth animation.
- The Welcome screen should be implemented as a dedicated view class, managed by the UIManager.
- The animation sequence and timing should be faithful to the original C version, but may be tuned for smoothness and modern display rates.

## References

- Original C implementation: `xboing2.4-clang/presents.c`
- Asset sources: `src/xboing/assets/images/presents/`, `src/xboing/assets/images/earth.png`, etc.
- Sound sources: `src/xboing/assets/sounds/`

---

This design ensures the Welcome screen is a visually engaging, faithful recreation of the original, and provides a memorable introduction to XBoing Python. 