# XBoing Python GUI Screen Flows

This document diagrams and explains the navigation and sequencing of all major UI views in XBoing Python, including the Welcome screen.

## Screen Flow Diagram

```mermaid
flowchart TD
    Welcome[Welcome Screen]\n(Shown only at launch)
    Game[Game View]
    Instructions[Instructions View]
    LevelComplete[Level Complete View]
    GameOver[Game Over View]

    Welcome -->|Start Game| Game
    Game -- Level Complete --> LevelComplete
    Game -- Game Over --> GameOver
    Game -- Instructions --> Instructions
    LevelComplete -- Continue --> Game
    LevelComplete -- Instructions --> Instructions
    GameOver -- Restart --> Game
    GameOver -- Instructions --> Instructions
    Instructions -- Back to Game --> Game
    Instructions -- Back to Level Complete --> LevelComplete
    Instructions -- Back to Game Over --> GameOver
```

## Navigation Rules

- **Welcome Screen**
  - Shown only once at launch, before the first game session.
  - After progressing past the Welcome screen (e.g., by starting the game), it cannot be returned to, even if the player loses all balls and starts a new game.
- **Game View**
  - Main gameplay area.
  - Can transition to Level Complete, Game Over, or Instructions.
- **Level Complete View**
  - Shown after completing a level.
  - Can return to Game or go to Instructions.
- **Game Over View**
  - Shown after losing all balls.
  - Can restart the game or go to Instructions.
- **Instructions View**
  - Can be accessed from Game, Level Complete, or Game Over.
  - Returns to the view from which it was accessed.

## Example Flows

- **Normal Play:**
  - Welcome → Game → Level Complete → Game → ...
- **Game Over:**
  - Game → Game Over → Game (restart)
- **Instructions:**
  - Game → Instructions → Game
  - Level Complete → Instructions → Level Complete
  - Game Over → Instructions → Game Over

---

This flow ensures the Welcome screen is a true entry point, and all other screens are accessible as overlays or transitions from the main game loop. 