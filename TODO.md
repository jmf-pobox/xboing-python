# TODO.md

Keep the TODO list organized by:
 - Tracking items that are either identified and unresolved or in-progress
 - Updating in progress items as [p] and complete items as [x] until deletion
 - Removing completed items after unit tests and linter checks pass fully.
 - Grouping items by scope and identifying them as <type>(<scope>): <short summary>

## Functionality
- [ ] feat(game): Add auto-launch after 5 seconds for stuck balls
    - Track the time when each ball becomes stuck to the paddle (e.g., using `pygame.time.get_ticks()` and a `stuck_since` attribute on the Ball).
    - In the game update loop, check if any ball is still stuck and if 5 seconds (5000 ms) have passed since it became stuck.
    - If so, automatically release the ball from the paddle as if the user clicked (call `release_from_paddle()` and trigger timer/events as needed).
    - Reset the `stuck_since` timestamp when the ball is released (by user or auto-launch).
    - Ensure this works for all cases where a ball becomes stuck (new level, after losing a ball, sticky paddle, etc.).
    - Add/adjust tests to verify the auto-launch behavior.
- [ ] feat(paddle): Implement machine gun powerup (state, UI, firing logic)

## Overall Coding Standards
- [ ] chore(lint): Progressive linter enforcement per docs/LINTER-PLAN.md for Ruff and Pylint until full compliance
- [ ] investigate(pygame): Investigate DeprecationWarning from pygame/pkgdata.py about pkg_resources being deprecated. Current analysis: This warning appears to be triggered by test code using `pygame.font.Font(None, ...)`, which loads the default font and causes pygame to use its internal resource loader (which uses pkg_resources). User is not convinced this is the root cause; further investigation may be needed.

## Production Code
- [ ] refactor(assets): Migrate asset loading and configuration to DI where feasible
- [ ] refactor(layout): Move background image loading out of GameLayout (src/layout/game_layout.py) into a dedicated asset loader module
- [ ] feat(blocks): Implement custom block explosion animations for bullet and ball hits (see issue #6)
- [ ] feat(blocks): Implement chain explosions for bomb blocks (neighbor explosions)
- [ ] feat(blocks): Render overlays for dynamite and random block text
- [ ] feat(blocks): Port any remaining special block behaviors and animations for full parity with the C version

## Test Suite
- [ ] chore(tests): Remove potentially ableist language from test suite
- [ ] chore(tests): Add type hints for all tests and ensure mypy --strict, ruff check, and black run clean
- [ ] refactor(tests): Update all tests to use injector-based setup with mocks/stubs via test modules
- [ ] feat(tests): Add or update tests to assert on log output using caplog
- [ ] fix(tests): Fix test_ammo_does_not_fire_without_ball_in_play to use a list for ball_manager.balls when mocking
- [ ] test(paddle): Increase test coverage for paddle gun logic and edge cases
- [ ] test(paddle): Add/expand integration tests for paddle features
- [ ] test(blocks): Ensure all block types in block_types.json are covered in tests and code

## Completed Items
- [x] Remove unused key_map attribute and get_key_name method from InputManager in src/xboing/engine/input.py
- [x] feat(cli): Add --start-level/-l command line argument to set starting level in XBoing
- [x] feat(cli): Add -help and -usage command line arguments to match C version
- [x] refactor(level): Pass starting_level to LevelManager and XBoingApp at construction, remove setattr hack

## New Tasks
- [x] Create docs/DESIGN-SCORING.md: Document all scoring, bonus, and penalty logic, especially rules not already in block_types.json, based on original C code and documentation.
- [x] Create src/xboing/ui/view_with_background.py: Base class for views that render the play area background.
- [x] Refactor GameView to inherit from ViewWithBackground and use draw_background.
- [ ] Update UIManager to remove any global background drawing; only views draw backgrounds as needed.
- [ ] Test that LevelCompleteView and InstructionsView do not render the play area background.
- [ ] Restore default space background in GameView.deactivate.
- [p] Add get_current_background_index() to LevelManager
- [p] Update LevelCompleteController to set background on game_view after loading next level
- [ ] Fix test_game_view_draw: add set_play_background stub to MockLayout
- [x] Fix: Timer UI at game start should show correct time_bonus for level 1 and update as expected
- [x] Fix pygame.event.Event call for TIMER_BLK in src/xboing/controllers/game_controller.py to use two arguments and post two events.
- [x] Ensure test mocks in tests/unit/test_game_controller.py return iterables for methods expected to return lists (e.g., set_timer).
