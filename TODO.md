# TODO.md

Keep the TODO list organized by:
 - Tracking items that are either identified and unresolved or in-progress
 - Updating in progress items as [p] and complete items as [x] until deletion
 - Removing completed items after unit tests and linter checks pass fully.
 - Grouping items by scope and identifying them as <type>(<scope>): <short summary>

## Functionality
- [x] feat(game): Add auto-launch after 3 seconds for stuck balls
    - Track the time when each ball becomes stuck to the paddle (e.g., using a timer in GameController, matching the C version's BALL_AUTO_ACTIVE_DELAY = 3000 ms).
    - In the game update loop, check if any ball is still stuck and if 3 seconds (3000 ms) have passed since it became stuck.
    - If so, automatically release the ball from the paddle as if the user clicked (call `release_from_paddle()` and trigger timer/events as needed).
    - Reset the timer when the ball is released (by user or auto-launch).
    - Ensure this works for all cases where a ball becomes stuck (new level, after losing a ball, sticky paddle, etc.).
    - Add/adjust tests to verify the auto-launch behavior.
    - The timer does not count down if the game is paused.
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

## Paddle Guide Animation (Launch Direction Indicator)
- [p] feat(paddle): Implement animated paddle guide (launch direction indicator) using guide images
    - Preload guide images (guide1.png to guide11.png) and store in a list.
    - Add guide animation state (`guide_pos`, `guide_inc`) to the relevant game or ball state.
    - Integrate guide animation update logic (ping-pong cycling) into the main update loop when a ball is in BALL_READY state.
    - Draw the correct guide image above the ball in the render/draw method when BALL_READY.
    - ~~Handle user input (left/right keys, optionally mouse) to adjust `guide_pos` and update the guide image in real time.~~ (Not needed: Python now matches C game, guide is animated only)
    - [x] On ball launch, set the ball's (dx, dy) velocity according to the current `guide_pos` mapping. (Ball.release_from_paddle now uses guide_pos)
    - Ensure the guide is hidden as soon as the ball is launched.
    - Write/adjust tests to verify correct guide animation, input handling, and launch direction.
    - Ensure all code is PEP 8, PEP 257, and PEP 484 compliant.
    - Run `hatch run lint-fix`, `pylint`, and `pytest` to ensure full compliance and test coverage.
    - Update `TODO.md` to mark as complete when done.
    - Note: Python implementation now matches the original C game—guide is animated only, not user-controlled.

- [x] Fix background cycling bug when advancing to the next level by reordering the background update logic in LevelCompleteController (move get_next_level before setting background index).
