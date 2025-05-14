# Dependency Injection Design Proposal for XBoing

## Overview

This document proposes the adoption of the [injector](https://injector.readthedocs.io/) dependency injection (DI) framework to simplify and standardize the construction and wiring of UI components, controllers, views, and game state in XBoing. The goal is to reduce manual dependency management, improve testability, and make the codebase more maintainable and extensible.

---

## Current Construction Pattern

Currently, the construction and wiring of core objects (UI, controllers, views, game state, etc.) is handled manually in `main.py`, `ui_factory.py`, and `controller_factory.py`. Dependencies are passed explicitly through constructors, and factories are used to centralize setup logic. For example:

- `main.py` creates the event bus, game state, audio manager, window, renderer, input manager, layout, and then passes these to factories.
- `UIFactory` and `ControllerFactory` are responsible for instantiating and wiring up UI components and controllers, respectively.
- Each controller and view receives its dependencies via constructor arguments, which are manually threaded through the call stack.

While this approach is explicit, it leads to:
- Boilerplate code for passing dependencies.
- Difficulty in swapping implementations (e.g., for testing or feature changes).
- Tight coupling between construction logic and application logic.

---

## Proposed DI Approach with `injector`

### 1. **Define Injectable Classes**

Annotate constructors with `@injector.inject` and use type hints for dependencies. For example:

```python
from injector import inject

class GameState:
    @inject
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus

class GameController:
    @inject
    def __init__(self, game_state: GameState, level_manager: LevelManager, ...):
        ...
```

### 2. **Create an Injector Module**

Define a module that binds interfaces to implementations and configures singletons or factories as needed:

```python
from injector import Module, singleton, provider

class XBoingModule(Module):
    @singleton
    @provider
    def provide_event_bus(self) -> EventBus:
        return EventBus()

    @singleton
    @provider
    def provide_game_state(self, event_bus: EventBus) -> GameState:
        return GameState(event_bus)

    # Add providers for controllers, UIManager, UIFactory, etc.
```

### 3. **Application Composition**

In `main.py`, replace manual construction with injector-based resolution:

```python
from injector import Injector
from my_di_module import XBoingModule

injector = Injector([XBoingModule()])
game_controller = injector.get(GameController)
ui_manager = injector.get(UIManager)
# ...
```

The injector will automatically resolve and inject all dependencies, including nested ones, according to the bindings in the module.

### 4. **Wiring UI and Controllers**

- Factories like `UIFactory` and `ControllerFactory` can be replaced or refactored to use DI, or retained for grouping logic but with dependencies injected.
- Views and UI components can be injected with their dependencies (e.g., event bus, game state, renderers) without manual wiring.

---

## Benefits for Unit Testing

- **Easier Mocking:** Dependencies can be overridden in test modules, allowing for easy injection of mocks or stubs.
- **Isolated Tests:** Each test can create an injector with only the required bindings, reducing test setup complexity.
- **No Manual Threading:** Tests do not need to manually construct deep dependency graphs; the injector handles it.
- **Example:**

```python
from injector import Injector, Module, provider
from unittest.mock import Mock

class TestModule(Module):
    @provider
    def provide_event_bus(self) -> EventBus:
        return Mock(spec=EventBus)

injector = Injector([TestModule()])
game_controller = injector.get(GameController)
# game_controller.event_bus is now a mock
```

---

## Migration Considerations

- **Incremental Adoption:** DI can be introduced gradually, starting with controllers and game state, then expanding to UI and views.
- **Refactoring Required:** Constructors must use type hints and (optionally) the `@inject` decorator.
- **Factory Classes:** May be retained for grouping, but should delegate instantiation to the injector.
- **Configuration:** Global settings, asset paths, and other configuration can be provided via DI as well.

---

## Open Questions for Feedback

- Should all controllers and views be managed by DI, or only core game logic? All controllers and views.
- Should UIFactory/ControllerFactory be refactored or removed? Refactored.
- Are there any components that should remain manually constructed? No.
- Preferences for singleton vs. factory scope for certain objects?  Factory scope.

---

## Type Safety and Constructor Signatures in DI

When using dependency injection, it is critical to:

- **Use precise types for all constructor parameters.** Avoid using `Any`—always specify the actual class or interface expected (e.g., `game_state: GameState`, `balls: list[Ball]`).
- **Do not declare required dependencies as `Optional` or default them to `None`.** Only use `Optional[...] = None` for parameters that are truly optional for the logic of the class.
- **Do not use mutable default arguments (like `[]` or `{}`) in constructors.**
- **Required dependencies should always be required in the constructor signature.** This ensures the DI framework can resolve and inject them, and makes the contract of the class clear.

**Example (Best Practice):**
```python
from injector import inject
from game.game_state import GameState
from game.ball import Ball

class MyController:
    @inject
    def __init__(self, game_state: GameState, balls: list[Ball]):
        self.game_state = game_state
        self.balls = balls
```

**Example (What to Avoid):**
```python
# Avoid this!
def __init__(self, game_state: Any = None, balls: list[Any] = []):
    ...
```

This approach ensures type safety, better documentation, and full compatibility with the DI framework.

---

## References
- [injector documentation](https://injector.readthedocs.io/)
- [Dependency Injection in Python (Real Python)](https://realpython.com/dependency-injection-python/)

---