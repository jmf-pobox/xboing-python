- [x] Add debug feature: Pressing X key during gameplay blows up all blocks and advances to the next level.
- [ ] Refactor SpriteBlock animation system to ensure type safety between list and dict animation_frames (already patched, but consider a more robust design).
- [ ] Fix test suite import errors (pygame and src import issues).
- [ ] Add `pillow` to `[tool.hatch.envs.default.dependencies]` in `pyproject.toml` for dev/scripts use.
- [ ] Recreate the dev environment using Hatch (`hatch shell` or `hatch env create`).
- [ ] Ensure VS Code is using the Hatch-managed environment as its Python interpreter.
- [ ] Remove any unused direct dependencies from `pyproject.toml` if found.
- [ ] (Optional) Use `pip-tools` to generate a `requirements.txt` for runtime dependencies from `pyproject.toml`.
- [ ] Use `pyproject.toml` as the single source of truth for both runtime and dev dependencies.
- [x] Refactor the audio player module (src/utils/audio_player.py) to remove .au file support, simplify code, and ensure it follows modern Python and project coding standards as per the refactor proposal in docs/AUDIO_PLAYER-refactor.md.
- [x] Implement a simple EventBus in src/utils/event_bus.py
- [x] Refactor AudioManager to subscribe to events and manage sound playback
- [x] Update game objects to fire events instead of playing sounds directly
- [x] Extend the event system for GUI updates if desired (audio system complete; GUI events can be added in future)
- [x] Write unit tests for the event bus and audio manager
- [x] Remove unused src/utils/audio_player.py and src/engine/audio.py modules
- [ ] Create `src/ui/` package for UI components
- [ ] Move/refactor score, lives, timer, overlays, and menu UI code into separate component classes in `src/ui/`
- [ ] Define UI events (e.g., `ScoreChangedEvent`, `LifeLostEvent`, `LevelChangedEvent`, etc.) in `src/engine/events.py`
- [ ] Update game logic to fire UI events on state changes
- [ ] Implement each UI component to subscribe to relevant events and update its display state
- [ ] Implement a `UIManager` class to own and draw all UI components
- [ ] Refactor main loop to remove direct UI rendering; use event firing and `ui_manager.draw_all(surface)`
- [ ] Add unit tests for each UI component (rendering, event handling)
- [ ] Add integration tests for event-driven UI updates
- [ ] Document new UI architecture and update developer docs as needed
- [ ] Refactor level display (level number) into an event-driven UI component in src/ui/
- [ ] Define LevelChangedEvent in src/engine/events.py
- [ ] Update game logic to fire LevelChangedEvent on level changes
- [ ] Add unit tests for LevelDisplay component
- [ ] Refactor timer display into an event-driven UI component in src/ui/
- [ ] Define TimerUpdatedEvent in src/engine/events.py
- [ ] Update game logic to fire TimerUpdatedEvent on timer updates
- [ ] Add unit tests for TimerDisplay component
- [ ] Remove direct renderer.draw_text for level title in message window region in main.py (DONE)
- [ ] Remove commented-out score_display = digit_display.render_number(...) line in main.py (DONE)
- [ ] Confirmed: All UI rendering for score, lives, level, timer, and message window is now fully event-driven and handled by their respective components. (DONE)
- [ ] Bundle a TTF font with tighter kerning (e.g., Roboto or Montserrat) and update the game to use it for all UI components for consistent cross-platform appearance.
- [ ] Extract the Special Window (for bonus displays) as a UI component, even though it is currently unused, to prepare for future features.
- [ ] Add special state variables (reverseOn, stickyBat, saving, fastGun, noWalls, Killer, x2Bonus, x4Bonus) to main.py or game_state.py.
- [ ] Fire events to update the SpecialDisplay component when any special state changes (event should communicate True/False for each special).
- [ ] Integrate the SpecialDisplay view into the main loop and ensure it draws in the special window region.
- [x] Design and implement ContentViewManager for the play window region.
- [x] Create UI components for each content view: GameView, InstructionsView. (WelcomeView, DemoView, LevelPreviewView, GameKeysView, HighScoresView still to do)
- [x] Refactor main loop/UIManager to use ContentViewManager for play window content.
- [x] Wire up InstructionsView to ContentViewManager and main loop: swap to instructions on '?' key, back to game on SPACE, pausing gameplay updates while in instructions view.
- [ ] Implement additional content views: WelcomeView, DemoView, LevelPreviewView, GameKeysView, HighScoresView.
- [ ] Extract overlays (Game Over, Level Complete, etc.) as content views or overlay components managed by ContentViewManager.
- [ ] Implement event system for swapping content views (e.g., ShowWelcomeEvent, ShowInstructionsEvent, etc.).
- [ ] Add unit and integration tests for all new content views and overlays, and for view switching logic.
- [ ] Document the new content view architecture and update developer docs as needed.
- [ ] Refactor GameView to avoid storing a direct reference to the balls list. Instead, provide a getter or observer mechanism so it always accesses the current balls list. This will prevent bugs caused by stale references when the balls list is reassigned in the main loop.
- [x] Implement InstructionsView as a content view for the play window, displaying instructions text and headline as per the original C version.
- [x] Wire up InstructionsView to ContentViewManager and main loop: swap to instructions on '?' key, back to game on SPACE, pausing gameplay updates while in instructions view.
- [ ] Add unit tests for InstructionsView rendering and for view switching logic (Instructions <-> Game).
- [ ] Review and update README.md documentation links whenever new design documents are added or removed from the docs/ directory to keep the documentation section current.
- [x] Refactor main.py to remove view booleans (e.g., instructions_active) and use content_view_manager.current_name for all view checks. This enables extensibility for arbitrary content views.
- [ ] Extract game over overlay logic from main.py and move to HighScoreView.
- [ ] Implement HighScoreView as a content view in src/ui/high_score_view.py.
- [ ] Register HighScoreView with ContentViewManager in main.py.
- [ ] On game over, switch to HighScoreView instead of drawing overlay in main loop.
- [ ] In HighScoreView, pressing Space resets the game and returns to GameView at level 1.
- [ ] Remove all direct game over overlay/UI code from main.py.
- [ ] Add/extend unit and integration tests for HighScoreView and view switching.
- [ ] Update documentation to reflect new content view flow.
- [x] Fix: Game over overlay should only cover play area, not the entire window
- [x] Fix: Spacebar in game over view should restart the game (reset_game is now called)
- [ ] Review: Check for any remaining legacy direct rendering code for overlays or UI
- [x] Add xboing.png as the logo in the instructions screen, loaded and displayed above the headline, using asset loader and asset_paths utilities.
- [ ] Extract repeated game state initialization logic (score, lives, level, timer, level title message) into a reusable function and use it at startup and in reset_game().
- [x] Rationalize game state reset/initialization into GameState.full_restart and remove the old helper function from main.py.
- [ ] Design and implement a UIManager class to own and coordinate all UI components, overlays, and content views, as proposed in GUI-DESIGN.md. 