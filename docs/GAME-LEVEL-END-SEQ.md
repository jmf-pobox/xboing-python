# Sequence Diagram: Last Block Breaks to LevelCompleteView Rendered

Participants:
- Player
- GameController
- GameState
- LevelManager
- UIManager
- LevelCompleteController
- LevelCompleteView

```
Player         GameController      GameState      LevelManager      UIManager      LevelCompleteController      LevelCompleteView
   |                 |                |               |                |                    |                        |
   |  Ball hits      |                |               |                |                    |                        |
   |  last block     |                |               |                |                    |                        |
   |---------------->|                |               |                |                    |                        |
   |                 | block_manager  |               |                |                    |                        |
   |                 | detects all    |               |                |                    |                        |
   |                 | blocks broken  |               |                |                    |                        |
   |                 |--------------->|               |                |                    |                        |
   |                 |                |               |                |                    |                        |
   |                 | posts LevelCompleteEvent (USEREVENT)           |                    |                        |
   |                 |----------------------------------------------->|                    |                        |
   |                 |                |               |                |                    |                        |
   |                 |                |               |                | UI switches to     |                        |
   |                 |                |               |                | LevelCompleteView  |                        |
   |                 |                |               |                |------------------->|                        |
   |                 |                |               |                |                    | LevelCompleteView      |
   |                 |                |               |                |                    | .activate()            |
   |                 |                |               |                |                    |----------------------->|
   |                 |                |               |                |                    | _compute_bonuses()     |
   |                 |                |               |                |                    | (calls GameState,      |
   |                 |                |               |                |                    |  LevelManager)         |
   |                 |                |               |                |                    |                        |
   |                 |                |               |                |                    | draw()                 |
   |                 |                |               |                |                    |----------------------->|
   |                 |                |               |                |                    | (renders bonus, score, |
   |                 |                |               |                |                    |  etc. to screen)       |
   |                 |                |               |                |                    |                        |
```

**Notes:**
- The GameController detects all blocks are broken and posts a `LevelCompleteEvent` to the Pygame event queue.
- The UIManager (or main event loop) receives this event and switches the active view/controller to `LevelCompleteView`/`LevelCompleteController`.
- `LevelCompleteView.activate()` is called, which computes bonuses by querying `GameState` and `LevelManager`.
- The view's `draw()` method is called each frame to render the level complete screen. 