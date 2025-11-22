# XBoing Refactoring Completion Plan

**Document Version:** 1.0
**Date:** 2025-11-22
**Branch:** `refactor/game-protocol`
**Based on:** `docs/GAME-CONTROLLER-DECOMPOSITION.md` Phases 3-5

---

## Executive Summary

### Current Status: 75% Complete

**What the tests passing means:** The refactoring is **functionally working** and **all major architectural components are complete**.

**What's Actually Done:**
- ✅ **Phase 0: Infrastructure (Completed 2025-11-22)**
  - 100% type-clean production code (0 mypy + 0 pyright errors)
  - Production/test code quality separation in hatch
  - GitHub Actions aligned with current standards
  - 202 tests passing with pytest-timeout enforced
- ✅ Phase 1: Protocols and Collision System (complete)
- ✅ Phase 2: Input Controllers extracted (complete)
- ✅ **Phase 3: GameStateManager extraction (Completed 2025-11-22)**
  - GameStateManager class created with all methods
  - 20 comprehensive tests covering all functionality
  - Fully integrated into GameController
  - All 202 tests passing
- ✅ **Phase 4: PowerUpManager extraction (Completed 2025-11-22)**
  - PowerUpManager class created with complete power-up management
  - 32 comprehensive tests (bomb, ammo, paddle size, reverse, sticky)
  - Integrated with CollisionHandlers and GameController
  - Event-driven paddle input synchronization
  - All 202 tests passing
- ✅ **Phase 5: Legacy code removal (Completed 2025-11-22)**
  - Removed 76 lines of legacy test compatibility code
  - Updated 7 tests to use new architecture
  - Removed unused imports
  - All 202 tests passing with clean production code

**What Remains (Final Polish):**
- ❌ Phase 6: Clean architecture goals (60% coverage → 90%, controller simplification)

### The Accomplishment

~~**75 lines of "test compatibility" code**~~ ✅ **RESOLVED** - All legacy compatibility code removed.

**GameController is now 406 lines** (down from 482) - primarily coordination with managers, but could be simplified further to ~300 lines (Phase 6).

~~**Power-up state scattered**~~ ✅ **RESOLVED** - PowerUpManager now centralizes all power-up state and effects.

### The Final Step

Complete Phase 6 for architecture polish:
- Simplify GameController further (~100 line reduction)
- Increase test coverage from 60% → 90%
- Performance testing and optimization
- Final documentation sync

**Estimated Remaining Effort:** 16-23 hours (~1 week focused work)
**Completed Effort:** 50-70 hours (Phases 3-5 complete)

---

## Detailed Phase Breakdown

### Phase 3: Extract GameStateManager

**Goal:** Centralize all game state logic (lives, levels, timers) into dedicated manager

**Current Problems:**
- GameController.handle_life_loss() (lines 335-367) mixes state management with ball creation
- GameController.check_level_complete() (lines 369-378) directly checks blocks and posts events
- GameController.update_blocks_and_timer() (lines 259-274) intertwines block updates with timer logic
- Test-only parameter `force_life_loss` pollutes production code

**Tasks:**

#### Task 3.1: Create GameStateManager Class (4-6 hours)

**File:** `src/xboing/game/game_state_manager.py`

**Class Design:**
```python
class GameStateManager:
    """Manages game state transitions: lives, levels, game over, timers."""

    def __init__(self, game_state: GameState, level_manager: LevelManager):
        self.game_state = game_state
        self.level_manager = level_manager

    def handle_life_loss(self, has_active_balls: bool) -> List[Event]:
        """Handle life loss logic, return events to post.

        Returns events like LifeLostEvent, GameOverEvent.
        Does NOT create balls or manage sticky state - those are separate concerns.
        """

    def check_level_complete(self, blocks_remaining: int) -> List[Event]:
        """Check if level is complete based on block count.

        Returns LevelCompleteEvent, ApplauseEvent if complete.
        """

    def update_timer(self, delta_ms: float, is_active: bool) -> List[Event]:
        """Update bonus timer if game is active.

        Returns TimerUpdatedEvent with current time.
        """

    def is_game_over(self) -> bool:
        """Check if game is over."""

    def reset_level(self) -> None:
        """Reset state for new level."""
```

**Why This Design:**
- Accepts parameters instead of accessing managers (loose coupling)
- Returns events instead of posting them (testable without pygame)
- Single responsibility: state transitions only
- No ball creation, no sticky management (separation of concerns)

#### Task 3.2: Migrate Life Loss Logic (2-3 hours)

**Move from GameController.handle_life_loss():**
- Check for game over state
- Determine if life should be lost
- Call game_state.lose_life()
- Generate events

**Leave in GameController:**
- Ball creation (delegate to BallManager or keep as controller responsibility)
- Sticky state management (will move to PowerUpManager in Phase 4)

**Remove:**
- `force_life_loss` parameter (test-specific, not production code)

**Update:**
- 1 test currently using `force_life_loss`

#### Task 3.3: Migrate Level Completion Logic (1-2 hours)

**Move from GameController.check_level_complete():**
- Level complete detection
- Event generation

**Leave in GameController:**
- Block count checking (pass as parameter to GameStateManager)

**Simplify GameController to:**
```python
def check_level_complete(self) -> None:
    blocks_remaining = len(self.block_manager.blocks)
    events = self.game_state_manager.check_level_complete(blocks_remaining)
    for event in events:
        pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"event": event}))
```

#### Task 3.4: Migrate Timer Logic (1-2 hours)

**Move from GameController.update_blocks_and_timer():**
- Timer decrement logic
- Timer event generation

**Separate Concerns:**
- Block updates stay in update loop
- Timer logic extracted to GameStateManager

**Result:**
```python
def update_blocks_and_timer(self, delta_ms: float):
    self.block_manager.update(delta_ms)

    is_active = not self.game_state.is_game_over() and not self.game_state.level_state.is_level_complete()
    events = self.game_state_manager.update_timer(delta_ms, is_active)
    for event in events:
        pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"event": event}))
```

#### Task 3.5: Create Tests for GameStateManager (6-8 hours)

**File:** `tests/unit/test_game_state_manager.py`

**Test Coverage:**
- Life loss when no active balls
- Life loss when active balls remain (no life lost)
- Game over state after last life
- Level complete detection
- Timer updates and events
- Edge cases (zero lives, zero blocks, timer expiration)

**Target:** 25-30 tests, >90% coverage of GameStateManager

#### Task 3.6: Update Affected GameController Tests (2-3 hours)

**Tests to Update:**
- `test_lives_display_and_game_over_event_order` - Remove `force_life_loss` usage
- Any tests checking life loss logic
- Any tests checking level completion logic

**Approach:** Use real GameStateManager, mock dependencies

**Phase 3 Subtotal: 14-21 hours**

---

### Phase 4: Extract PowerUpManager

**Goal:** Centralize all power-up state and effects into dedicated manager

**Current Problems:**
- CollisionHandlers owns `sticky` and `reverse` state (lines 66-67)
- CollisionHandlers.handle_block_effects() has complex power-up logic (lines 173-229)
- Direct paddle manipulation violates boundaries
- No duration tracking (power-ups permanent until reset)
- Power-up state mixed with collision logic

**Tasks:**

#### Task 4.1: Create PowerUpManager Class (4-6 hours)

**File:** `src/xboing/game/powerup_manager.py`

**Class Design:**
```python
class PowerUpManager:
    """Manages all power-up state, effects, and durations."""

    def __init__(self, paddle: Paddle, game_state: GameState):
        self.paddle = paddle
        self.game_state = game_state
        self._sticky_active = False
        self._reverse_active = False
        self._sticky_duration_remaining = 0.0  # ms, 0 = permanent
        self._reverse_duration_remaining = 0.0

    # State queries
    def is_sticky_active(self) -> bool
    def is_reverse_active(self) -> bool

    # Activation methods (called by collision handlers)
    def activate_sticky(self, duration_ms: Optional[float] = None) -> List[Event]:
        """Activate sticky paddle. Returns SpecialStickyChangedEvent."""

    def deactivate_sticky(self) -> List[Event]:
        """Deactivate sticky paddle. Returns SpecialStickyChangedEvent."""

    def toggle_reverse(self) -> List[Event]:
        """Toggle reverse controls. Returns SpecialReverseChangedEvent."""

    def activate_bomb(self) -> List[Event]:
        """Handle bomb explosion. Returns BombExplodedEvent."""

    def add_ammo(self) -> List[Event]:
        """Add ammo to game state. Returns AmmoEvent."""

    def grow_paddle(self) -> List[Event]:
        """Grow paddle if not at max. Returns PaddleGrowEvent."""

    def shrink_paddle(self) -> List[Event]:
        """Shrink paddle if not at min. Returns PaddleShrinkEvent."""

    # Duration management
    def update(self, delta_ms: float) -> List[Event]:
        """Update power-up durations, return expiration events."""

    def reset_all(self) -> List[Event]:
        """Reset all power-ups (for new level). Returns deactivation events."""
```

**Why This Design:**
- Single responsibility: power-up state and effects
- Clean interface for activation
- Encapsulates duration logic
- Returns events (testable)
- Direct paddle access acceptable (needs to change paddle state)

#### Task 4.2: Move Power-Up State from CollisionHandlers (3-4 hours)

**Remove from CollisionHandlers:**
- `self.sticky` instance variable
- `self.reverse` instance variable
- `set_sticky()` method
- `set_reverse()` method

**Update CollisionHandlers.handle_block_effects():**

**Old Code (lines 182-229):**
```python
if effect == BOMB_BLK:
    pygame.event.post(...)
elif effect == STICKY_BLK:
    self.sticky = True
    self.paddle.sticky = True
    pygame.event.post(...)
elif effect == REVERSE_BLK:
    self.reverse = not self.reverse
    pygame.event.post(...)
# ... etc
```

**New Code:**
```python
def handle_block_effects(self, effect: str, block: Block) -> None:
    """Handle special block effects via PowerUpManager."""
    events = []

    if effect == BOMB_BLK:
        events = self.powerup_manager.activate_bomb()
    elif effect == STICKY_BLK:
        events = self.powerup_manager.activate_sticky()
    elif effect == REVERSE_BLK:
        events = self.powerup_manager.toggle_reverse()
    elif effect in (BULLET_BLK, MAXAMMO_BLK):
        events = self.powerup_manager.add_ammo()
    elif effect == PAD_EXPAND_BLK:
        events = self.powerup_manager.grow_paddle()
    elif effect == PAD_SHRINK_BLK:
        events = self.powerup_manager.shrink_paddle()

    self.post_game_state_events(events)
```

**Result:** CollisionHandlers simplified, no power-up state, delegates to manager

#### Task 4.3: Integrate PowerUpManager with GameController (2-3 hours)

**Add to GameController.__init__():**
```python
self.powerup_manager = PowerUpManager(paddle, game_state)
```

**Pass to CollisionHandlers:**
```python
self.collision_handlers = CollisionHandlers(
    game_state, paddle, ball_manager, bullet_manager,
    block_manager, powerup_manager
)
```

**Update Existing Methods:**
- `enable_sticky()` → delegate to PowerUpManager
- `disable_sticky()` → delegate to PowerUpManager
- `toggle_reverse()` → delegate to PowerUpManager (if exists)
- `on_new_level_loaded()` → call `powerup_manager.reset_all()`

**Add to Update Loop:**
```python
def update(self, delta_ms: float):
    # ... existing updates ...

    # Update power-up durations
    events = self.powerup_manager.update(delta_ms)
    for event in events:
        pygame.event.post(...)
```

#### Task 4.4: Implement Duration Tracking (3-4 hours)

**Design Decision Needed:** Are power-ups timed or permanent in XBoing?

**Research:** Check original XBoing C code for:
- Sticky paddle duration
- Reverse control duration

**Implementation Options:**
1. **Permanent** (simpler): Power-ups last until level end or explicit deactivation
2. **Timed** (more complex): Power-ups expire after N seconds

**Recommendation:** Start with permanent, add duration support if needed

**If Timed:**
```python
def update(self, delta_ms: float) -> List[Event]:
    events = []

    if self._sticky_duration_remaining > 0:
        self._sticky_duration_remaining -= delta_ms
        if self._sticky_duration_remaining <= 0:
            events.extend(self.deactivate_sticky())

    if self._reverse_duration_remaining > 0:
        self._reverse_duration_remaining -= delta_ms
        if self._reverse_duration_remaining <= 0:
            self._reverse_active = False
            events.append(SpecialReverseChangedEvent(active=False))

    return events
```

#### Task 4.5: Remove Direct Paddle Manipulation (2-3 hours)

**Current Problem:** CollisionHandlers directly calls:
- `self.paddle.set_size()` for grow/shrink
- `self.paddle.sticky = True` for sticky activation

**Solution:** PowerUpManager can access paddle (it owns reference)

**Simplification:** This is acceptable - PowerUpManager's job is to modify paddle state

**Keep:** Direct paddle access in PowerUpManager (not a violation)

#### Task 4.6: Create Tests for PowerUpManager (8-10 hours)

**File:** `tests/unit/test_powerup_manager.py`

**Test Coverage:**
- Sticky activation and deactivation
- Reverse toggle (on/off/on)
- Bomb effect handling
- Ammo addition
- Paddle growth (normal and at max)
- Paddle shrinkage (normal and at min)
- Duration expiration (if implemented)
- Reset all power-ups
- Event generation for all effects

**Target:** 30-40 tests, >90% coverage of PowerUpManager

#### Task 4.7: Update Affected Tests (4-6 hours)

**Tests to Update:**
- `test_sticky_paddle_activation_event` - Use PowerUpManager
- `test_paddle_expand_event_fired` - Use PowerUpManager
- `test_paddle_shrink_event_fired` - Use PowerUpManager
- Any collision tests checking power-up effects

**Approach:** Mock PowerUpManager in collision tests, test PowerUpManager separately

**Phase 4 Subtotal: 22-30 hours**

---

### Phase 5: Remove ALL Legacy Compatibility Code

**Goal:** Eliminate all "test compatibility" code from production files

**Current Legacy Code:**

**In GameController (75 total lines):**
1. `_handle_ball_block_collision()` (31 lines, 129-159)
2. `_handle_ball_paddle_collision()` (3 lines, 161-163)
3. `_handle_bullet_block_collision()` (3 lines, 165-167)
4. `_handle_bullet_ball_collision()` (3 lines, 169-171)
5. `sticky` property (7 lines, 175-182)
6. `reverse` property (7 lines, 185-192)
7. `_last_mouse_x` property (7 lines, 196-203)

**Tests Using Legacy Code:** 13+ tests

**Tasks:**

#### Task 5.1: Identify All Tests Using Legacy Code (1 hour)

**Run Grep:**
```bash
grep -r "_handle_ball_block_collision\|_handle_ball_paddle_collision\|_handle_bullet_block_collision\|_handle_bullet_ball_collision\|force_life_loss" tests/
grep -r "controller.sticky\|controller.reverse\|controller._last_mouse_x" tests/
```

**Create Checklist:** Document every test file and test function that needs updating

**Estimated Impact:** 13-16 tests need significant refactoring

#### Task 5.2: Update Tests to Remove _handle_* Calls (6-8 hours)

**Strategy:** Replace direct method calls with integration tests using real collision system

**Example Refactoring:**

**Old Test (using legacy method):**
```python
def test_paddle_expand_event_fired(self, mock_event_post):
    block = Block(...)
    block.type = PAD_EXPAND_BLK
    ball = Ball(...)

    controller._handle_ball_block_collision(ball, block)

    assert any(isinstance(call[0][0].event, PaddleGrowEvent)
               for call in mock_event_post.call_args_list)
```

**New Test (using collision system):**
```python
def test_paddle_expand_event_fired(self, controller, mock_event_post):
    # Create block with expand power-up
    block = Block(100, 100, PAD_EXPAND_BLK)
    controller.block_manager.add_block(block)

    # Create ball at block position
    ball = Ball(100, 100)
    ball.set_velocity(0, 5)  # Moving toward block
    controller.ball_manager.add_ball(ball)

    # Register collidables and trigger collision
    controller._register_all_collidables()
    controller.collision_system.check_collisions()

    # Verify event posted
    assert any(isinstance(call[0][0].event, PaddleGrowEvent)
               for call in mock_event_post.call_args_list)
```

**Tests to Refactor:**
- `test_paddle_expand_event_fired`
- `test_paddle_shrink_event_fired`
- `test_sticky_paddle_activation_event`
- `test_block_scoring_and_event_on_hit`
- 3-4 similar tests

**Complexity:** Medium-High (requires understanding collision system integration)

#### Task 5.3: Remove Legacy Methods from GameController (1 hour)

**Delete Methods:**
```python
# Delete lines 128-171 (44 lines)
def _handle_ball_block_collision(...)
def _handle_ball_paddle_collision(...)
def _handle_bullet_block_collision(...)
def _handle_bullet_ball_collision(...)
```

**Verify:** No references remain in production code (tests already updated)

**Run:** Full test suite to ensure no breakage

#### Task 5.4: Update Tests to Remove Property Wrappers (2-3 hours)

**For controller.sticky:**
```python
# Old: controller.sticky = True
# New: controller.powerup_manager.activate_sticky()

# Old: assert controller.sticky
# New: assert controller.powerup_manager.is_sticky_active()
```

**For controller.reverse:**
```python
# Old: controller.reverse = True
# New: controller.paddle_input.set_reverse(True)

# Old: assert controller.reverse
# New: assert controller.paddle_input.reverse
```

**For controller._last_mouse_x:**
```python
# Old: controller._last_mouse_x = 100
# New: controller.paddle_input.set_last_mouse_x(100)

# Old: assert controller._last_mouse_x == 100
# New: assert controller.paddle_input.get_last_mouse_x() == 100
```

**Tests to Update:**
- `test_arrow_key_movement_reversed`
- `test_mouse_movement_reversed`
- `test_ball_sticks_to_paddle_when_sticky`
- 2-3 similar tests

#### Task 5.5: Remove Property Wrappers from GameController (1 hour)

**Delete Properties:**
```python
# Delete lines 173-203 (31 lines)
@property
def sticky(self) -> bool: ...

@property
def reverse(self) -> bool: ...

@property
def _last_mouse_x(self) -> Optional[int]: ...
```

**Result:** 75 lines of legacy code removed

#### Task 5.6: Remove Test-Only Parameters (1 hour)

**Remove from handle_life_loss():**
```python
# Old:
def handle_life_loss(self, force_life_loss: bool = False) -> None:
    if not self.ball_manager.active_ball() or force_life_loss:
        # ...

# New:
def handle_life_loss(self) -> None:
    if not self.ball_manager.active_ball():
        # ...
```

**Update Test:**
```python
# test_lives_display_and_game_over_event_order

# Old approach:
controller.handle_life_loss(force_life_loss=True)

# New approach:
# Remove all balls to trigger real life loss
for ball in list(controller.ball_manager.balls):
    controller.ball_manager.remove_ball(ball)
controller.handle_life_loss()
```

#### Task 5.7: Final Test Suite Validation (2-3 hours)

**Run:** Full test suite multiple times

**Fix:** Any remaining failures

**Verify:**
- All 150+ tests pass
- No warnings about deprecated methods
- No references to removed code
- Coverage maintained or improved

**Phase 5 Subtotal: 14-19 hours**

---

### Phase 6: Clean Architecture & Polish

**Goal:** Achieve all original success criteria

**Tasks:**

#### Task 6.1: Simplify GameController (3-4 hours)

**Current:** 479 lines with mixed responsibilities
**Target:** ~300 lines, coordinator only

**Simplification Opportunities:**
1. Extract ball creation to BallManager
2. Simplify update loop (delegate more)
3. Remove verbose logging (or move to debug mode)
4. Consolidate event posting patterns
5. Remove commented-out code

**Method Sizes:**
- `update_balls_and_collisions()` is 55 lines - simplify
- `handle_life_loss()` will be much simpler after Phase 3

**Expected Reduction:** 150-180 lines

#### Task 6.2: Increase Test Coverage to 90% (8-12 hours)

**Current Coverage:** 60% (4844 lines, 1922 untested)
**Target Coverage:** 90% (minimum)

**Coverage Gaps Analysis:**
```bash
hatch run cov --cov-report=html
# Open htmlcov/index.html to identify gaps
```

**Expected Gaps:**
- GameStateManager (new, needs full coverage)
- PowerUpManager (new, needs full coverage)
- Edge cases in existing code
- Error handling paths
- Boundary conditions

**Coverage Strategy:**
1. Write tests for new classes first (GameStateManager, PowerUpManager)
2. Identify lowest coverage files
3. Add tests for uncovered lines
4. Focus on critical paths and error handling

**Estimated New Tests:** 40-60 tests

#### Task 6.3: Update All Documentation (3-4 hours)

**Files to Update:**

**1. GAME-CONTROLLER-DECOMPOSITION.md**
- Update Phase 3-5 status from "Not Started" to "Complete"
- Document actual implementation vs planned
- Update "Current Status" section with completion date
- Add lessons learned

**2. CODE-GAME-PROTOCOL-REVISED.md**
- Clarify PhysicsComponent integration via PhysicsMixin
- Update class diagrams if any
- Document new managers (GameStateManager, PowerUpManager)

**3. ARCHITECTURE-MVC-REVISED.md**
- Add GameStateManager to architecture diagram
- Add PowerUpManager to architecture diagram
- Update component interaction diagrams

**4. Class Docstrings**
- Ensure all new classes have comprehensive docstrings
- Update GameController docstring to reflect coordinator role
- Document manager responsibilities clearly

**5. STATUS.md**
- Update completion percentage to 100%
- Document actual timeline
- Add "Lessons Learned" section
- Archive as historical record

**6. PLAN.md (this file)**
- Mark all tasks complete
- Document actual hours spent
- Note any deviations from plan
- Final retrospective

#### Task 6.4: Code Review & Cleanup (2-3 hours)

**Linting:**
```bash
hatch run check  # Run black, ruff, mypy
```

**Fix:**
- Any linting errors
- Type hint issues
- Import organization

**Review:**
- Dead code removal
- TODO comments (resolve or move to TODO.md)
- Commented-out code removal
- Debug logging cleanup

**Final Checklist:**
- [ ] All tests pass (150+)
- [ ] Coverage ≥ 90%
- [ ] All linters pass
- [ ] No legacy code remains
- [ ] Documentation updated
- [ ] GameController ≤ 300 lines
- [ ] Clear component boundaries

**Phase 6 Subtotal: 16-23 hours**

---

## Total Effort Summary

| Phase | Tasks | Hours (Low-High) | Complexity | Status |
|-------|-------|------------------|------------|--------|
| Phase 3: GameStateManager | 6 tasks | 14-21 | Medium | ✅ Complete |
| Phase 4: PowerUpManager | 7 tasks | 22-30 | Medium-High | ✅ Complete |
| Phase 5: Legacy Removal | 7 tasks | ~4 (actual) | Medium | ✅ Complete |
| Phase 6: Clean Architecture | 4 tasks | 16-23 | Medium | ❌ Not Started |
| **COMPLETED** | **20 tasks** | **50-70 hours** | **Mixed** | **✅ Done** |
| **REMAINING** | **4 tasks** | **16-23 hours** | **Medium** | **⏳ To Do** |

**Original Timeline Estimate:** 66-93 hours (2-3 weeks)
**Completed:** 50-70 hours (Phases 3-5 done)
**Remaining Timeline Estimate:**
- **Aggressive:** 3-4 days (6-8 hours/day, ~20 hours)
- **Realistic:** 1 week (4-6 hours/day, ~20 hours)
- **Conservative:** 1.5 weeks (part-time, interruptions)

---

## Execution Strategy

### Recommended Approach: Sequential Phases

**Week 1: Phase 3 (GameStateManager)**
- Days 1-2: Create class, migrate life loss logic
- Days 3-4: Migrate level completion, timer logic
- Day 5: Write comprehensive tests

**Week 2: Phase 4 (PowerUpManager)**
- Days 1-2: Create class, move power-up state
- Days 3-4: Integrate with system, duration tracking
- Day 5: Write comprehensive tests

**Week 3: Phases 5-6 (Cleanup & Polish)**
- Days 1-2: Remove legacy code
- Days 2-3: Update tests, fix failures
- Days 4-5: Increase coverage, documentation, final review

### Alternative: Incremental Delivery

**Milestone 1:** Phase 3 complete
- Commit: "refactor: Extract GameStateManager"
- Review & deploy
- Breathing room

**Milestone 2:** Phase 4 complete
- Commit: "refactor: Extract PowerUpManager"
- Review & deploy
- Breathing room

**Milestone 3:** Phases 5-6 complete
- Commit: "refactor: Remove legacy code and achieve clean architecture"
- Final review & merge to master

**Benefit:** Lower risk, easier review, can pause between phases

---

## Success Criteria (From Decomposition Plan)

### Must-Have for Completion:

- [ ] **GameStateManager exists** and handles all game state logic
- [ ] **PowerUpManager exists** and handles all power-up state
- [ ] **Zero legacy compatibility code** in production files
- [ ] **Zero test-only parameters** in production methods
- [ ] **All 150+ tests pass** with new architecture
- [ ] **Test coverage ≥ 90%** (currently 60%)
- [ ] **GameController ≤ 300 lines** (currently 479)
- [ ] **Documentation updated** to reflect new architecture
- [ ] **All linters pass** (black, ruff, mypy --strict)

### Architectural Goals:

- [ ] **Clear component boundaries:** Each manager has single responsibility
- [ ] **No circular dependencies:** Clean dependency graph
- [ ] **Event-driven communication:** Components return events, don't post directly
- [ ] **Testable without pygame:** Managers work headless
- [ ] **Easy to extend:** New power-ups, game states simple to add

### Definition of Done:

**The refactoring is complete when:**
1. All success criteria above are met
2. No "TODO" or "FIXME" comments related to refactoring
3. Code review approved by maintainer
4. Documentation reflects reality (not aspirational)
5. Can confidently add new features without technical debt

---

## Risk Assessment

### High Risks:

**1. Test Refactoring Complexity (Phase 5)**
- **Risk:** 13+ tests need significant rework, may uncover bugs
- **Probability:** Medium
- **Impact:** High (blocks completion)
- **Mitigation:**
  - Tackle tests incrementally
  - Keep old tests until new ones pass
  - Add integration tests to cover end-to-end flows
  - Budget extra time (already in estimate)

**2. Power-Up Duration Design (Phase 4.4)**
- **Risk:** Unclear if power-ups should be timed or permanent
- **Probability:** Medium
- **Impact:** Medium (affects implementation)
- **Mitigation:**
  - Research original XBoing behavior
  - Start with simpler permanent implementation
  - Make duration configurable for future

**3. Coverage Target Unreachable (Phase 6.2)**
- **Risk:** 90% coverage may be hard to achieve
- **Probability:** Low
- **Impact:** Medium (success criteria)
- **Mitigation:**
  - Focus on critical paths first
  - Accept 85% if remaining 5% is trivial code
  - Document coverage exclusions

### Medium Risks:

**4. Scope Creep**
- **Risk:** Finding new refactoring opportunities during work
- **Probability:** Medium
- **Impact:** Low (timeline slip)
- **Mitigation:**
  - Document new opportunities in TODO.md
  - Stay focused on Phases 3-6 only
  - Defer improvements to post-refactoring

**5. Merge Conflicts**
- **Risk:** Long-running branch diverges from master
- **Probability:** Low (branch is current)
- **Impact:** Low (easy to resolve)
- **Mitigation:**
  - Rebase on master weekly
  - Keep commits logical and atomic

### Low Risks:

**6. Performance Regression**
- **Risk:** More indirection affects performance
- **Probability:** Very Low
- **Impact:** Low (easily optimized)
- **Mitigation:**
  - Monitor frame rate during testing
  - Profile if concerns arise

---

## Dependencies & Blockers

### Dependencies:

- Phase 4 depends on Phase 3 (GameStateManager may be used by PowerUpManager)
- Phase 5 depends on Phase 4 (can't remove legacy until new architecture works)
- Phase 6 depends on Phase 5 (can't achieve clean architecture with legacy code)

### Potential Blockers:

- **Test environment issues:** If tests fail to run, debugging required
- **Unclear requirements:** Original XBoing behavior needs research
- **Time constraints:** If 2-3 weeks not available, need to split work

### External Dependencies:

- None (all code internal to project)

---

## Git Strategy

### Commit Structure:

**Phase 3:**
```
refactor(game): Extract GameStateManager for life/level/timer logic

- Create GameStateManager class
- Move handle_life_loss logic
- Move check_level_complete logic
- Move timer management logic
- Add comprehensive tests
- Update affected GameController tests

BREAKING CHANGE: GameController no longer has force_life_loss parameter
```

**Phase 4:**
```
refactor(game): Extract PowerUpManager for power-up state and effects

- Create PowerUpManager class
- Move sticky/reverse state from CollisionHandlers
- Extract all power-up effects from handle_block_effects
- Add duration tracking
- Add comprehensive tests
- Update affected tests

BREAKING CHANGE: CollisionHandlers no longer has sticky/reverse properties
```

**Phase 5:**
```
refactor(game): Remove legacy compatibility code and clean architecture

- Remove _handle_* legacy methods from GameController
- Remove sticky/reverse/mouse_x property wrappers
- Update all affected tests to use new architecture
- Simplify GameController to coordinator role

BREAKING CHANGE: GameController no longer has test compatibility methods
```

**Phase 6:**
```
refactor(game): Achieve 90% coverage and final polish

- Add tests to reach 90% coverage
- Simplify GameController to ~300 lines
- Update all documentation
- Final code review and cleanup
```

### Branch Strategy:

**Option A:** Single branch (current)
- Commit phases sequentially on `refactor/game-protocol`
- Single PR with multiple commits
- Easier to review as logical progression

**Option B:** Stacked branches
- Create `refactor/game-protocol-phase3` from current
- Create `refactor/game-protocol-phase4` from phase3
- Create `refactor/game-protocol-phase5` from phase4
- Separate PRs for each phase
- Better for incremental review

**Recommendation:** Option A (single branch, multiple commits)

---

## Monitoring & Validation

### Continuous Validation:

**After Each Task:**
```bash
hatch run test          # All tests pass
hatch run check         # All linters pass
hatch run cov           # Check coverage
```

**After Each Phase:**
```bash
hatch run test --verbose  # Full test output
hatch run cov --cov-report=html  # Detailed coverage
git diff --stat HEAD~5..HEAD  # Review changes
```

### Progress Tracking:

**Daily:**
- Update PLAN.md task checkboxes
- Commit completed work
- Document blockers or deviations

**Weekly:**
- Review progress vs timeline
- Adjust estimates if needed
- Update stakeholders

### Success Metrics:

- **Tests:** 150+ passing (currently 150)
- **Coverage:** 90% (currently 60%, need +30%)
- **LOC:** GameController < 300 (currently 479, need -179)
- **Legacy:** 0 lines (currently 75, need -75)
- **Managers:** 2 new classes (GameStateManager, PowerUpManager)

---

## Lessons Learned (To Be Updated)

### What Went Well:

- [ ] (To be filled during execution)

### What Was Challenging:

- [ ] (To be filled during execution)

### What We'd Do Differently:

- [ ] (To be filled during execution)

### Surprises:

- [ ] (To be filled during execution)

---

## Appendix A: Quick Reference

### Key Files:

**Production Code:**
- `src/xboing/controllers/game_controller.py` (479 lines → 300)
- `src/xboing/game/collision_handlers.py` (262 lines → ~200)
- `src/xboing/game/game_state_manager.py` (NEW)
- `src/xboing/game/powerup_manager.py` (NEW)

**Tests:**
- `tests/unit/test_game_controller.py` (28KB, 13+ tests to update)
- `tests/unit/test_game_state_manager.py` (NEW, 25-30 tests)
- `tests/unit/test_powerup_manager.py` (NEW, 30-40 tests)

**Documentation:**
- `docs/GAME-CONTROLLER-DECOMPOSITION.md` (update status)
- `docs/CODE-GAME-PROTOCOL-REVISED.md` (update architecture)
- `docs/ARCHITECTURE-MVC-REVISED.md` (add new managers)

### Command Reference:

```bash
# Run tests
hatch run test
hatch run test tests/unit/test_game_controller.py
hatch run test -k test_sticky_paddle

# Check code quality
hatch run check
hatch run lint
hatch run typecheck

# Coverage
hatch run cov
hatch run cov --cov-report=html
open htmlcov/index.html

# Git
git status
git diff --stat
git log --oneline -10
```

---

## Appendix B: Original Plan Comparison

### Original GAME-CONTROLLER-DECOMPOSITION.md Timeline:

**From document (lines 424-431):**
1. Phase 0-1: Event System and Component Lifecycle (2 weeks) ✅ DONE
2. Phase 2-3: Protocol Implementation and Component Extraction (3 weeks) ✅ DONE (Phase 2)
3. Phase 4: Game Controller Refactoring (2 weeks) ❌ NOT DONE (Phase 3-4)
4. Phase 5: Testing Implementation (2 weeks) ❌ NOT DONE (Phase 5-6)
5. Phase 6-7: Performance and Error Handling (2 weeks) ❌ SKIPPED

**Original Total:** 11 weeks
**Actual Completed:** ~3 weeks (Phases 0-2)
**Remaining:** 2-3 weeks (Phases 3-6)

### Key Differences:

**Original Plan:**
- Included EventBus and component lifecycle (not implemented)
- Planned for performance optimizations (deferred)
- Estimated 11 weeks total

**Actual Reality:**
- Simpler event system (pygame events, not EventBus)
- Focus on architecture, not performance
- Estimated ~5-6 weeks total (3 done, 2-3 remaining)

---

## Final Notes

This plan is based on honest assessment of current state and realistic effort estimates. The 66-93 hour estimate comes from detailed task breakdown and includes buffer for unknowns.

**The refactoring is worth completing** because:
1. Removes 75 lines of technical debt
2. Achieves stated architectural goals
3. Makes future features easier (machine gun powerup)
4. Improves testability and maintainability
5. Sets good precedent for code quality

**Questions or concerns?** Review STATUS.md for detailed analysis of current state.

**Ready to begin?** Start with Phase 3, Task 3.1: Create GameStateManager Class

---

**Document Status:** ACTIVE PLAN
**Next Review:** After Phase 3 completion
**Owner:** Development Team
**Approved By:** (To be filled)
