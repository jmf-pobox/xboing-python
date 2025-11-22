"""Tests for GameStateManager."""

import logging

import pytest

from xboing.engine.events import (
    ApplauseEvent,
    GameOverEvent,
    LevelCompleteEvent,
    LivesChangedEvent,
    TimerUpdatedEvent,
)
from xboing.game.game_state import GameState
from xboing.game.game_state_manager import GameStateManager
from xboing.game.level_manager import LevelManager


@pytest.fixture
def level_manager():
    """Create a level manager for testing."""
    return LevelManager()


@pytest.fixture
def game_state():
    """Create a game state for testing."""
    return GameState()


@pytest.fixture
def manager(game_state, level_manager):
    """Create a game state manager for testing."""
    return GameStateManager(game_state, level_manager)


class TestGameStateManagerLifeLoss:
    """Tests for life loss handling."""

    def test_life_loss_when_no_active_balls(self, manager, game_state):
        """Test that life is lost when no active balls remain."""
        initial_lives = game_state.lives

        # Call handle_life_loss with no active balls
        events = manager.handle_life_loss(has_active_balls=False)

        # Should lose a life
        assert game_state.lives == initial_lives - 1

        # Should return LivesChangedEvent
        assert any(isinstance(e, LivesChangedEvent) for e in events)

    def test_no_life_loss_when_active_balls_remain(self, manager, game_state):
        """Test that life is NOT lost when active balls remain."""
        initial_lives = game_state.lives

        # Call handle_life_loss with active balls
        events = manager.handle_life_loss(has_active_balls=True)

        # Should NOT lose a life
        assert game_state.lives == initial_lives

        # Should return no events
        assert len(events) == 0

    def test_game_over_after_last_life(self, manager, game_state):
        """Test that game over event is returned after losing last life."""
        # Set to 1 life
        game_state.lives = 1

        # Lose the last life
        events = manager.handle_life_loss(has_active_balls=False)

        # Should be game over
        assert game_state.is_game_over()

        # Should return GameOverEvent
        assert any(isinstance(e, GameOverEvent) for e in events)

    def test_no_life_loss_when_already_game_over(self, manager, game_state):
        """Test that no life is lost if game is already over."""
        # Set game over state properly
        game_state.lives = 0
        game_state.set_game_over(True)
        initial_lives = game_state.lives

        # Try to lose a life
        events = manager.handle_life_loss(has_active_balls=False)

        # Should not change lives
        assert game_state.lives == initial_lives

        # Should return no events
        assert len(events) == 0

    def test_multiple_life_losses(self, manager, game_state):
        """Test losing multiple lives in sequence."""
        # Start with 3 lives
        game_state.lives = 3

        # Lose first life
        manager.handle_life_loss(has_active_balls=False)
        assert game_state.lives == 2
        assert not game_state.is_game_over()

        # Lose second life
        manager.handle_life_loss(has_active_balls=False)
        assert game_state.lives == 1
        assert not game_state.is_game_over()

        # Lose third life (game over)
        events3 = manager.handle_life_loss(has_active_balls=False)
        assert game_state.lives == 0
        assert game_state.is_game_over()
        assert any(isinstance(e, GameOverEvent) for e in events3)


class TestGameStateManagerLevelComplete:
    """Tests for level completion detection."""

    def test_level_complete_when_no_blocks(self, manager, game_state):
        """Test that level complete is detected when no blocks remain."""
        events = manager.check_level_complete(blocks_remaining=0)

        # Should set level complete
        assert game_state.level_state.is_level_complete()

        # Should return LevelCompleteEvent and ApplauseEvent
        assert any(isinstance(e, LevelCompleteEvent) for e in events)
        assert any(isinstance(e, ApplauseEvent) for e in events)
        assert len(events) == 2

    def test_level_not_complete_when_blocks_remain(self, manager, game_state):
        """Test that level is not complete when blocks remain."""
        events = manager.check_level_complete(blocks_remaining=5)

        # Should not set level complete
        assert not game_state.level_state.is_level_complete()

        # Should return no events
        assert len(events) == 0

    def test_level_complete_transition(self, manager, game_state):
        """Test transition from incomplete to complete."""
        # Start with blocks remaining
        events1 = manager.check_level_complete(blocks_remaining=1)
        assert not game_state.level_state.is_level_complete()
        assert len(events1) == 0

        # Now no blocks remain
        events2 = manager.check_level_complete(blocks_remaining=0)
        assert game_state.level_state.is_level_complete()
        assert len(events2) == 2


class TestGameStateManagerTimer:
    """Tests for timer management."""

    def test_timer_updates_when_active(self, manager, game_state):
        """Test that timer updates when game is active."""
        # Set initial timer value
        game_state.level_state.timer = 100  # 100 seconds
        initial_time = game_state.level_state.get_bonus_time()

        # Update timer while active (need >= 1000ms to see timer decrease)
        events = manager.update_timer(delta_ms=1000.0, is_active=True)

        # Timer should have decreased by 1 second
        assert game_state.level_state.get_bonus_time() < initial_time
        assert game_state.level_state.get_bonus_time() == initial_time - 1

        # Should return TimerUpdatedEvent
        assert len(events) == 1
        assert isinstance(events[0], TimerUpdatedEvent)

    def test_timer_does_not_update_when_inactive(self, manager, game_state):
        """Test that timer does not update when game is inactive."""
        initial_time = game_state.level_state.get_bonus_time()

        # Update timer while inactive
        events = manager.update_timer(delta_ms=100.0, is_active=False)

        # Timer should not have changed
        assert game_state.level_state.get_bonus_time() == initial_time

        # Should return no events
        assert len(events) == 0

    def test_timer_countdown(self, manager, game_state):
        """Test timer countdown over multiple updates."""
        # Set initial time
        game_state.level_state.timer = 100  # 100 seconds
        initial_time = game_state.level_state.get_bonus_time()

        # Update multiple times (need >= 1000ms total to see timer decrease)
        for _ in range(10):
            events = manager.update_timer(delta_ms=500.0, is_active=True)
            assert len(events) == 1

        # Timer should have decreased by approximately 5 seconds (10 * 500ms = 5000ms)
        final_time = game_state.level_state.get_bonus_time()
        assert final_time == initial_time - 5

    def test_timer_event_contains_current_time(self, manager, game_state):
        """Test that timer event contains the current timer value."""
        events = manager.update_timer(delta_ms=100.0, is_active=True)

        assert len(events) == 1
        timer_event = events[0]
        assert isinstance(timer_event, TimerUpdatedEvent)

        # Event should contain current time
        assert hasattr(timer_event, "time_remaining")
        assert timer_event.time_remaining == game_state.level_state.get_bonus_time()


class TestGameStateManagerGameOver:
    """Tests for game over state checking."""

    def test_is_game_over_when_lives_zero(self, manager, game_state):
        """Test game over detection when lives reach zero."""
        game_state.lives = 0
        game_state.set_game_over(True)
        assert manager.is_game_over()

    def test_is_not_game_over_with_lives_remaining(self, manager, game_state):
        """Test game over not detected when lives remain."""
        game_state.lives = 3
        assert not manager.is_game_over()

    def test_is_game_over_reflects_game_state(self, manager, game_state):
        """Test that is_game_over reflects underlying game_state."""
        # Start with lives
        game_state.lives = 2
        assert not manager.is_game_over()

        # Lose lives
        game_state.lives = 1
        assert not manager.is_game_over()

        # Game over (need to set flag)
        game_state.lives = 0
        game_state.set_game_over(True)
        assert manager.is_game_over()


class TestGameStateManagerResetLevel:
    """Tests for level reset functionality."""

    def test_reset_level_does_not_crash(self, manager):
        """Test that reset_level can be called without error."""
        # Currently reset_level is a no-op, but test it exists
        manager.reset_level()  # Should not raise

    def test_reset_level_logs(self, manager, caplog):
        """Test that reset_level logs a message."""
        caplog.set_level(logging.DEBUG)

        manager.reset_level()

        # Should log a reset message
        assert "Level state reset" in caplog.text


class TestGameStateManagerIntegration:
    """Integration tests for GameStateManager."""

    def test_complete_game_cycle(self, manager, game_state):
        """Test a complete game cycle: play, lose lives, game over."""
        # Start with 3 lives
        game_state.lives = 3

        # Play and lose first life
        manager.handle_life_loss(has_active_balls=False)
        assert game_state.lives == 2
        assert not manager.is_game_over()

        # Complete a level
        manager.check_level_complete(blocks_remaining=0)
        assert game_state.level_state.is_level_complete()

        # Continue playing, lose second life
        manager.handle_life_loss(has_active_balls=False)
        assert game_state.lives == 1

        # Lose final life
        manager.handle_life_loss(has_active_balls=False)
        assert game_state.lives == 0
        assert manager.is_game_over()

    def test_timer_and_level_complete_interaction(self, manager, game_state):
        """Test timer behavior around level completion."""
        # Update timer while playing
        events1 = manager.update_timer(delta_ms=100.0, is_active=True)
        assert len(events1) == 1

        # Complete level
        manager.check_level_complete(blocks_remaining=0)
        assert game_state.level_state.is_level_complete()

        # Timer should not update after level complete
        is_active = not game_state.level_state.is_level_complete()
        events3 = manager.update_timer(delta_ms=100.0, is_active=is_active)
        assert len(events3) == 0

    def test_life_loss_and_game_over_interaction(self, manager, game_state):
        """Test life loss behavior around game over."""
        # Set to 1 life
        game_state.lives = 1

        # Lose last life (should trigger game over)
        events = manager.handle_life_loss(has_active_balls=False)

        # Should have both life lost and game over events
        assert any(isinstance(e, LivesChangedEvent) for e in events)
        assert any(isinstance(e, GameOverEvent) for e in events)
        assert manager.is_game_over()

        # Trying to lose another life should do nothing
        events2 = manager.handle_life_loss(has_active_balls=False)
        assert len(events2) == 0
