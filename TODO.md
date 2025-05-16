# TODO.md

- [ ] Apply Python coding standards: comments, type hints, etc. to tests
- [ ] Use module-level or class-specific loggers (logging.getLogger(__name__) or logging.getLogger(f"xboing.{ClassName}")) instead of hardcoded names.
- [ ] Set per-class/module log level overrides where more verbosity is needed.
- [ ] Add or update tests to assert on log output using caplog.
- [ ] Migrate UIFactory to use DI for all UI components and views (in progress)
- [ ] Migrate ControllerFactory to use DI for all controllers (in progress)
- [ ] Incrementally migrate remaining controllers and UI components to DI (remove manual/factory construction)
- [ ] Migrate asset loading and configuration to DI where feasible
- [ ] Update all tests to use injector-based setup, providing mocks/stubs via test modules as needed
- [ ] Remove or refactor UIFactory and ControllerFactory once all construction is handled by DI
- [ ] Refactor background image loading out of GameLayout (src/layout/game_layout.py) into a dedicated asset loader module for stricter separation of layout and asset management.
- [ ] Keep the Project Structure section in README.md up to date with any future directory changes
- [ ] Migrate main.py to use DI for controllers (ControllerManager, GameController, etc.) instead of ControllerFactory. Do not remove ControllerFactory yet.
- [ ] Continue to ensure all new/refactored code is fully type-annotated and documented.
- [ ] Update documentation as further architectural changes are made.
- [ ] Review BallManager API for further enhancements if needed.
-