# Dependency Injection Design for XBoing

## Overview

XBoing uses the [injector](https://injector.readthedocs.io/) dependency injection (DI) framework as the exclusive mechanism for constructing and wiring all controllers, views, UI components, and core game objects. This approach eliminates manual dependency management and factory-based construction, resulting in a codebase that is more maintainable, testable, and extensible.

## Registry Pattern for DI in XBoing

### Canonical Instance Registry

- **All core managers, controllers, and renderers are created up front** (in the main application setup or a dedicated setup function).
- These canonical instances are **passed to the DI module (`XBoingModule`) via its constructor**.
- **All provider methods in the DI module return these pre-initialized instances from instance variables** (e.g., `self._ball_manager`, `self._audio_manager`, etc.).
- **Provider methods must not accept dependencies as parameters**; they must always return the instance from `__init__`.
- This pattern guarantees **singleton-like behavior** for all core objects, eliminates accidental duplication, and ensures all consumers receive the same instance.

### Example: Registry Provider
```python
from injector import Module, provider
from game.ball_manager import BallManager

class XBoingModule(Module):
    def __init__(self, ball_manager: BallManager, ...):
        self._ball_manager = ball_manager
        ...

    @provider
    def provide_ball_manager(self) -> BallManager:
        """Return the canonical BallManager instance."""
        return self._ball_manager
```

### Why Not Use Parameters in Providers?
- If a provider method takes a dependency as a parameter (e.g., `ball_manager: BallManager`), the DI system may try to resolve it by type and create a new instance if not explicitly bound.
- This can break the singleton/registry pattern and lead to subtle bugs, such as multiple instances of a manager being used in different parts of the app.
- **Always use the instance variable from `__init__` in providers.**

## Exception: Composite/Factory Providers and DI Cycles

Some objects, such as `ControllerManager`, are composites that must be constructed after all their dependencies are available. These may also be involved in DI cycles (e.g., `ControllerManager` needs a reference to `game_over_controller`, which in turn needs a reference to `ControllerManager`).

### Example: Factory/Composite Provider
```python
@provider
def provide_controller_manager(
    self,
    game_controller: GameController,
    instructions_controller: InstructionsController,
    level_complete_controller: LevelCompleteController,
    game_over_controller: GameOverController,
) -> ControllerManager:
    """Provide a ControllerManager instance for managing controllers."""
    manager = ControllerManager()
    manager.register_controller("game", game_controller)
    manager.register_controller("instructions", instructions_controller)
    manager.register_controller("level_complete", level_complete_controller)
    manager.register_controller("game_over", game_over_controller)
    manager.set_controller("game")
    # Set controller_manager on game_over_controller to break DI cycle
    game_over_controller.controller_manager = manager
    return manager
```
- This pattern is only used when necessary to wire up dependencies or break DI cycles.
- For all other managers and core objects, use the registry pattern.

## Summary Table: Registry vs. Factory Provider Patterns

| Provider Type         | Pattern Used         | When to Use                                    |
|----------------------|---------------------|------------------------------------------------|
| Core managers        | Registry            | Only one instance, no wiring needed             |
| ControllerManager    | Factory/composite   | Needs to wire up other controllers, breaks DI cycle |

## Benefits for Unit Testing

- **Easier Mocking:** Dependencies can be overridden in test modules, allowing for easy injection of mocks or stubs.
- **Isolated Tests:** Each test can create an injector with only the required bindings, reducing test setup complexity.
- **No Manual Threading:** Tests do not need to manually construct deep dependency graphs; the injector handles it.

## How to Add New Dependencies or Components with the Registry Pattern

1. **Create the Instance Up Front**
   - In your main setup or a dedicated setup function, create the canonical instance of your new manager/component.
2. **Pass It to the DI Module**
   - Add it as a parameter to the `XBoingModule` constructor and store it as an instance variable.
3. **Add a Provider**
   - In `XBoingModule`, add a `@provider` method that returns the instance variable.
   - Do not accept the dependency as a parameter in the provider.
4. **Request the Dependency Where Needed**
   - In any class that needs your new component, add it as a constructor argument with the correct type hint. The injector will resolve and inject it automatically.
5. **(Optional) Override in Tests**
   - In your test modules, you can provide a test-specific provider for your component to inject mocks or stubs.

**Tips:**
- Always use precise type hints for all dependencies.
- Avoid using `Any` or `Optional` unless truly necessary.
- Do not use mutable default arguments.
- Register all new injectable classes in the DI module for consistency.

## Type Safety and Constructor Signatures in DI

- **Use precise types for all constructor parameters.** Avoid using `Any`—always specify the actual class or interface expected (e.g., `game_state: GameState`).
- **Do not declare required dependencies as `Optional` or default them to `None`.** Only use `Optional[...] = None` for parameters that are truly optional for the logic of the class.
- **Do not use mutable default arguments (like `[]` or `{}`) in constructors.**
- **Required dependencies should always be required in the constructor signature.** This ensures the DI framework can resolve and inject them, and makes the contract of the class clear.

## References
- [injector documentation](https://injector.readthedocs.io/)
- [Dependency Injection in Python (Real Python)](https://realpython.com/dependency-injection-python/)