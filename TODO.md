# TODO.md

- [ ] Add type hints for all tests and making sure mypy --strict, ruff check, and black run clean
- [ ] Update all tests to use injector-based setup, providing mocks/stubs via test modules as needed
- [ ] Add or update tests to assert on log output using caplog.
- [ ] Migrate asset loading and configuration to DI where feasible
- [ ] Refactor background image loading out of GameLayout (src/layout/game_layout.py) into a dedicated asset loader module for stricter separation of layout and asset management.
- [x] Refactor magic number `3` in mouse button comparisons in `src/engine/input.py` to use a named constant.
-