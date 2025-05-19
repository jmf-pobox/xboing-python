# TODO.md

- [ ] Remove potentially ableist language from test suite
- [ ] Add type hints for all tests and making sure mypy --strict, ruff check, and black run clean
- [ ] Update all tests to use injector-based setup, providing mocks/stubs via test modules as needed
- [ ] Add or update tests to assert on log output using caplog.
- [ ] Migrate asset loading and configuration to DI where feasible
- [ ] Refactor background image loading out of GameLayout (src/layout/game_layout.py) into a dedicated asset loader module for stricter separation of layout and asset management.
- Progressive linter enforcement: Follow docs/LINTER-PLAN.md to re-enable and fix one rule at a time for Ruff and Pylint until full compliance is achieved.
- [ ] Add auto-launch after 5 seconds for stuck balls:
    - Track the time when each ball becomes stuck to the paddle (e.g., using `pygame.time.get_ticks()` and a `stuck_since` attribute on the Ball).
    - In the game update loop, check if any ball is still stuck and if 5 seconds (5000 ms) have passed since it became stuck.
    - If so, automatically release the ball from the paddle as if the user clicked (call `release_from_paddle()` and trigger timer/events as needed).
    - Reset the `stuck_since` timestamp when the ball is released (by user or auto-launch).
    - Ensure this works for all cases where a ball becomes stuck (new level, after losing a ball, sticky paddle, etc.).
    - Add/adjust tests to verify the auto-launch behavior.
- [ ] Investigate DeprecationWarning from pygame/pkgdata.py about pkg_resources being deprecated. Current analysis: This warning appears to be triggered by test code using `pygame.font.Font(None, ...)`, which loads the default font and causes pygame to use its internal resource loader (which uses pkg_resources). User is not convinced this is the root cause; further investigation may be needed.
- [ ] Fix test_ammo_does_not_fire_without_ball_in_play to use a list for ball_manager.balls when mocking
