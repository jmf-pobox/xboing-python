# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Changed
- Minimum Python version raised from 3.10 to 3.14
- Modernized type annotations across 69 source files (PEP 585 builtin
  generics, PEP 604 union syntax)
- License corrected to MIT (PEP 639 SPDX identifier in pyproject.toml)
- Upgraded dev tools: mypy >=2.1.0, pyright >=1.1.410, ruff >=0.15.0
- Added ruff rule categories: FURB, PERF, PIE
- CI matrix narrowed to Python 3.14

### Removed
- `typing_extensions` runtime dependency (no longer needed with Python 3.14)
- `aiohttp` dev dependency

## [0.4.0] - 2025-11-22

### Added
- GameController decomposition (Phases 0-6): protocol architecture,
  collision system, input controllers, GameStateManager, PowerUpManager
- Complexity metrics integration (radon, xenon)
- CI alignment with quality gates

## [0.3.0] - 2025-05-28

### Added
- Animated paddle guide
- Renderer refactoring
- Scoreboard and README updates

## [0.2.0] - 2025-05-26

### Added
- Paddle gun system with ammo collection
- Ball-block collision animations
- MyPy strict mode compliance

## [0.1.0] - 2025-05-17

### Added
- Initial Python port of XBoing
- Core gameplay: paddle, ball, blocks, collisions
- 80 levels, full audio assets
- Dependency injection architecture
- Hatch-based project structure
