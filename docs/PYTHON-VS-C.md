# Gap Analysis: xboing-python vs xboing-c

## Repositories

- **xboing-python**: https://github.com/jmf-pobox/xboing-python (Python 3.10+ / pygame)
- **xboing-c**: https://github.com/jmf-pobox/xboing-c (C11 / SDL2)

Both are ports of the original XBoing (1993, Justin C. Kibell, X11/Xlib).

## Overview

This document compares the Python/pygame port against the C/SDL2 port to
identify what the Python version is missing.

**Estimated completeness: 35-40%** of the C version's feature set.

The Python port has core gameplay working (paddle, ball, blocks, collisions,
bullets, level loading) and shares the same 80 levels and audio assets. The
gaps are primarily in game screens, block effect logic, visual effects,
persistence, and scoring depth.

## Codebase Metrics

| Metric | xboing-c | xboing-python |
|--------|----------|---------------|
| Source lines | 23,332 (43 .c files) | 12,372 (82 .py files) |
| Test lines | 25,442 (59 test files) | 5,674 (40 test files) |
| Test functions | 1,115 | 202 |
| Test:source ratio | 1.09:1 | 0.46:1 |
| Fuzz targets | 4 (config, highscore, level, savegame) | 0 |
| Golden screenshot tests | Yes (presents, intro, highscore, etc.) | No |
| Level files | 80 | 80 |
| Sound files | 46 | 47 |

## Feature Matrix

### Game Screens / Modes

The C version has 16 game modes with enter/exit callbacks and function-pointer
dispatch. The Python version has 4.

| Screen | xboing-c | xboing-python | Status |
|--------|----------|---------------|--------|
| Gameplay | `game_rules.c`, `game_render.c` | `game_controller.py`, `game_view.py` | Present |
| Level Complete / Bonus | `bonus_system.c` (10-state tally) | `level_complete_view.py` (10-state machine) | Present |
| Game Over | `game_modes.c` | `game_over_view.py` | Present |
| Instructions | `intro_system.c` INSTRUCT mode | `instructions_view.py` | Present |
| Presents/Splash | `presents_system.c` (14-state sequencer: flag, earth, letters, sparkle, typewriter) | Assets present, no screen | **Missing** |
| Intro (block descriptions) | `intro_system.c` (22 block entries, sparkle animations) | Not implemented | **Missing** |
| Demo / Attract | `demo_system.c` (ball-trail animation, text) | Not implemented | **Missing** |
| Level Preview | `demo_system.c` PREVIEW mode | Not implemented | **Missing** |
| Key Bindings | `keys_system.c` (game + editor bindings) | Not implemented | **Missing** |
| High Score Display | `highscore_system.c` (10-entry table, sparkle row-walk) | Not implemented | **Missing** |
| Dialogue (modal input) | `dialogue_system.c` (text input with validation) | Not implemented | **Missing** |
| Level Editor | `editor_system.c` (draw, palette, grid transforms, save/load, play-test) | Not implemented | **Missing** |
| Pause Overlay | `sdl2_state.c` SDL2ST_PAUSE | Basic toggle via input controller, no overlay | **Partial** |

### Block Types

Both codebases define 30 block types. The C version implements behavior for all
30. The Python version has working behavior for ~12.

| Block Type | xboing-c | xboing-python | Status |
|------------|----------|---------------|--------|
| Standard colors (RED-PURPLE) | Full | Full | Present |
| BULLET_BLK (ammo pickup) | Full | Full | Present |
| BLACK_BLK (indestructible) | Full (cooldown timer, hit animation) | Basic handling | Partial |
| COUNTER_BLK (multi-hit, 5 slides) | Full with decrement display | Defined, limited implementation | Partial |
| BOMB_BLK (explosion chain) | Full with neighbor explosion | `PowerUpManager.activate_bomb()` | Partial |
| DEATH_BLK (lose life) | Full | Defined, effect unclear | Partial |
| REVERSE_BLK | Full | `PowerUpManager` | Present |
| STICKY_BLK | Full | `PowerUpManager` | Present |
| PAD_SHRINK_BLK / PAD_EXPAND_BLK | Full | `PowerUpManager` | Present |
| HYPERSPACE_BLK (teleport) | Full random teleport | Defined, no teleport logic | **Missing** |
| MGUN_BLK (machine gun) | Full fast-gun activation | Defined only | **Missing** |
| WALLOFF_BLK (disable walls) | Full with border color change | Defined only | **Missing** |
| MULTIBALL_BLK | Full with ball splitting | Defined only | **Missing** |
| EXTRABALL_BLK | Full with spawn | Defined only | **Missing** |
| DROP_BLK (falling, hit-points) | Full with counter overlay | Defined only | **Missing** |
| MAXAMMO_BLK (max ammo refill) | Full | Defined only | **Missing** |
| ROAMER_BLK (moving block) | Full with movement AI | Stub fields only | **Missing** |
| TIMER_BLK (add time) | Full (+20s) | Defined only | **Missing** |
| RANDOM_BLK (morph to another type) | Full | Defined only | **Missing** |
| DYNAMITE_BLK (destroy all blocks) | Full | Defined only | **Missing** |
| BONUSX2_BLK / BONUSX4_BLK | Full with mutual exclusion | Defined only | **Missing** |
| BONUS_BLK (bonus coin) | Full with coin counting | Partial | Partial |
| BLACKHIT_BLK | Full | Defined only | **Missing** |

### Gameplay Systems

| System | xboing-c | xboing-python | Status |
|--------|----------|---------------|--------|
| Ball physics (angle, speed) | Mass, 14-zone paddle collision, tilt mechanic | Basic angle from paddle offset, random perturbation | Partial |
| Multiple balls (MAX_BALLS=5) | Full with multiball spawn, pop animation | `BallManager` supports multiple balls | Present |
| Ball birth animation (8 frames) | Full | Full | Present |
| Ball animation (4-5 sprites) | Full | Full | Present |
| Bullet/gun system | 40 slots, tink effects, fast gun dual-fire, unlimited mode | Basic `BulletManager`, firing + block collision | Partial |
| Tilt mechanic | 3 tilts, auto-launch stuck balls | Auto-launch timer only | Partial |
| EyeDude character | Full: walk, turn, die, collision, 10K bonus | Not implemented | **Missing** |
| Render interpolation | Full `render_alpha` for sub-frame smoothing | Not implemented | **Missing** |

### Specials / Power-ups

The C version has 8 specials with a panel display, mutual exclusion, and
attract-mode randomization (`special_system.c`).

| Special | xboing-c | xboing-python | Status |
|---------|----------|---------------|--------|
| Reverse | Full | `PowerUpManager` | Present |
| Sticky | Full | `PowerUpManager` | Present |
| Saving (extra life) | Full | Not implemented | **Missing** |
| Fast Gun (dual-fire) | Full | Not implemented | **Missing** |
| No Wall (disable bottom) | Full | Not implemented | **Missing** |
| Killer (instant destroy) | Full | Not implemented | **Missing** |
| x2 (score multiplier) | Full | Not implemented | **Missing** |
| x4 (score multiplier) | Full | Not implemented | **Missing** |
| Specials display panel | Full 2-row, 4-column layout | `special_display.py` exists | Partial |

### Visual Effects

The C version has a complete SFX system (`sfx_system.c`) with 5 screen
transition effects, border glow cycling, and devil eyes animation. The Python
version has none.

| Effect | xboing-c | xboing-python | Status |
|--------|----------|---------------|--------|
| Screen shake | Full | Not implemented | **Missing** |
| Screen fade (13-step grid) | Full | Not implemented | **Missing** |
| Blind reveal (column strips) | Full | Not implemented | **Missing** |
| Screen shatter (10x10 tile scatter) | Full | Not implemented | **Missing** |
| Static effect | Full | Not implemented | **Missing** |
| Border glow cycling (7-step) | Full | Not implemented | **Missing** |
| Devil eyes blink (26-step, 6 sprites) | Full | Eye images in assets, no system | **Missing** |
| Sparkle animations | Full (used in 5+ screens) | Not implemented | **Missing** |
| Block explosion animation | Full with per-frame progression | Basic explosion frames defined | Partial |

### Scoring

| Feature | xboing-c | xboing-python | Status |
|---------|----------|---------------|--------|
| Basic scoring | Full | `GameState.add_score()` | Present |
| Score multiplier (x2, x4) | Full with callback notification | No multiplier support | **Missing** |
| Extra life at score thresholds | Full | Not implemented | **Missing** |
| Per-block point values | Full via `score_logic.c` | From `block_types.json` | Present |
| Digit rendering (right-aligned) | Full | `DigitRenderer` | Present |

### Persistence

The C version has 3 persistence systems. The Python version has none.

| System | xboing-c | xboing-python | Status |
|--------|----------|---------------|--------|
| Save/load game state | JSON-based (`savegame_io.c`), version 2 format | Not implemented | **Missing** |
| High score file I/O | File locking, global+personal tables (`highscore_io.c`) | Not implemented | **Missing** |
| Configuration persistence | JSON config (`config_io.c`) | Not implemented | **Missing** |
| XDG path resolution | Full `paths_config_t` with data/config/state dirs | Not implemented | **Missing** |

### Input

| Feature | xboing-c | xboing-python | Status |
|---------|----------|---------------|--------|
| Keyboard controls | Full | Full | Present |
| Mouse controls | Full with reverse-aware mirroring | Full with reverse | Present |
| CLI options | Full: start level, sound, verbose, sfx, version | Not implemented | **Missing** |

### Level System

| Feature | xboing-c | xboing-python | Status |
|---------|----------|---------------|--------|
| 80 levels | Full | Full | Present |
| Level loading/parsing | Full (`level_system.c`) | `LevelManager` | Present |
| Level wrapping (1..80 cycle) | Full | Not verified | Unknown |
| Background cycling (4 backgrounds) | Full | Background images present | Partial |

## Gap Summary

### Fully missing systems (no implementation at all)

1. **12 game screens** — presents, intro, demo, preview, keys, highscore,
   dialogue, editor, and their state machines
2. **Visual effects system** — all 5 transition effects, border glow, devil
   eyes, sparkle
3. **Persistence** — save/load, high scores, config
4. **EyeDude character** — walking bonus character
5. **CLI options** — start level, sound toggle, verbose mode

### Defined but not implemented (stubs only)

1. **18 block type behaviors** — types exist in `block_types.py` but lack
   activation logic
2. **6 specials** — saving, fast gun, no wall, killer, x2, x4
3. **Score multiplier** — no x2/x4 application
4. **Extra life at score thresholds**

### Partially implemented (working but incomplete)

1. **Ball physics** — lacks mass, tilt, 14-zone paddle collision
2. **Bullet system** — lacks tink effects, fast gun dual-fire, unlimited mode
3. **Bonus screen** — state machine present, animation fidelity may differ
4. **Specials panel display** — file exists, completeness unclear

## Prioritized Recommendations

| Priority | Gap | Effort | Impact |
|----------|-----|--------|--------|
| 1 | Block effect logic (18 types) | Medium | High — enables real gameplay variety |
| 2 | Score multiplier + extra life thresholds | Low | High — core scoring mechanic |
| 3 | Specials activation (6 missing) | Medium | High — power-up variety |
| 4 | Screen transition effects (shake, fade, blind) | Medium | Medium — polish |
| 5 | Presents / intro / attract screens | High | Medium — game personality |
| 6 | High score system (table + persistence) | Medium | Medium — replayability |
| 7 | Save/load game | Medium | Medium — session continuity |
| 8 | Ball physics (mass, tilt, 14-zone) | Medium | Medium — fidelity to original |
| 9 | EyeDude character | Medium | Low — fun but not core |
| 10 | Level editor | High | Low — developer tool |
