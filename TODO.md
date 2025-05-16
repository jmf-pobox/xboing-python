# TODO.md

- [ ] Use module-level or class-specific loggers (logging.getLogger(__name__) or logging.getLogger(f"xboing.{ClassName}")) instead of hardcoded names.
- [ ] Set per-class/module log level overrides where more verbosity is needed.
- [ ] Add or update tests to assert on log output using caplog.
- [ ] Update all tests to use injector-based setup, providing mocks/stubs via test modules as needed.
- [ ] Incrementally migrate remaining manual constructions (e.g., asset loaders, configuration) to DI as appropriate.
- [ ] Refactor background image loading out of GameLayout (src/layout/game_layout.py) into a dedicated asset loader module for stricter separation of layout and asset management.
