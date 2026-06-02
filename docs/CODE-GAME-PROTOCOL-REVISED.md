# XBoing Game Protocol Design and Implementation Plan (Revised)

## Overview

This document outlines a plan to standardize the interfaces of game objects in the XBoing Python port by introducing a set of protocols. The goal is to formalize these interfaces for better maintainability, type safety, and testability, while also enabling the development of other similar games such as pinball using the same framework.

## Current Architecture

The XBoing game architecture currently implements a mix of inheritance and implicit patterns:

- A base class hierarchy exists with `GameShape` as the root, and `CircularGameShape` as a specialized subclass
- Game objects (Ball, Block, Bullet, Paddle) implement their own `update` methods with varying signatures
- Most objects implement `draw` methods to render themselves
- Objects implement position, collision, and state-tracking methods without a formal contract
- The `Controller` protocol exists, but game objects use inheritance rather than protocols
- An event-driven system is used for communication between components

This approach works but could be improved to better support reusability across different games.

## Proposed Solution: Game Protocols and Physics Components

We propose defining a set of protocols that formalize the existing implicit contracts between game objects and their consumers (controllers, managers, and the game loop), while also introducing physics components that can be reused across different games.

### Core Protocols

```python
from typing import Protocol, Tuple, Optional, List
import pygame

class Updateable(Protocol):
    """Protocol for objects that update with the game clock."""
    def update(self, delta_ms: float) -> List[pygame.event.Event]:
        """
        Update the object state based on the time delta.
        Returns a list of events that resulted from the update.
        """
        ...

class Drawable(Protocol):
    """Protocol for objects that can draw themselves."""
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the object on the given surface."""
        ...

class Collidable(Protocol):
    """Protocol for objects that can be involved in collisions."""
    def get_rect(self) -> pygame.Rect:
        """Get the object's collision rectangle."""
        ...
    
    def collides_with(self, other: 'Collidable') -> bool:
        """Check if this object collides with another collidable object."""
        ...

class Positionable(Protocol):
    """Protocol for objects with a position in the game world."""
    def get_position(self) -> Tuple[float, float]:
        """Get the object's current position as (x, y)."""
        ...
    
    def set_position(self, x: float, y: float) -> None:
        """Set the object's position to (x, y)."""
        ...

class Activatable(Protocol):
    """Protocol for objects with an active state."""
    def is_active(self) -> bool:
        """Check if the object is currently active."""
        ...
    
    def set_active(self, active: bool) -> None:
        """Set the object's active state."""
        ...
```

### Physics Components

To enhance reusability across different games, we introduce physics components that can be composed with game objects:

```python
class PhysicsComponent:
    """Component for handling physics behavior of game objects."""
    
    def __init__(self, position: Tuple[float, float], velocity: Tuple[float, float] = (0, 0),
                 acceleration: Tuple[float, float] = (0, 0), mass: float = 1.0):
        """Initialize the physics component with position, velocity, acceleration, and mass."""
        self.position = position
        self.velocity = velocity
        self.acceleration = acceleration
        self.mass = mass
    
    def update(self, delta_ms: float) -> Tuple[float, float]:
        """
        Update the physics state based on the time delta.
        Returns the new position.
        """
        # Update velocity based on acceleration
        self.velocity = (
            self.velocity[0] + self.acceleration[0] * delta_ms / 1000,
            self.velocity[1] + self.acceleration[1] * delta_ms / 1000
        )
        
        # Update position based on velocity
        self.position = (
            self.position[0] + self.velocity[0] * delta_ms / 1000,
            self.position[1] + self.velocity[1] * delta_ms / 1000
        )
        
        return self.position
    
    def apply_force(self, force: Tuple[float, float]) -> None:
        """Apply a force to the object, changing its acceleration based on mass."""
        self.acceleration = (
            self.acceleration[0] + force[0] / self.mass,
            self.acceleration[1] + force[1] / self.mass
        )
    
    def set_velocity(self, velocity: Tuple[float, float]) -> None:
        """Set the object's velocity."""
        self.velocity = velocity
    
    def get_velocity(self) -> Tuple[float, float]:
        """Get the object's current velocity."""
        return self.velocity
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

### Collision System

To handle collisions in a reusable way across different games:

```python
class CollisionSystem:
    """System for detecting and resolving collisions between game objects."""
    
    def __init__(self):
        """Initialize the collision system."""
        self.collidables = []
    
    def add_collidable(self, collidable: Collidable) -> None:
        """Add a collidable object to the system."""
        self.collidables.append(collidable)
    
    def remove_collidable(self, collidable: Collidable) -> None:
        """Remove a collidable object from the system."""
        if collidable in self.collidables:
            self.collidables.remove(collidable)
    
    def check_collisions(self) -> List[Tuple[Collidable, Collidable]]:
        """
        Check for collisions between all collidable objects.
        Returns a list of pairs of colliding objects.
        """
        collisions = []
        for i, obj1 in enumerate(self.collidables):
            for obj2 in self.collidables[i+1:]:
                if obj1.collides_with(obj2):
                    collisions.append((obj1, obj2))
        return collisions
```

## Implementation Plan

### Phase 1: Protocol and Component Definition

1. Create a new module `src/xboing/game/protocols.py` containing the protocol definitions
2. Create a new module `src/xboing/game/components.py` containing the physics component
3. Create a new module `src/xboing/game/collision.py` containing the collision system
4. Define all core protocols with comprehensive docstrings and type hints
5. Add unit tests for protocol conformance checking and component behavior

### Phase 2: Update Existing Classes

1. Update `Ball` class to use the physics component and conform to the protocols
2. Update `Block` class to conform to the protocols
3. Update `Bullet` class to use the physics component and conform to the protocols
4. Update `Paddle` class to conform to the protocols
5. Standardize the `update` method signatures across all game objects

### Phase 3: Implement Managers and Controllers

1. Update manager classes to use the protocols for type hints
2. Update controllers to use protocol-based type hints
3. Add tests that verify protocol conformance
4. Implement a collision manager that uses the collision system

### Phase 4: Protocol Extensions and Game-Specific Components

1. Add specialized protocols for specific game behaviors (e.g., `Shootable`, `Movable`)
2. Create composite protocols for common combinations
3. Implement game-specific components (e.g., `PinballPhysicsComponent`, `XBoingPhysicsComponent`)
4. Create example implementations for a pinball game using the same framework

## Testing Strategy

### Unit Tests

We will significantly increase unit test coverage to ensure protocol compliance:

1. Create test fixtures that validate protocol implementation
2. Add tests for each protocol method in each implementing class
3. Create tests that exercise polymorphic behavior through protocols
4. Implement mock objects that implement the protocols for testing controllers
5. Add tests for the physics component and collision system

Example test pattern:

```python
def test_ball_implements_updateable_protocol():
    ball = Ball(100, 100)
    assert isinstance(ball, Updateable)
    # Test specific method behavior
    events = ball.update(16.67)  # Test with typical frame time
    # Assert expected state changes and events
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

1. **Phase 1 (Protocol and Component Definition)**: 1 week
   - Create protocols.py, components.py, and collision.py
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

4. **Phase 4 (Extensions and Game-Specific Components)**: 2 weeks
   - Add specialized protocols
   - Create composite protocols
   - Implement game-specific components
   - Create pinball game example
   - Final documentation

## Benefits

Implementing these protocols and components will provide several key benefits:

1. **Type Safety**: Static type checking will catch errors where objects don't implement the expected interface
2. **Documentation**: Protocols clearly define the contract for new game objects
3. **Consistency**: All game objects will follow the same update pattern
4. **Polymorphism**: Code can treat different game objects uniformly through protocols
5. **Testability**: Mocking and testing will be simplified through protocol interfaces
6. **Maintainability**: New developers can understand the system architecture more easily
7. **Reusability**: Physics components and collision system can be reused across different games
8. **Extensibility**: New game types can be created by implementing the same protocols and using the same components

## Framework Reusability for Other Games

The proposed design enhances reusability for other games in several ways:

1. **Physics Components**: The physics component can be reused or extended for different games with different physics behaviors
2. **Collision System**: The collision system provides a reusable way to detect and resolve collisions
3. **Protocols**: The protocols define clear interfaces that can be implemented by different game objects
4. **Event System**: The event-driven architecture allows for flexible communication between components
5. **Game-Specific Extensions**: Game-specific behaviors can be implemented as specialized protocols or components

### Example: Pinball Game

A pinball game could be implemented using the same framework by:

1. Implementing the same protocols for pinball-specific objects (flippers, bumpers, targets)
2. Using the physics component with pinball-specific parameters
3. Using the collision system for detecting collisions between the ball and pinball elements
4. Extending the event system with pinball-specific events
5. Reusing the same UI components and controllers with pinball-specific views

## Conclusion

Introducing formal protocols, physics components, and a collision system will significantly improve the XBoing codebase's maintainability, type safety, testability, and reusability for other games. The implementation can be done incrementally, ensuring backward compatibility while moving toward a more robust architecture.

By following this plan, we will formalize the existing implicit contracts, improve code documentation, and make the architecture more explicit without requiring substantial changes to the existing code. The addition of physics components and a collision system will enhance reusability for other games like pinball.