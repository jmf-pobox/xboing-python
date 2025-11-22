# Game Controller Decomposition Plan (Revised)

## Overview

The `GameController` class currently handles too many responsibilities, making it difficult to maintain and test. This document outlines a revised plan to decompose the `GameController` into smaller, more focused components, with a phased approach that builds on the existing architecture and protocols.

## Current State Assessment

The `GameController` currently handles:
- Game state management
- Input handling
- Collision detection and response
- Event management
- Game loop updates
- Special power-up effects (sticky paddle, reverse controls)
- Level completion logic
- Life management

This monolithic design leads to several issues:
1. **High Coupling**: Changes to one aspect often affect others
2. **Testing Difficulty**: Hard to test individual components in isolation
3. **Code Duplication**: Similar logic appears in multiple methods
4. **Maintenance Challenges**: Large methods with mixed responsibilities
5. **Limited Reusability**: Components are tightly integrated

## Current Status (as of June 2023)

The decomposition of the `GameController` is progressing according to the phased approach outlined in this document. Here's the current status of each phase:

### Phase 1: Complete Collision System Integration ✅

- **Status: Completed**
- The `CollisionSystem` has been fully implemented and integrated into the `GameController`
- The `CollisionHandlers` class has been created and handles all collision logic:
  - Ball-Block collisions
  - Ball-Paddle collisions
  - Bullet-Block collisions
  - Bullet-Ball collisions
- Special block effects are handled by the `CollisionHandlers` class
- Collision handlers are properly registered in the `GameController`
- The `_register_all_collidables` method centralizes collidable registration

### Phase 2: Input Handling Extraction ✅

- **Status: Completed**
- The `PaddleInputController` has been implemented and handles:
  - Keyboard-based paddle movement
  - Mouse-based paddle movement
  - Reverse controls functionality
- The `GameInputController` has been implemented and handles:
  - Game control events (pause, quit)
  - Ammo firing and ball launching
  - Debug keys
  - Stuck ball timer management
- Both controllers are properly integrated with the `GameController`

### Phase 3: Game State Management Extraction ❌

- **Status: Not Started**
- The `GameStateManager` has not been implemented yet
- Life management and level completion logic are still handled directly in the `GameController`
- Event handling for game state changes is still in the `GameController`

### Phase 4: Power-Up Management Extraction ❌

- **Status: Not Started**
- The `PowerUpManager` has not been implemented yet
- Power-up effects and state are currently handled by the `CollisionHandlers` class
- Special effects like sticky paddle and reverse controls are managed through properties in the `GameController`

### Phase 5: Final Integration ❌

- **Status: Not Started**
- The `GameController` still handles many responsibilities that should be delegated to specialized components
- Tests have not been updated to reflect the new architecture
- Documentation needs to be updated to reflect the current state of the implementation

## Progress So Far

Significant progress has already been made:
- The `CollisionSystem` has been implemented and integrated
- Game objects implement the `Collidable` protocol
- Collision handlers are registered in the `GameController`
- The `_register_all_collidables` method centralizes collidable registration
- Input handling has been extracted to dedicated controllers

## Revised Decomposition Strategy

### Phase 0: Event System Implementation ✅

#### 0.1 Create EventBus

```python
class EventBus:
    """Centralized event system for component communication."""
    
    def __init__(self) -> None:
        self._subscribers: Dict[Type[Event], List[Callable[[Event], None]]] = {}
        self._event_queue: List[Event] = []
    
    def subscribe(self, event_type: Type[Event], handler: Callable[[Event], None]) -> None:
        """Subscribe to an event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
    
    def post(self, event: Event) -> None:
        """Post an event to the queue."""
        self._event_queue.append(event)
    
    def process_events(self) -> None:
        """Process all events in the queue."""
        while self._event_queue:
            event = self._event_queue.pop(0)
            event_type = type(event)
            if event_type in self._subscribers:
                for handler in self._subscribers[event_type]:
                    handler(event)
```

#### 0.2 Define Event Types

```python
@dataclass
class GameEvent:
    """Base class for all game events."""
    timestamp: float = field(default_factory=time.time)

@dataclass
class CollisionEvent(GameEvent):
    """Event fired when a collision occurs."""
    collider: Collidable
    collidee: Collidable
    collision_type: CollisionType

@dataclass
class PowerUpEvent(GameEvent):
    """Event fired when a power-up is activated."""
    power_up_type: str
    duration: float
```

### Phase 1: Component Lifecycle Management

#### 1.1 Create Component Base Class

```python
class Component:
    """Base class for all game components."""
    
    def __init__(self, event_bus: EventBus) -> None:
        self.event_bus = event_bus
        self._active = False
    
    def initialize(self) -> None:
        """Initialize the component."""
        self._active = True
        self._register_event_handlers()
    
    def cleanup(self) -> None:
        """Clean up component resources."""
        self._active = False
        self._unregister_event_handlers()
    
    def _register_event_handlers(self) -> None:
        """Register event handlers with the event bus."""
        pass
    
    def _unregister_event_handlers(self) -> None:
        """Unregister event handlers from the event bus."""
        pass
    
    @property
    def is_active(self) -> bool:
        """Check if the component is active."""
        return self._active
```

#### 1.2 Implement Component Manager

```python
class ComponentManager:
    """Manages component lifecycle and dependencies."""
    
    def __init__(self, event_bus: EventBus) -> None:
        self.event_bus = event_bus
        self._components: Dict[str, Component] = {}
    
    def register_component(self, name: str, component: Component) -> None:
        """Register a component with the manager."""
        self._components[name] = component
    
    def initialize_component(self, name: str) -> None:
        """Initialize a component."""
        if name in self._components:
            self._components[name].initialize()
    
    def cleanup_component(self, name: str) -> None:
        """Clean up a component."""
        if name in self._components:
            self._components[name].cleanup()
```

### Phase 2: Protocol Implementation

#### 2.1 Define Game Object Protocols

```python
class GameObject(Updateable, Drawable, Collidable, Positionable, Activatable):
    """Protocol for all game objects."""
    pass

class PhysicsObject(Protocol):
    """Protocol for objects with physics behavior."""
    def apply_force(self, force: Vector2) -> None: ...
    def update_physics(self, delta_ms: float) -> None: ...
```

#### 2.2 Implement Protocol Compliance

```python
class Ball(Component, GameObject):
    """Ball game object implementing required protocols."""
    
    def __init__(self, event_bus: EventBus, position: Vector2, radius: float) -> None:
        super().__init__(event_bus)
        self.position = position
        self.radius = radius
        self.velocity = Vector2(0, 0)
    
    def update(self, delta_ms: float) -> List[Event]:
        """Update ball state."""
        if not self.is_active:
            return []
        self.update_physics(delta_ms)
        return self._check_collisions()
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the ball."""
        if not self.is_active:
            return
        pygame.draw.circle(surface, (255, 255, 255), 
                         (int(self.position.x), int(self.position.y)), 
                         int(self.radius))
```

### Phase 3: Component Extraction

#### 3.1 Physics Component

```python
class PhysicsComponent(Component):
    """Handles physics simulation for game objects."""
    
    def __init__(self, event_bus: EventBus) -> None:
        super().__init__(event_bus)
        self._objects: List[PhysicsObject] = []
    
    def add_object(self, obj: PhysicsObject) -> None:
        """Add a physics object to the simulation."""
        self._objects.append(obj)
    
    def update(self, delta_ms: float) -> None:
        """Update physics simulation."""
        if not self.is_active:
            return
        for obj in self._objects:
            obj.update_physics(delta_ms)
```

#### 3.2 Collision Component

```python
class CollisionComponent(Component):
    """Handles collision detection and response."""
    
    def __init__(self, event_bus: EventBus) -> None:
        super().__init__(event_bus)
        self._collidables: List[Collidable] = []
    
    def add_collidable(self, obj: Collidable) -> None:
        """Add a collidable object."""
        self._collidables.append(obj)
    
    def update(self, delta_ms: float) -> None:
        """Check for collisions."""
        if not self.is_active:
            return
        for i, obj1 in enumerate(self._collidables):
            for obj2 in self._collidables[i+1:]:
                if self._check_collision(obj1, obj2):
                    self.event_bus.post(CollisionEvent(obj1, obj2))
```

### Phase 4: Game Controller Refactoring

#### 4.1 Simplified GameController

```python
class GameController(Controller):
    """Coordinator for game components."""
    
    def __init__(self, event_bus: EventBus) -> None:
        self.event_bus = event_bus
        self.component_manager = ComponentManager(event_bus)
        self._initialize_components()
    
    def _initialize_components(self) -> None:
        """Initialize all game components."""
        # Create components
        physics = PhysicsComponent(self.event_bus)
        collision = CollisionComponent(self.event_bus)
        input_handler = InputComponent(self.event_bus)
        
        # Register components
        self.component_manager.register_component("physics", physics)
        self.component_manager.register_component("collision", collision)
        self.component_manager.register_component("input", input_handler)
        
        # Initialize components
        for name in ["physics", "collision", "input"]:
            self.component_manager.initialize_component(name)
    
    def update(self, delta_ms: float) -> None:
        """Update game state."""
        self.event_bus.process_events()
        for component in self.component_manager._components.values():
            if component.is_active:
                component.update(delta_ms)
    
    def cleanup(self) -> None:
        """Clean up game resources."""
        for name in self.component_manager._components:
            self.component_manager.cleanup_component(name)
```

### Phase 5: Testing Strategy

#### 5.1 Unit Testing

```python
class TestPhysicsComponent:
    def test_physics_update(self):
        # Arrange
        event_bus = EventBus()
        physics = PhysicsComponent(event_bus)
        ball = Mock(spec=PhysicsObject)
        physics.add_object(ball)
        
        # Act
        physics.update(16.67)
        
        # Assert
        ball.update_physics.assert_called_once_with(16.67)

class TestCollisionComponent:
    def test_collision_detection(self):
        # Arrange
        event_bus = EventBus()
        collision = CollisionComponent(event_bus)
        ball1 = Mock(spec=Collidable)
        ball2 = Mock(spec=Collidable)
        collision.add_collidable(ball1)
        collision.add_collidable(ball2)
        
        # Act
        collision.update(16.67)
        
        # Assert
        # Verify collision events were posted
```

#### 5.2 Integration Testing

```python
class TestGameController:
    def test_component_interaction(self):
        # Arrange
        event_bus = EventBus()
        controller = GameController(event_bus)
        
        # Act
        controller.update(16.67)
        
        # Assert
        # Verify components were updated
        # Verify events were processed
```

### Phase 6: Performance Considerations

1. **Event Queue Management**
   - Implement event pooling to reduce garbage collection
   - Use fixed-size queues for high-frequency events
   - Batch similar events

2. **Component Updates**
   - Implement spatial partitioning for collision detection
   - Use object pooling for frequently created/destroyed objects
   - Implement update frequency control

3. **Memory Management**
   - Implement proper cleanup of unused components
   - Use weak references for event handlers
   - Implement resource pooling

### Phase 7: Error Handling

1. **Component Errors**
   - Implement error boundaries for components
   - Add error recovery mechanisms
   - Log component errors

2. **Event Handling**
   - Add event validation
   - Implement event error handling
   - Add event retry mechanisms

3. **State Recovery**
   - Implement state snapshots
   - Add state recovery mechanisms
   - Implement error reporting

## Implementation Timeline

1. **Phase 0-1**: Event System and Component Lifecycle (2 weeks)
2. **Phase 2-3**: Protocol Implementation and Component Extraction (3 weeks)
3. **Phase 4**: Game Controller Refactoring (2 weeks)
4. **Phase 5**: Testing Implementation (2 weeks)
5. **Phase 6-7**: Performance and Error Handling (2 weeks)

## Success Criteria

1. **Code Quality**
   - All components follow protocol requirements
   - Test coverage > 90%
   - No circular dependencies
   - Clear component boundaries

2. **Performance**
   - 60 FPS maintained
   - Memory usage stable
   - No garbage collection spikes

3. **Maintainability**
   - Clear documentation
   - Easy to add new components
   - Simple to modify existing components

4. **Error Handling**
   - Graceful error recovery
   - Clear error messages
   - Proper error logging

## Next Steps

1. Begin with Phase 1 by extracting the `CollisionHandlers` class
2. Update tests to verify collision handling
3. Proceed through phases in order, ensuring tests pass at each step
4. Document design decisions and component interactions
5. Review and refine the architecture as implementation progresses
