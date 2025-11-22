# Claude Code: Project Context and Instructions

## Project Overview

This is `xboing-python` - a Python port of the classic XBoing breakout-style arcade game, modernized with clean architecture and comprehensive testing.

**Goal**: Maintain a clean, well-tested, modular codebase for a classic arcade game while preserving the original gameplay experience.

## Key Documentation Files

Essential reading for understanding the project:

- **[CLAUDE.md](CLAUDE.md)** (this file) - Project context, workflow commands, coding standards, session management
- **[STATUS.md](STATUS.md)** - Current implementation status, refactoring progress, test counts, recent changes
- **[docs/ARCHITECTURE-MVC-REVISED.md](docs/ARCHITECTURE-MVC-REVISED.md)** - MVC architecture, design patterns
- **[docs/CODE-GAME-PROTOCOL.md](docs/CODE-GAME-PROTOCOL.md)** - Protocol-based architecture design
- **[docs/CODE-GAME-PROTOCOL-REVISED.md](docs/CODE-GAME-PROTOCOL-REVISED.md)** - Refined protocol patterns
- **[docs/GAME-CONTROLLER-DECOMPOSITION.md](docs/GAME-CONTROLLER-DECOMPOSITION.md)** - Decomposition plan for GameController
- **[docs/CODE-TESTING-STRATEGY.md](docs/CODE-TESTING-STRATEGY.md)** - Testing approach and patterns
- **[PLAN.md](PLAN.md)** - Current refactoring roadmap

## CRITICAL: Code Quality Standards (MANDATORY)

**🚨 ABSOLUTE REQUIREMENTS - NO EXCEPTIONS:**

### Required Quality Gates (Run After EVERY Code Change)

**Production Code (src/) - MUST PASS ALWAYS:**
```bash
hatch run lint           # 1. ZERO Ruff violations (src/ only)
hatch run format         # 2. Perfect formatting (src/ only)
hatch run type           # 3. ZERO MyPy errors (src/ only, strict mode)
hatch run type-pyright   # 4. ZERO Pyright errors (src/ only, strict mode)
hatch run test           # 5. ALL tests pass (currently 170 tests)
```

**Test Code (tests/) - Fix Gradually:**
```bash
hatch run lint-test          # Check test code lint (438 mypy, 814 pyright errors to fix)
hatch run type-test          # Check test code types with mypy
hatch run type-pyright-test  # Check test code types with pyright
```

**Combined Checks:**
```bash
hatch run check          # Production code only (lint + type + type-pyright + test)
hatch run check-all      # Everything including test code (for progress tracking)
hatch run lint-all       # Check src/ + tests/
hatch run format-all     # Format src/ + tests/
hatch run type-all       # Run both mypy and pyright on src/
hatch run type-all-code  # Run mypy on src/ + tests/
hatch run type-pyright-all  # Run pyright on everything
```

**Quality Status:**
- Production code (src/): 100% type-clean ✅
- Test code (tests/): Fix gradually during refactoring

### Code Standards (MANDATORY)
- **Type hints**: Full type annotations on all functions and methods
- **MyPy strict mode**: No Any types, no untyped definitions
- **Pyright strict mode**: All strict checks enabled
- **Protocol inheritance**: All protocol implementations must explicitly inherit
- **88 character line limit**: Enforced by black
- **Double quotes**: For strings (enforced by black)
- **Clean separation**: MVC pattern with Controllers, Models, Views, Renderers

### Prohibited Patterns
- ❌ No `type | None` parameters unless absolutely necessary
- ❌ No inline import statements
- ❌ No mock objects in production code (tests only)
- ❌ No defensive coding or fallback logic unless explicitly requested
- ❌ No `hasattr()` - use protocols instead
- ❌ No duck typing - use explicit protocol inheritance
- ❌ No circular imports - maintain clean dependency hierarchy

### Micro-Commit Workflow (MANDATORY)
- **One change** = One commit (extract function, fix bug, add test)
- **Commit size limits**: 1-5 files, <100 lines preferred
- **Branch workflow**: ALL development on feature branches
- **Quality gates between commits**: Run all 5 commands above

### Communication Standards
- ❌ Never claim "fixed" without user confirmation
- ❌ No buzzwords, jargon, or superlatives
- ❌ No exaggeration or enthusiasm about unverified results
- ❌ **DO NOT CODE when asked yes/no questions** - just answer the question
- ✅ State what changed and why
- ✅ Explain what needs user verification
- ✅ Use plain, accurate language
- ✅ Modest, short commit messages
- ✅ Answer questions directly without over-engineering

### Solution Standards (MANDATORY)
- ✅ **Proper solution first**: Identify and implement the correct solution immediately
- ✅ **No compromises on false warnings**: False warnings train you to ignore logs - unacceptable
- ✅ **Industry standard patterns**: Use professional patterns (MVC, protocols, composition)
- ❌ **No shortcuts or hacks**: Don't offer inferior alternatives to save time
- ❌ **No warning filters to hide problems**: Fix the root cause, don't mask symptoms

## Workflow Commands

**ALWAYS use these commands (defined in pyproject.toml):**

### Development Workflow
```bash
# Run the game
hatch run game

# Testing
hatch run test           # Run ALL unit tests
hatch run test-cov       # Run tests with coverage

# Quality gates (run after every change)
hatch run lint           # Linting with ruff
hatch run format         # Format code with black
hatch run format-check   # Check formatting without modifying
hatch run type           # Type checking with mypy
hatch run type-pyright   # Type checking with pyright
hatch run type-all       # Both mypy and pyright
hatch run check          # lint + type + type-pyright + test
hatch run check-cov      # lint + type + type-pyright + test-cov

# Run specific tests
hatch run test tests/unit/test_ball.py                           # Single file
hatch run test tests/unit/test_ball.py -v                        # Verbose output
hatch run test tests/unit/test_ball.py::TestBall                # Single test class
hatch run test tests/unit/test_ball.py::TestBall::test_bounce_off_paddle -v  # Single test

# Game with coverage
hatch run cov-game       # Run game with coverage, show report
hatch run cov-game-html  # Run game with coverage, generate HTML
```

## Environment Setup

### Critical Dependencies

1. **pygame**: Game engine
   - Used for graphics, sound, and input handling
   - Cross-platform support

2. **injector**: Dependency injection framework
   - Used for clean separation of concerns
   - Enables testability

3. **Python**: Python 3.10+
   - Modern Python features (protocols, type hints)

### Test Organization

**Unit tests**: `tests/unit/`
- Test individual components in isolation
- Mock dependencies
- Fast execution
- Currently: 170 tests

**Integration tests**: `tests/integration/`
- Test interactions between components
- Real dependencies
- Slower execution

**Game tests**: `tests/game/`
- End-to-end game scenarios
- Full system integration

## Architecture

### Core Design Patterns

**MVC Pattern:**
- **Models**: Game state, entities (Ball, Paddle, Block, Bullet)
- **Views**: Display management (GameView, MenuView)
- **Controllers**: Input handling, game logic coordination (GameController)

**Protocol-based Architecture:**
- `Updateable`: Objects that update each frame
- `Drawable`: Objects that can be rendered
- `Collidable`: Objects that participate in collision detection
- `Positionable`: Objects with position and bounds
- `Activatable`: Objects that can be active/inactive

**Manager Pattern:**
- `BallManager`: Manages multiple balls
- `BlockManager`: Manages level blocks
- `BulletManager`: Manages bullet projectiles
- `GameStateManager`: Manages game state transitions
- `LevelManager`: Manages level loading and progression

**Collision System:**
- `CollisionSystem`: Collision detection (broad and narrow phase)
- `CollisionHandlers`: Collision response logic

### Current Refactoring

We are decomposing the monolithic `GameController` (originally 479 lines) into specialized managers:

**Phase 3 (Current)**: GameStateManager extraction ✅
- Life loss handling
- Level completion detection
- Timer management
- Game over coordination

**Phase 4 (Next)**: PowerUpManager extraction
- Power-up state management (sticky, reverse, etc.)
- Duration tracking
- Effect application

**Phases 5-6**: Legacy cleanup and final architecture
- Remove test compatibility code
- Reduce GameController to < 300 lines
- Achieve 90% test coverage

See [PLAN.md](PLAN.md) for detailed roadmap.

## User's Preferences

From conversation and codebase:
1. ✅ Clean, maintainable architecture over quick hacks
2. ✅ Comprehensive testing (170 tests and growing)
3. ✅ Protocol-based design for flexibility
4. ✅ Micro-commits with quality gates
5. ✅ Zero tolerance for type errors or lint violations

## Important Notes for Claude

### When Making Design Decisions
- Prioritize clean architecture over convenience
- User prefers robust solutions over quick hacks
- Testing is core to the project, not optional
- Maintain 100% test pass rate throughout refactoring
- Follow Single Responsibility Principle

### When Refactoring
- Never break existing tests
- Extract managers one at a time
- Remove legacy code only after new patterns proven
- Keep commits small and focused
- Run full quality checks between each change

## Debugging Tips

### Common Issues

1. **Import errors**: Check for circular imports
2. **Type errors**: Verify protocol implementations
3. **Test failures**: Check for unintended side effects
4. **Pygame issues**: Ensure proper initialization in tests

### Verification Commands

```bash
# Check test status
hatch run test

# Check for type errors
hatch run type
hatch run type-pyright

# Check code quality
hatch run lint

# Full quality check
hatch run check
```

## Bug Reporting Workflow

When you encounter a bug:

1. **Create minimal test case**:
   ```python
   def test_bug_description():
       """Test for bug: brief description."""
       # Minimal failing example
   ```

2. **Verify it fails**:
   ```bash
   hatch run test tests/unit/test_new_bug.py
   ```

3. **Create GitHub issue**:
   - Use bug report template
   - Include test case and exact error
   - Reference related code

4. **Update documentation**:
   - Add bug to STATUS.md if blocking progress
   - Link issue number in code comments

## Measuring Completeness

**Primary measure**: Game functionality and code quality

### Metrics to Track:

```bash
# Test count
hatch run test | grep "passed"

# Code coverage
hatch run test-cov

# Type coverage
hatch run type-pyright-stats

# Line count (should decrease as we refactor)
hatch run count-lines
```

### After Each Phase:

1. **Phase completed**: e.g., "Phase 3: GameStateManager extraction"
2. **Test count**: e.g., "170 tests passing"
3. **Code metrics**: e.g., "GameController reduced from 479 to 473 lines"
4. **Coverage**: e.g., "60% coverage (target: 90%)"

## Session Management

If starting fresh from `/Users/jfreeman/Coding/xboing-python/`:
1. Review STATUS.md for current progress
2. Review PLAN.md for refactoring roadmap
3. Use workflow commands at the top of this document
4. Always run `hatch run check` before each micro-commit
5. There are no pre-existing issues that should be used to justify anything
6. Success is defined as 100%. Do not ask to settle for lower standards of success.

## Git Workflow

**Branch Strategy:**
- `master`: Stable, working code
- `refactor/*`: Feature branches for refactoring work
- Current branch: `refactor/game-protocol`

**Commit Standards:**
```bash
# Format: <type>(<scope>): <description>
# Examples:
refactor(state): Extract GameStateManager from GameController
test(collision): Add tests for ball-block collision edge cases
fix(paddle): Correct reverse control handling
docs(architecture): Update MVC documentation

# Always include co-authorship tag
🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

## Quality Philosophy

> **"If it doesn't pass all quality gates, it doesn't get committed."**

Every commit must pass:
1. All tests (170+ passing)
2. Type checking (mypy + pyright strict)
3. Linting (ruff)
4. Formatting (black)

No exceptions. Quality is not negotiable.
