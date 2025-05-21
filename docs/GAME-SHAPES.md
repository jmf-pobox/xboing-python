# GameShape Refactor Plan for XBoing Python

_Last updated: [auto-generated]_ 

## Overview

This document outlines a detailed plan to refactor all core game objects (Ball, Bullet, Block, Paddle, etc.) to use a unified `GameShape` base class hierarchy. The goal is to eliminate code duplication, improve maintainability, and enable future extensibility for new game object types.

---

## Rationale

- **Eliminate Duplication:** Ball, Bullet, Block, and Paddle all manage position, rect, and collision logic in similar ways.
- **Improve Maintainability:** Centralizing shared logic makes it easier to update and extend.
- **Enable Extensibility:** New shapes (e.g., elliptical, polygonal, power-ups) can be added with minimal changes.
- **Polymorphism:** Collision, drawing, and update logic can be handled via base class interfaces.

---

## Proposed Class Hierarchy

```
GameShape (ABC)
│
├── CircularGameShape (GameShape)
│     └── Ball (CircularGameShape)
│
├── Bullet (GameShape)
├── Block (GameShape)
└── Paddle (GameShape)
```

- **GameShape (ABC):**
  - Abstract base class for all game objects with a `rect` and position.
  - Defines interface for `get_rect()`, `update_rect()`, `get_position()`, and possibly `draw()`.
- **CircularGameShape:**
  - Inherits from `GameShape`.
  - Adds `radius` and circular-specific logic (e.g., collision, drawing).
  - Used for `Ball` (and possibly power-ups).
- **Bullet, Block, Paddle:**
  - Inherit directly from `GameShape`.
  - Use rectangular logic for position, collision, and drawing.
- **Ball:**
  - Inherits from `CircularGameShape`.
  - Implements/extends circular-specific logic.

---

## Migration Steps

### 1. Define Base Classes

- Create `GameShape` as an abstract base class (ABC) in `src/xboing/game/game_shape.py`:
  - Attributes: `x`, `y`, `rect`
  - Methods: `get_rect()`, `update_rect()`, `get_position()`, `draw()` (abstract or default)

- Create `CircularGameShape` as a subclass for circular objects:
  - Adds `radius`, circular collision/drawing logic

### 2. Refactor Existing Classes

- **Ball:**
  - Inherit from `CircularGameShape`.
  - Remove duplicated rect/radius logic now handled by the base class.
  - Use base class methods for position, rect, and drawing where possible.

- **Bullet:**
  - Inherit from `GameShape` (as a rectangle, not a circle).
  - Remove circular logic if present.
  - Use base class methods for position, rect, and drawing.

- **Block, Paddle:**
  - Inherit from `GameShape`.
  - Ensure they use the base class's rect/position logic.
  - Move any shared logic to the base class as needed.

### 3. Update Instantiations and Type Hints

- Update all code that instantiates or type-checks these objects to use the new base classes.
- Update type hints in methods that accept any game shape (e.g., collision systems).

### 4. Refactor Collision and Drawing Logic

- Refactor collision detection to use polymorphic methods:
  - `collides_with(other: GameShape) -> bool`
  - Each subclass implements its own collision logic (circle-circle, rect-rect, circle-rect, etc.).
- Refactor drawing logic to use the base class interface.

### 5. Update Tests

- Update or add tests for the new class hierarchy and behaviors.
- Ensure all existing tests pass after the refactor.

---

## Example Base Class Sketch

```python
# src/xboing/game/game_shape.py
import pygame
from abc import ABC, abstractmethod
from typing import Tuple

class GameShape(ABC):
    def __init__(self, x: float, y: float, width: int, height: int):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(int(self.x), int(self.y), width, height)

    def update_rect(self) -> None:
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def get_rect(self) -> pygame.Rect:
        return self.rect

    def get_position(self) -> Tuple[float, float]:
        return (self.x, self.y)

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        pass

class CircularGameShape(GameShape):
    def __init__(self, x: float, y: float, radius: int):
        super().__init__(x, y, radius * 2, radius * 2)
        self.radius = radius

    def update_rect(self) -> None:
        self.rect.x = int(self.x - self.radius)
        self.rect.y = int(self.y - self.radius)

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x), int(self.y)), self.radius)
```

---

## Future Extensibility

- **New Shapes:** Add `PolygonGameShape`, `EllipseGameShape`, etc., as needed.
- **Power-ups/Enemies:** Inherit from the appropriate base class for consistent behavior.
- **Collision System:** Can use `isinstance` or polymorphic methods for shape-specific collision logic.

---

## Risks and Mitigations

- **Refactor Risk:** Touches many core files; requires careful, incremental testing.
- **Initial Time Investment:** Estimated 1-2 days for a careful, well-tested refactor.
- **Potential for Subtle Bugs:** Ensure all collision and drawing logic is migrated and tested.

---

## Checklist

- [ ] Define `GameShape` and `CircularGameShape` base classes
- [ ] Refactor `Ball`, `Bullet`, `Block`, `Paddle` to use new base classes
- [ ] Update all instantiations and type hints
- [ ] Refactor collision and drawing logic to use polymorphism
- [ ] Update/add tests for new hierarchy
- [ ] Ensure all tests pass

---

_This plan should be reviewed and updated as the refactor progresses._ 