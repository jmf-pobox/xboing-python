# Business Logic Summary: DoBonuses Function

## Overview
The `DoBonuses` function handles the calculation and display of bonus points earned from collecting bonus coins during gameplay. It's part of the level completion sequence that rewards players for their performance.

## Function Parameters
- `Display *display`: X11 display connection
- `Window window`: X11 window to draw on

## Key Variables
- `numBonus`: Number of bonus coins collected during the level
- `secs`: Seconds remaining on the level timer
- `bonusScore`: Running total of bonus points accumulated
- `firstTime`: Boolean flag to indicate first execution of the function
- `maxLen`: Calculated width for centering the bonus coin display

## Mathematical Formulas

### Score Calculations
- Regular Bonus Coin Score: 
  ```
  Score Increase = BONUS_COIN_SCORE = 3000 points per coin
  Total Coin Bonus = numBonus × 3000
  ```
  *Condition*: Awarded only if timer hasn't run out (secs > 0) and 0 < numBonus ≤ MAX_BONUS

- Super Bonus (when numBonus > MAX_BONUS):
  ```
  Score Increase = SUPER_BONUS_SCORE = 50000 points (flat bonus)
  ```
  *Condition*: Awarded only if timer hasn't run out (secs > 0) and numBonus > MAX_BONUS

- Level Bonus (calculated in DoLevel function):
  ```
  theLevel = level - GetStartingLevel() + 1
  Level Bonus = theLevel × LEVEL_SCORE = theLevel × 100
  ```
  *Condition*: Awarded only if timer hasn't run out (secs > 0)

- Bullet Bonus (calculated in DoBullets function):
  ```
  Bullet Bonus = GetNumberBullets() × BULLET_SCORE = GetNumberBullets() × 500
  ```
  *Condition*: Awarded only if GetNumberBullets() > 0

- Time Bonus (calculated in DoTimeBonus function):
  ```
  Time Bonus = secs × TIME_BONUS = secs × 100
  ```
  *Condition*: Awarded only if timer hasn't run out (secs > 0)

  Where `secs` is the number of seconds remaining on the level timer.

- Total Bonus (sum of all bonuses):
  ```
  Total Bonus = Coin Bonus + Super Bonus (if applicable) + Level Bonus + Bullet Bonus + Time Bonus
  ```

### Display Positioning Calculations
- Maximum display width for centering:
  ```
  maxLen = (numBonus × 27) + (10 × numBonus) + 5
  ```
  Where:
  - 27 pixels is the width of each bonus coin
  - 10 pixels is the spacing between coins
  - 5 pixels is additional padding

- Position length for current display:
  ```
  plen = (numBonus × 27) + (10 × numBonus)
  ```

- X-coordinate for centered display:
  ```
  x = (((PLAY_WIDTH + MAIN_WIDTH) / 2) + (maxLen / 2)) - plen
  ```
  This formula centers the remaining coins by:
  1. Finding the center of the play area: `(PLAY_WIDTH + MAIN_WIDTH) / 2`
  2. Adding half the maximum width: `+ (maxLen / 2)`
  3. Subtracting the current width: `- plen`

## Business Logic Flow

### 1. Time Check
- Retrieves the number of seconds left on the level timer
- If the timer has run out (secs == 0):
  - Plays a "Doh4" sound effect
  - Displays "Bonus coins void - Timer ran out!" message
  - Sets game speed to slow
  - Advances to the next bonus sequence (BONUS_LEVEL)
  - Returns without awarding any bonus points

### 2. First-Time Setup
If this is the first time the function is called (firstTime == True):
- Sets firstTime to False
- Performs checks on the number of bonus coins collected:
  - If no bonus coins were collected (numBonus == 0):
    - Plays a "Doh1" sound effect
    - Displays "Sorry, no bonus coins collected." message
    - Sets game speed to slow
    - Advances to the next bonus sequence (BONUS_LEVEL)
    - Returns without awarding any bonus points
  - If more than MAX_BONUS coins were collected:
    - Plays a "supbons" sound effect
    - Displays "Super Bonus" message with the super bonus score
    - Adds SUPER_BONUS_SCORE to the player's score
    - Sets game speed to slow
    - Advances to the next bonus sequence (BONUS_LEVEL)
    - Returns after awarding the super bonus
- Calculates the display width needed to center the bonus coins (maxLen)

### 3. Bonus Coin Processing
For each bonus coin:
- Calculates the position to draw the bonus coin
- Draws the bonus coin on screen
- Plays a "bonus" sound effect
- Adds BONUS_COIN_SCORE to the player's score
- Decrements the number of remaining bonus coins (numBonus)

### 4. Completion Check
When all bonus coins have been processed (numBonus <= 0):
- Sets up for the next bonus sequence (BONUS_LEVEL)
- Resets the bonus coin counter
- Adjusts the vertical position for the next text
- Sets game speed to slow

## Summary
The DoBonuses function rewards players for collecting bonus coins during gameplay. It provides visual feedback by displaying each bonus coin and incrementing the score accordingly. Special cases are handled for when no coins were collected, when the timer ran out, or when a large number of coins were collected (super bonus). The function is part of a larger bonus calculation sequence that occurs when a level is completed.
