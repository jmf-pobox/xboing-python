# Dependency Injection Design for XBoing

## Overview

XBoing uses the [injector](https://injector.readthedocs.io/) dependency injection (DI) framework as the exclusive mechanism for constructing and wiring all controllers, views, UI components, and core game objects. This approach eliminates manual dependency management and factory-based construction, resulting in a codebase that is more maintainable, testable, and extensible.

## How Dependency Injection Works in XBoing

### 1. **Injectable Classes**

All classes that require dependencies should use type-annotated constructor arguments. The `@inject` decorator from `injector` is optional if all arguments are type-annotated, but recommended for clarity.

Example:
```python
from injector import inject
from game.game_state import GameState

class GameController:
    @inject
    def __init__(self, game_state: GameState, ...):
        self.game_state = game_state
```

### 2. **DI Module and Providers**

The `XBoingModule` defines all providers for controllers, views, UI components, and core objects. Each provider method returns an instance of the required class, with all dependencies injected.

Example:
```python
from injector import Module, provider
from controllers.game_controller import GameController

class XBoingModule(Module):
    @provider
    def provide_game_controller(self, game_state: GameState, ... ) -> GameController:
        return GameController(game_state, ...)
```

### 3. **Application Composition**

In `xboing.py`, the application is composed by creating an injector and resolving all required components:

```python
from injector import Injector
from di_module import XBoingModule

injector = Injector([XBoingModule(...)])
game_controller = injector.get(GameController)
ui_manager = injector.get(UIManager)
# ...
```

The injector automatically resolves and injects all dependencies, including nested ones, according to the bindings in the module.

---

## Benefits for Unit Testing

- **Easier Mocking:** Dependencies can be overridden in test modules, allowing for easy injection of mocks or stubs.
- **Isolated Tests:** Each test can create an injector with only the required bindings, reducing test setup complexity.
- **No Manual Threading:** Tests do not need to manually construct deep dependency graphs; the injector handles it.

Example:
```python
from injector import Injector, Module, provider
from unittest.mock import Mock

class TestModule(Module):
    @provider
    def provide_game_state(self) -> GameState:
        return Mock(spec=GameState)

injector = Injector([TestModule()])
game_controller = injector.get(GameController)
# game_controller.game_state is now a mock
```

---

## How to Add New Dependencies or Components with DI

To add a new injectable class or component using the DI system:

1. **Annotate the Constructor**
   - Use `@injector.inject` (optional if all arguments are type-annotated) and provide precise type hints for all dependencies.
   - Example:
     ```python
     from injector import inject
     from game.game_state import GameState

     class MyComponent:
         @inject
         def __init__(self, game_state: GameState):
             self.game_state = game_state
     ```

2. **Add a Provider to the DI Module**
   - In `src/di_module.py`, add a `@provider` method to the `XBoingModule` for your new class.
   - Example:
     ```python
     from injector import provider
     from my_module import MyComponent

     class XBoingModule(Module):
         @provider
         def provide_my_component(self, game_state: GameState) -> MyComponent:
             return MyComponent(game_state)
     ```

3. **Request the Dependency Where Needed**
   - In any class that needs your new component, add it as a constructor argument with the correct type hint.
   - The injector will resolve and inject it automatically.

4. **(Optional) Override in Tests**
   - In your test modules, you can provide a test-specific provider for your component to inject mocks or stubs.

**Tips:**
- Always use precise type hints for all dependencies.
- Avoid using `Any` or `Optional` unless truly necessary.
- Do not use mutable default arguments.
- Register all new injectable classes in the DI module for consistency.

---

## Type Safety and Constructor Signatures in DI

When using dependency injection, it is critical to:

- **Use precise types for all constructor parameters.** Avoid using `Any`—always specify the actual class or interface expected (e.g., `game_state: GameState`).
- **Do not declare required dependencies as `Optional` or default them to `None`.** Only use `Optional[...] = None` for parameters that are truly optional for the logic of the class.
- **Do not use mutable default arguments (like `[]` or `{}`) in constructors.**
- **Required dependencies should always be required in the constructor signature.** This ensures the DI framework can resolve and inject them, and makes the contract of the class clear.

**Example (Best Practice):**
```python
from injector import inject
from game.game_state import GameState

class MyController:
    @inject
    def __init__(self, game_state: GameState):
        self.game_state = game_state
```

**Example (What to Avoid):**
```python
# Avoid this!
def __init__(self, game_state: Any = None):
    ...
```

This approach ensures type safety, better documentation, and full compatibility with the DI framework.

---

## References
- [injector documentation](https://injector.readthedocs.io/)
- [Dependency Injection in Python (Real Python)](https://realpython.com/dependency-injection-python/)