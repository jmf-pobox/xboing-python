# XBoing Scoring, Bonus, and Penalty Logic

## Overview
This document summarizes the scoring, bonus, and penalty logic in XBoing, based on the original C code (`score.c`), the official documentation (`xboing.man`, `README`), and the current Python implementation. It is intended to capture all rules not already specified in `src/xboing/assets/config/block_types.json`.

For block-specific point values, refer to `block_types.json`. This document focuses on additional rules, including bonuses, penalties, multipliers, and end-of-level calculations.

---

## 1. Block Scoring
- **Block point values** (e.g., RED_BLK = 100, BLUE_BLK = 110, etc.) are defined in `block_types.json`.
- Some blocks (e.g., COUNTER_BLK) may have more than one score associated with them, depending on their state.

## 2. Paddle Hit Bonus
- **Each time the paddle is hit with the ball, the player earns 10 points.**

## 3. Bonus Multipliers
- **x2 and x4 Bonus:**
  - If the player collects a x2 or x4 bonus coin, all subsequent points are multiplied by 2 or 4, respectively.
  - If the player collects x2, then x4, then x2 again, the multiplier returns to x2.
  - The multiplier is **reset after each ball death** (i.e., losing a ball disables the multiplier).
  - This logic is implemented in the C function `ComputeScore`, which multiplies the increment by 2 or 4 if the corresponding bonus is active.

## 4. End-of-Level Bonuses
At the end of each level, the following bonuses are awarded:

- **Level Bonus:**
  - `level_bonus = level_number * 100`
  - Example: Level 20 yields a 2,000 point bonus.
  - **If the level is not completed within the allotted time, the player does not receive the level bonus.**

- **Time Bonus:**
  - `time_bonus = seconds_remaining * 100`
  - If the level timer runs out, the player does not receive the time bonus.

- **Bullet Bonus:**
  - `bullet_bonus = 500 * (number of unused bullets)`
  - Awarded for each bullet not used at the end of the level.

- **Coin Bonus:**
  - `coin_bonus = 3000 * (number of bonus coins collected)`
  - Each bonus coin collected during the level is worth 3,000 points at the end of the level.

- **Super Bonus:**
  - If the player collects more than 8 bonuses in a level, a **Super Bonus** of 50,000 points is awarded.

- **Total Bonus:**
  - `total_bonus = coin_bonus + (super_bonus if earned) + level_bonus + bullet_bonus + time_bonus`
  - The total bonus is added to the player's score at the end of the level.

- **Final Score:**
  - `final_score = score + total_bonus`

## 5. Special Scoring Events
- **Roamer (moving enemy):**
  - Worth 400 points when destroyed.
- **Eye Dude:**
  - If shot or hit by the ball, awards 10,000 points. Only appears if the top row is clear.
- **Drop Block:**
  - Score decreases as the block moves down the screen: `drop_score = (row) * 100` (row is the current row of the block).
- **Counter Block:**
  - Worth 200 points per number (may require multiple hits).

## 6. Bullet and Ammo Rules
- **Starting Bullets:**
  - Player receives 4 bullets at the start of each level.
- **Ball Loss:**
  - If the player loses a ball, they are given 2 bullets as a token.
- **Ammo Block:**
  - Awards 50 points plus additional bullets.
- **Unlimited Ammo Block:**
  - Grants unlimited ammo for the level (no direct score effect).

## 7. Penalties and Missed Bonuses
- **Death Block:**
  - If hit by the ball, destroys the ball (no direct score penalty, but loss of ball and multiplier reset).
- **Level Timeout:**
  - If the level timer runs out, the player receives **no time bonus and no level bonus** for that level.
- **Multiplier Reset:**
  - Losing a ball resets any active x2 or x4 score multiplier.

## 8. Extra Ball and Lives
- **Extra Ball Block:**
  - Awards an extra ball (life) and 100 points.
- **Every 100,000 Points:**
  - The player receives a new ball (life) for every 100,000 points scored.

## 9. High Score Table
- **Highscores are saved at the end of each game.**
- If the player quits mid-game, their score is still added to the highscore table.
- There are two highscore tables: global (best score per user) and personal (all attempts).

## 10. Miscellaneous
- **Specials:**
  - Some blocks (e.g., reverse, machine gun, sticky paddle, etc.) have special effects but do not directly affect the score unless otherwise noted.
- **Dynamite Block:**
  - When hit, destroys all blocks of the same type (awarding points for each destroyed block).
- **Random Block:**
  - Changes type and point value randomly.

---

## References
- `src/xboing/assets/config/block_types.json` — Block point values and special behaviors
- `xboing2.4-clang/score.c` — Original C scoring logic
- `docs/xboing2.4/xboing.man` — Official manual page
- `docs/xboing2.4/README` — Game overview and additional notes
- `src/xboing/ui/level_complete_view.py` — Python bonus calculation (WIP)

---

**Note:** This document is intended to be the authoritative source for all scoring, bonus, and penalty logic in the XBoing Python project, except for block-specific values, which are maintained in `block_types.json`. 