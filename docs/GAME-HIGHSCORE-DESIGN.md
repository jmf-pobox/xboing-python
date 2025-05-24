# HighScoreView Design & Requirements

## 1. Visual Layout
- The HighScoreView replaces the PlayView after game over.
- It displays:
  - A title (e.g., "High Scores" or "Roll of Honour")
  - A table of the top N scores (rank, score, level, time, date, player name)
  - The player's final score, highlighted if it is a new high score
  - (Optional) Boing Master text or other messages
  - A prompt (e.g., "Press SPACE to restart")

## 2. Data Model
- Each high score entry contains:
  - Rank (1-based)
  - Score (integer)
  - Level reached (integer)
  - Game duration (seconds, displayed as MM:SS or H:MM:SS)
  - Date (e.g., DD MMM YY)
  - Player name (string, max length 20)
- The high score table is a list of up to 10 entries (NUM_HIGHSCORES).
- (Optional) Support for both global and personal high scores.

## 3. Persistence
- High scores are saved to and loaded from a file (e.g., JSON or similar, not binary as in C).
- On game over, if the player's score qualifies, prompt for name entry and insert into the table.
- The table is sorted descending by score.
- (Optional) Support for environment variable or config to specify high score file location.

## 4. Event Flow
- On game over:
  - Switch to HighScoreView.
  - Display the table and the player's score.
  - If the score qualifies, prompt for name entry (future step).
- In HighScoreView:
  - Pressing SPACE resets the game and returns to GameView.
  - (Optional) Support for toggling between global/personal tables, or other overlays.

## 5. Extensibility
- The view should be able to:
  - Display both global and personal bests (future)
  - Support animated overlays (e.g., sparkles, title effects)
  - Show custom messages (e.g., Boing Master text)
  - Be themed/skinned for future UI updates

## 6. Migration/Implementation Steps
1. **Create a high score data model** (Python class or dataclass).
2. **Implement file I/O** for loading/saving the high score table (JSON or similar, not binary).
3. **Update HighScoreView** to:
   - Load and display the table
   - Highlight the player's score if present
   - Show all required columns (rank, score, level, time, date, name)
4. **On game over**, check if the score qualifies and (future) prompt for name entry.
5. **Add tests** for high score logic and view rendering.
6. **Document** the design and usage in this file.

---

## References
- Original C implementation: `xboing2.4-clang/highscore.c`
- Current Python view: `src/ui/high_score_view.py`
- Event-driven UI architecture: `docs/GUI-DESIGN.md`

---

*This document is for review and planning. Please provide feedback or additional requirements before implementation proceeds.* 