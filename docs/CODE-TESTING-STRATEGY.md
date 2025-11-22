# XBoing Testing Strategy

## Overview

XBoing uses pytest for unit testing, with a focus on testing both individual components and their interactions. The testing strategy emphasizes:

1. Testing real objects where possible
2. Using mocks only when necessary
3. Testing both success and failure paths
4. Ensuring proper cleanup between tests
5. Maintaining test isolation

## Test Configuration

### pytest.ini

The project uses a custom pytest configuration that:
- Enables strict mode for type checking
- Sets up test timeouts
- Configures test discovery patterns
- Sets up logging for tests

### Timeout Configuration

The project uses `pytest-timeout` to prevent tests from hanging indefinitely. This is particularly important for:

1. **Physics Tests**
   - Infinite loops in collision detection
   - Recursive position/velocity updates
   - Deadlocks in event handling

2. **Event System Tests**
   - Event queue processing
   - Event handler registration
   - Event propagation

3. **Resource Loading Tests**
   - Asset loading
   - File system operations
   - Network requests

#### Configuration

The timeout is configured in `pytest.ini`:
```ini
[pytest]
timeout = 5
timeout_method = thread
```

This sets a 5-second timeout for all tests using the thread-based timeout method.

#### Usage Examples

1. **Default Timeout**
```python
def test_ball_physics():
    ball = Ball(10, 10)
    ball.set_velocity(5, 0)
    ball.update(16.67)  # Will timeout after 5 seconds if stuck
```

2. **Custom Timeout**
```python
@pytest.mark.timeout(10)  # Override default timeout
def test_complex_collision():
    # Complex collision test that might need more time
    pass
```

3. **Disable Timeout**
```python
@pytest.mark.timeout(0)  # Disable timeout
def test_long_running_operation():
    # Test that intentionally takes a long time
    pass
```

#### Common Timeout Issues

1. **Recursive Calls**
   - Infinite recursion in position/velocity updates
   - Solution: Ensure proper base cases and termination conditions
   ```python
   # Bad - can cause timeout
   def set_position(self, x, y):
       self.set_position(x, y)  # Infinite recursion
   
   # Good
   def set_position(self, x, y):
       self._x = x
       self._y = y
       self.update_rect()
   ```

2. **Event Loop Deadlocks**
   - Circular event dependencies
   - Solution: Use event queue with proper processing limits
   ```python
   # Bad - can cause timeout
   def handle_event(self, event):
       self.handle_event(event)  # Infinite loop
   
   # Good
   def handle_event(self, event):
       self.event_queue.append(event)
       self.process_events()  # With proper limits
   ```

3. **Resource Loading**
   - Missing assets causing infinite retries
   - Solution: Implement proper fallback behavior
   ```python
   # Bad - can cause timeout
   def load_asset(self, path):
       while not self.asset_loaded:
           self.retry_load()  # Infinite retry
   
   # Good
   def load_asset(self, path):
       try:
           return self._load_asset(path)
       except AssetError:
           return self.get_fallback_asset()
   ```

#### Best Practices

1. **Timeout Selection**
   - Use default timeout (5s) for most tests
   - Increase timeout for complex operations
   - Disable timeout only when necessary

2. **Debugging Timeouts**
   - Check for infinite loops
   - Verify resource cleanup
   - Look for deadlocks in event handling
   - Monitor resource usage

3. **Preventing Timeouts**
   - Implement proper termination conditions
   - Use timeouts in event processing
   - Handle resource loading failures gracefully
   - Test with realistic data sizes

4. **CI/CD Considerations**
   - Set appropriate timeout for CI environment
   - Monitor test execution times
   - Fail fast on timeout
   - Log timeout details for debugging

### Test Organization

Tests are organized in a `tests/` directory mirroring the source structure:
```
tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
└── conftest.py     # Shared test fixtures
```

## Testing Approach

### Real Objects vs Mocks

#### When to Use Real Objects

1. **Game Objects (Ball, Paddle, Block)**
   - Use real objects to test actual physics and collision behavior
   - Ensures realistic interaction between components
   - Helps catch integration issues early

2. **Physics Components**
   - Test with real physics calculations
   - Verify position and velocity updates
   - Test boundary conditions and edge cases

3. **Asset Loading**
   - Use real asset loading to verify file paths and formats
   - Test fallback behavior when assets are missing

#### When to Use Mocks

1. **External Dependencies**
   - Pygame surface and event handling
   - File system operations
   - Network calls (if any)

2. **Complex Dependencies**
   - Game state when testing controllers
   - Audio system when testing sound effects
   - Input handling when testing game logic

3. **Performance-Critical Components**
   - Rendering system
   - Collision detection in isolation

### Common Test Pitfalls

1. **Physics Synchronization**
   - Always ensure position/velocity are synchronized between objects and their physics components
   - Use `set_position()` and `set_velocity()` instead of directly modifying physics attributes
   - Verify both object attributes and physics component state

2. **Event Handling**
   - Test both event generation and event handling
   - Verify event order and timing
   - Check event data consistency

3. **State Management**
   - Reset state between tests
   - Don't assume test execution order
   - Clean up resources properly

4. **Boundary Conditions**
   - Test edge cases (e.g., ball at screen boundaries)
   - Verify collision detection at boundaries
   - Test with minimum and maximum values

5. **Timing and Updates**
   - Test with realistic frame times
   - Verify update logic with different time steps
   - Check animation frame timing

## Package-Specific Testing

### Controllers

Controllers require careful testing of:
- Event handling
- State transitions
- Input processing
- Game object management

Example:
```python
def test_game_controller_handles_events():
    controller = GameController(...)
    events = [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)]
    controller.handle_events(events)
    # Verify state changes and event processing
```

### Engine

The engine package tests focus on:
- Event system
- Game loop
- State management
- Resource loading

Example:
```python
def test_event_system():
    event_manager = EventManager()
    event = GameEvent()
    event_manager.post(event)
    # Verify event handling and propagation
```

### Utils

Utility tests emphasize:
- File operations
- Asset loading
- Helper functions
- Error handling

Example:
```python
def test_asset_loading():
    asset = load_asset("test.png")
    assert asset is not None
    # Verify asset properties
```

### Game Objects

Game object tests focus on:
- Physics behavior
- Collision detection
- State management
- Animation

Example:
```python
def test_ball_physics():
    ball = Ball(10, 10)
    ball.set_velocity(5, 0)
    ball.update(16.67)
    # Verify position and velocity updates
```

## Best Practices

1. **Test Isolation**
   - Each test should be independent
   - Use fixtures for setup and teardown
   - Don't rely on test execution order

2. **Meaningful Assertions**
   - Test behavior, not implementation
   - Use descriptive assertion messages
   - Verify both success and failure cases

3. **Resource Management**
   - Clean up resources in fixtures
   - Use context managers where appropriate
   - Handle file system operations carefully

4. **Test Coverage**
   - Aim for high coverage of critical paths
   - Test edge cases and error conditions
   - Include integration tests for key features

5. **Performance**
   - Keep tests fast and focused
   - Use appropriate mocking to avoid slow operations
   - Consider test execution time in CI/CD

## Running Tests

### Local Development

```bash
# Run all tests
hatch run test

# Run specific test file
hatch run test tests/unit/test_ball.py

# Run with coverage
hatch run test --cov=src
```

### CI/CD

Tests are run automatically in CI/CD with:
- Full test suite
- Coverage reporting
- Linting checks
- Type checking

## Debugging Failed Tests

1. **Check Physics State**
   - Verify position and velocity
   - Check boundary conditions
   - Look for synchronization issues

2. **Event Handling**
   - Verify event generation
   - Check event processing
   - Look for timing issues

3. **State Management**
   - Check object state
   - Verify cleanup
   - Look for side effects

4. **Resource Issues**
   - Check file paths
   - Verify asset loading
   - Look for cleanup problems

## Test Logging and Debugging

### Logging in Tests

Tests should use the same logging infrastructure as the main code, with some test-specific considerations:

1. **Test-Specific Loggers**
```python
import logging
import pytest

logger = logging.getLogger(f"tests.{__name__}")

def test_ball_physics():
    logger.info("Testing ball physics with initial position (10, 10)")
    ball = Ball(10, 10)
    logger.debug(f"Initial velocity: {ball.get_velocity()}")
    # ... test code ...
```

2. **Using caplog Fixture**
```python
def test_event_handling(caplog):
    caplog.set_level(logging.DEBUG)
    event_manager = EventManager()
    event = GameEvent()
    event_manager.post(event)
    
    # Assert on log messages
    assert "Event posted" in caplog.text
    assert "Event processed" in caplog.text
```

3. **Logging Decorators in Tests**
```python
from utils.logging_decorators import log_entry_exit, log_timing

@log_entry_exit()
@log_timing()
def test_complex_collision():
    # Test implementation
    pass
```

### Debugging Test Failures

1. **Logging State Changes**
```python
def test_ball_collision():
    ball = Ball(10, 10)
    logger.debug(f"Initial state: pos={ball.get_position()}, vel={ball.get_velocity()}")
    
    ball.update(16.67)
    logger.debug(f"After update: pos={ball.get_position()}, vel={ball.get_velocity()}")
    
    assert ball.get_position() == (20, 10)
```

2. **Logging Physics Calculations**
```python
def test_ball_physics():
    ball = Ball(10, 10)
    ball.set_velocity(5, 0)
    
    logger.debug("Physics update:")
    logger.debug(f"  Initial position: {ball.get_position()}")
    logger.debug(f"  Initial velocity: {ball.get_velocity()}")
    
    ball.update(16.67)
    
    logger.debug(f"  Final position: {ball.get_position()}")
    logger.debug(f"  Final velocity: {ball.get_velocity()}")
```

3. **Logging Event Flow**
```python
def test_game_controller_events():
    controller = GameController()
    logger.debug("Posting game events:")
    
    for event in events:
        logger.debug(f"  Processing event: {event}")
        controller.handle_event(event)
        logger.debug(f"  State after event: {controller.get_state()}")
```

### Best Practices for Test Logging

1. **Log Level Usage**
   - `DEBUG`: Detailed state information, calculations
   - `INFO`: Test progress, major state changes
   - `WARNING`: Unexpected but handled conditions
   - `ERROR`: Test failures, unhandled conditions

2. **Logging Assertions**
```python
def test_ball_collision():
    ball = Ball(10, 10)
    block = Block(20, 10)
    
    logger.debug("Testing collision:")
    logger.debug(f"  Ball position: {ball.get_position()}")
    logger.debug(f"  Block position: {block.get_position()}")
    
    collision = ball.check_collision(block)
    logger.debug(f"  Collision detected: {collision}")
    
    assert collision, "Expected collision between ball and block"
```

3. **Logging Timeouts**
```python
@pytest.mark.timeout(5)
def test_long_running_operation():
    logger.info("Starting long-running test")
    start_time = time.time()
    
    # Test implementation
    
    elapsed = time.time() - start_time
    logger.debug(f"Test completed in {elapsed:.2f} seconds")
```

4. **Logging Resource Management**
```python
def test_asset_loading():
    logger.info("Testing asset loading")
    try:
        asset = load_asset("test.png")
        logger.debug(f"Asset loaded: {asset}")
    except AssetError as e:
        logger.error(f"Failed to load asset: {e}")
        raise
    finally:
        logger.debug("Cleaning up resources")
        cleanup_resources()
```

### Integration with CI/CD

1. **Log Collection**
   - Capture all test logs in CI/CD
   - Store logs as artifacts
   - Include logs in test failure reports

2. **Log Analysis**
   - Parse logs for common failure patterns
   - Track test execution times
   - Monitor resource usage

3. **Debug Information**
   - Include relevant logs in bug reports
   - Use logs to reproduce failures
   - Track state changes leading to failures

### Example Test Class with Logging

```python
import logging
import pytest
from utils.logging_decorators import log_entry_exit, log_timing

logger = logging.getLogger(f"tests.{__name__}")

class TestBallPhysics:
    @pytest.fixture(autouse=True)
    def setup(self):
        logger.info("Setting up test")
        self.ball = Ball(10, 10)
        yield
        logger.info("Cleaning up test")
    
    @log_entry_exit()
    @log_timing()
    def test_ball_movement(self):
        logger.debug(f"Initial position: {self.ball.get_position()}")
        self.ball.set_velocity(5, 0)
        self.ball.update(16.67)
        logger.debug(f"Final position: {self.ball.get_position()}")
        assert self.ball.get_position() == (20, 10)
    
    @log_entry_exit()
    def test_ball_collision(self):
        logger.info("Testing ball collision")
        block = Block(20, 10)
        logger.debug(f"Block position: {block.get_position()}")
        collision = self.ball.check_collision(block)
        logger.debug(f"Collision detected: {collision}")
        assert collision
```

This approach ensures that:
- Tests provide detailed debugging information
- Logging is consistent with the main codebase
- Test failures are easily reproducible
- Resource usage and timing are tracked
- CI/CD integration is supported

## Conclusion

The testing strategy emphasizes:
- Using real objects where possible
- Careful use of mocks
- Comprehensive coverage
- Proper resource management
- Clear test organization

This approach helps maintain code quality and catch issues early in development. 