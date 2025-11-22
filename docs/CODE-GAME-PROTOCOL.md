# XBoing Game Protocol Design and Implementation Plan

## Overview

This document outlines a plan to standardize the interfaces of game objects in the XBoing Python port by introducing a set of protocols. Currently, the game objects (Ball, Block, Bullet, etc.) update themselves with the game clock but do not conform to a common interface that specifies this contract. This plan aims to formalize these interfaces for better maintainability, type safety, and testability.

## Current Architecture

The XBoing game architecture currently implements implicit patterns through duck typing:

- Game objects (Ball, Block, Bullet, Paddle) implement their own `update` methods with varying signatures
- Most objects implement `draw` methods to render themselves
- Objects implement position, collision, and state-tracking methods without a formal contract
- The `Controller` protocol exists, but no equivalent exists for game objects

This approach works but misses opportunities for better code organization, explicit contracts, and improved static type checking.

## Proposed Solution: Game Protocols

We propose defining a set of protocols that formalize the existing implicit contracts between game objects and their consumers (controllers, managers, and the game loop).

### Core Protocols

```python
from typing import Protocol, Tuple, Optional
import pygame

class Updateable(Protocol):
    """Protocol for objects that update with the game clock."""
    def update(self, delta_ms: float) -> None: ...

class Drawable(Protocol):
    """Protocol for objects that can draw themselves."""
    def draw(self, surface: pygame.Surface) -> None: ...

class Collidable(Protocol):
    """Protocol for objects that can be involved in collisions."""
    def get_rect(self) -> pygame.Rect: ...

class Positionable(Protocol):
    """Protocol for objects with a position in the game world."""
    def get_position(self) -> Tuple[float, float]: ...
    def set_position(self, x: float, y: float) -> None: ...

class Activatable(Protocol):
    """Protocol for objects with an active state."""
    def is_active(self) -> bool: ...
```

### Extended Game Object Protocol

For the main game objects that combine several of these aspects:

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class GameObject(Updateable, Drawable, Collidable, Positionable, Activatable, Protocol):
    """Combined protocol for complete game objects."""
    pass
```

## Implementation Plan

### Phase 1: Protocol Definition

1. Create a new module `src/xboing/game/protocols.py` containing the protocol definitions
2. Define all core protocols with comprehensive docstrings and type hints
3. Add unit tests for protocol conformance checking

### Phase 2: Update Existing Classes

1. Update `Ball` class to explicitly conform to the protocols
2. Update `Block` class to explicitly conform to the protocols
3. Update `Bullet` class to explicitly conform to the protocols
4. Update `Paddle` class to explicitly conform to the protocols
5. Standardize the `update` method signatures across all game objects

### Phase 3: Implement Managers and Controllers

1. Update manager classes to use the protocols for type hints
2. Update controllers to use protocol-based type hints
3. Add tests that verify protocol conformance

### Phase 4: Protocol Extensions

1. Add specialized protocols for specific game behaviors (e.g., `Shootable`, `Movable`)
2. Create composite protocols for common combinations

## Testing Strategy

### Unit Tests

We will significantly increase unit test coverage to ensure protocol compliance:

1. Create test fixtures that validate protocol implementation
2. Add tests for each protocol method in each implementing class
3. Create tests that exercise polymorphic behavior through protocols
4. Implement mock objects that implement the protocols for testing controllers

Example test pattern:

```python
def test_ball_implements_updateable_protocol():
    ball = Ball(100, 100)
    assert isinstance(ball, Updateable)
    # Test specific method behavior
    ball.update(16.67)  # Test with typical frame time
    # Assert expected state changes
```

### Type Checking

We will add comprehensive type checking to verify protocol conformance:

1. Set up MyPy with strict checking for all game modules
2. Use `@runtime_checkable` protocols to enable `isinstance` checks
3. Add type annotations to all relevant functions and methods
4. Verify type safety with the `mypy` and `pyright` tools

## Best Practices

### PEP Type Hint Best Practices

We will follow the latest Python type hinting best practices:

1. Use `typing.Protocol` for interface definitions (PEP 544)
2. Use `typing.TypeGuard` where appropriate for runtime type narrowing (PEP 647)
3. Use `typing.Annotated` for additional metadata on type hints (PEP 593)
4. Leverage Python 3.13 features like Self types (PEP 673) where applicable
5. Use `typing.Generic` for generic protocols where needed
6. Follow [type-hints/peps](https://typing.readthedocs.io/en/latest/source/protocols.html) guidance

### Documentation Standards

1. Every protocol will have comprehensive docstrings
2. Each protocol method will have detailed parameter and return type documentation
3. Example usage will be provided for each protocol
4. Protocols will be included in API documentation

## Integration with Hatch Workflow

The implementation of these protocols will be integrated with the [Hatch workflow](TOOL-HATCH.md) as follows:

1. Type checking will be added to the `check` command:
   ```bash
   hatch run typecheck
   ```

2. Protocol-specific tests will be runnable via:
   ```bash
   hatch run test -- -k protocol
   ```

3. Code coverage for protocols will be tracked:
   ```bash
   hatch run cov
   ```

4. Mypy will be configured in `pyproject.toml` with protocol-specific settings

## Timeline

1. **Phase 1 (Protocol Definition)**: 1 week
   - Create protocols.py
   - Write tests
   - Add documentation

2. **Phase 2 (Update Classes)**: 2 weeks
   - Update Ball (3 days)
   - Update Block (3 days)
   - Update Bullet (2 days)
   - Update Paddle (3 days)
   - Standardize interfaces (3 days)

3. **Phase 3 (Managers and Controllers)**: 1 week
   - Update all managers
   - Update controllers
   - Add tests

4. **Phase 4 (Extensions)**: 1 week
   - Add specialized protocols
   - Create composite protocols
   - Final documentation

## Benefits

Implementing these protocols will provide several key benefits:

1. **Type Safety**: Static type checking will catch errors where objects don't implement the expected interface
2. **Documentation**: Protocols clearly define the contract for new game objects
3. **Consistency**: All game objects will follow the same update pattern
4. **Polymorphism**: Code can treat different game objects uniformly through protocols
5. **Testability**: Mocking and testing will be simplified through protocol interfaces
6. **Maintainability**: New developers can understand the system architecture more easily

## Conclusion

Introducing formal protocols for game objects will significantly improve the XBoing codebase's maintainability, type safety, and testability. The implementation can be done incrementally, ensuring backward compatibility while moving toward a more robust architecture.

By following this plan, we will formalize the existing implicit contracts, improve code documentation, and make the architecture more explicit without requiring substantial changes to the existing code.
