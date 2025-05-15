# MVC Model-Controller Event Refactor Plan

## Motivation

Currently, the GameState model (and potentially other models) fires Pygame events directly when its state changes. While this keeps the UI in sync, it couples the model to the Pygame event system, making headless testing, reuse, and decoupling more difficult. Moving event firing responsibility to controllers will:
- Decouple models from Pygame and event systems
- Enable pure, side-effect-free models for easier testing
- Make event firing explicit and flexible

## Goals
- GameState and other models should not post Pygame events directly
- All event firing should be handled by controllers (or a service layer)
- Models should return information about what changed (e.g., via return values or change objects)
- All existing game and UI functionality should be preserved
- Enable headless and unit testing of models without Pygame

## Migration Strategy

### 1. Audit and Document Current Event Firing
- Identify all places in GameState (and other models) where events are posted
- List all affected methods and events

### 2. Define Change Notification Pattern
- Decide on a pattern for models to report changes (e.g., return a list of change objects, enums, or flags)
- Document the pattern and update model method signatures as needed

### 3. Refactor Model Methods
- Remove all direct calls to `pygame.event.post` from GameState and other models
- Update methods to return change information (e.g., `return [ScoreChanged(score), ...]`)
- Update docstrings to clarify side-effect-free behavior

### 4. Update Controllers
- Update all controllers to:
  - Call model methods and capture returned changes
  - For each change, fire the appropriate Pygame event (or take other action)
- Ensure all event firing logic is now in controllers

### 5. Update Tests
- Add/modify tests for GameState and other models to verify state changes via return values, not event queue
- Add/modify controller tests to verify correct event firing based on model changes
- Add headless tests for models

### 6. Update Documentation
- Update `GUI-DESIGN.md` and other docs to reflect the new event firing pattern
- Document the new responsibilities of models and controllers

### 7. Manual QA
- Run the game and verify all UI, sound, and gameplay flows still work
- Run the full test suite

## Example Code Patterns

### Before (Model Fires Event)
```python
def add_score(self, points):
    self.score += points
    pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"event": ScoreChangedEvent(self.score)}))
```

### After (Model Returns Change, Controller Fires Event)
```python
def add_score(self, points):
    self.score += points
    return [ScoreChangedEvent(self.score)]

# In controller:
changes = game_state.add_score(100)
for change in changes:
    pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"event": change}))
```

## Testing Considerations
- Models can now be tested in isolation, verifying return values for state changes
- Controllers can be tested for correct event firing
- Headless (non-Pygame) tests are now possible for models

## Migration Checklist
- [ ] Audit all model event firing (GameState, etc.)
- [ ] Define and document change notification pattern
- [ ] Refactor all model methods to return changes, not fire events
- [ ] Update all controllers to fire events based on model changes
- [ ] Update/add tests for models and controllers
- [ ] Update documentation
- [ ] Manual QA: verify all game and UI flows

---

**Review this plan and suggest any changes or additions before starting the refactor.** 