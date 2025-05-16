# TODO.md

## Unified Pygame Event System Migration (2024)

- [ ] Remove all imports and usage of EventBus and EventHandlerProtocol from all modules.
- [ ] Refactor GameState to use pygame.event.post for all events.
- [ ] Refactor all controllers (GameController, LevelCompleteController, etc.) to use pygame.event.post for firing events and handle_events(events) for handling.
- [ ] Refactor all UI components (ScoreDisplay, LivesDisplay, etc.) to use handle_events(events) and check for custom Pygame events.
- [ ] Refactor AudioManager to use handle_events(events) and play sounds on custom Pygame events.
- [ ] Refactor UIManager to use only the Pygame event queue for view switching.
- [ ] Refactor main.py to remove all EventBus logic and use only the Pygame event queue.
- [ ] Update or remove all tests that use EventBus or protocol-based handlers.
- [ ] Run the test suite before and after each change.
- [ ] Manual QA: launch the game and verify all major flows (gameplay, game over, level complete, UI updates, sound, etc.) work.

---

## Other Refactors & Improvements

- [ ] Move UIManager/ControllerManager synchronization logic out of main.py and into a coordinator or the manager classes themselves.
- [ ] Apply logging decorators (@log_entry_exit, @log_exceptions, @log_timing) to key functions in main.py.
- [ ] Use module-level or class-specific loggers (logging.getLogger(__name__) or logging.getLogger(f"xboing.{ClassName}")) instead of hardcoded names.
- [ ] Set per-class/module log level overrides where more verbosity is needed.
- [ ] Add or update tests to assert on log output using caplog.
- [ ] Refactor background image loading out of GameLayout (src/layout/game_layout.py) into a dedicated asset loader module for stricter separation of layout and asset management.
- [ ] Refactor GameState to always use its own self.event_bus instead of requiring an event_bus argument to full_restart, to prevent similar bugs in the future.
- [ ] Update all tests to use injector-based setup, providing mocks/stubs via test modules as needed.
- [ ] Incrementally migrate remaining manual constructions (e.g., asset loaders, configuration) to DI as appropriate.
- [ ] Update documentation and code comments to reflect DI usage and patterns.
- [ ] Remove obsolete factory code and manual wiring after migration is complete.
- [ ] Run the full test suite and perform manual QA to ensure correctness after each major migration step.

## main.py Compliance with GUI-DESIGN.md and LOGGING-DESIGN.md

- [x] Finish moving all UI component instantiation and layout logic from main.py to UIFactory.
- [x] Move controller instantiation and registration from main.py to a controller setup module/class.
- [x] Move game object creation (paddle, balls, block manager, etc.) from main.py to a game factory or state setup module.
- [x] Move event handler functions (e.g., on_level_complete, advance_to_next_level, reset_game) into appropriate controller classes. (Verified: all event handler logic is now in controllers, not in main.py)
- [x] Remove launch/game over/level complete logic from main.py and delegate to controllers. (Verified: all such logic is now handled by controllers and/or the coordinator, not in main.py)
- [x] Ensure correct startup, level loading, and level advancement logic. (Game now starts on level 1, level advancement and ball launch work as expected)
- [ ] Ensure all asset loading logic is handled by asset loader modules, not in main.py.

## Follow-up Suggestions

- [ ] Refactor background image loading out of GameLayout (src/layout/game_layout.py) into a dedicated asset loader module for stricter separation of layout and asset management.
- [ ] Refactor GameState to always use its own self.event_bus instead of requiring an event_bus argument to full_restart, to prevent similar bugs in the future.

## Adopt Dependency Injection (DI) with injector

- [x] 1. Add `injector` as a project dependency (update requirements and install).
- [x] 2. Refactor all controllers and views to use type hints and (optionally) the `@inject` decorator for their dependencies.
- [x] 3. Create an `XBoingModule` (or similar) in a new `di/` or `core/` package, providing all bindings for controllers, views, UIManager, UIFactory, and other core objects. Use factory scope for all objects unless singleton is required.
- [x] 4. Refactor `UIFactory` and `ControllerFactory` to be injectable and to delegate instantiation to the injector, or replace with DI-based composition if possible.
- [x] 5. Update `main.py` to use the injector for application composition, removing manual construction and wiring of dependencies (for GameOver and Instructions screens).
- [ ] 6. Update all tests to use injector-based setup, providing mocks/stubs via test modules as needed.
- [ ] 7. Incrementally migrate remaining manual constructions (e.g., asset loaders, configuration) to DI as appropriate.
- [ ] 8. Update documentation and code comments to reflect DI usage and patterns.
- [ ] 9. Remove obsolete factory code and manual wiring after migration is complete.
- [ ] 10. Run the full test suite and perform manual QA to ensure correctness after each major migration step.

---

**Next session:**
Continue with main.py compliance refactor, starting with moving UIManager/ControllerManager synchronization logic out of main.py and into a coordinator or the manager classes themselves.

- [x] Set the timer in GameState at the start of each round and after loading a level.
- [x] Ensure the timer is updated in the UI immediately after the ball is launched.
- [x] Test that the timer displays and counts down correctly in-game.

- [x] Integrate application icon using assets/images/icon.png in the game window (complete)

- [x] Refactor GameState and GameController to decouple event firing (complete)

- [x] BUGFIX: When the last life is lost, the lives display (balls) should update to zero before the game over overlay appears. Fixed by emitting both LivesChangedEvent(0) and GameOverEvent in GameState.lose_life(). Added a test to ensure event order.

- [x] Resolve all mypy --strict errors in src/ui/score_display.py with PEP-compliant typing and docstrings

- [x] Resolve all mypy --strict errors in src/ui/message_display.py with PEP-compliant typing and docstrings

- [x] Resolve all mypy --strict errors in src/ui/lives_display.py with PEP-compliant typing and docstrings

- [x] Resolve all mypy --strict errors in src/ui/level_display.py with PEP-compliant typing and docstrings

- [x] Resolve all mypy --strict errors in src/ui/level_complete_view.py with PEP-compliant typing and docstrings

- [x] Resolve all mypy --strict errors in src/ui/bottom_bar_view.py with PEP-compliant typing and docstrings

- [x] Resolve all mypy --strict errors in src/ui/top_bar_view.py with PEP-compliant typing and docstrings

- [x] Resolve all mypy --strict errors in src/ui/special_display.py with PEP-compliant typing and docstrings

- [x] Resolve all mypy --strict errors in src/ui/game_view.py with PEP-compliant typing and docstrings

- [x] Resolve all mypy --strict errors in src/ui/instructions_view.py with PEP-compliant typing and docstrings

- [x] Resolve all mypy --strict errors in src/ui/game_over_view.py with PEP-compliant typing and docstrings

- [x] Resolve all mypy --strict errors in src/ui/ui_factory.py with PEP-compliant typing and docstrings

- [x] src/renderers/digit_renderer.py: mypy strict, PEP-compliant type annotations, modern docstrings, tests pass, ruff clean

- [x] src/renderers/lives_renderer.py: mypy strict, PEP-compliant type annotations, modern docstrings, tests pass, ruff clean
