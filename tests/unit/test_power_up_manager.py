"""Tests for PowerUpManager."""

import logging
from unittest.mock import Mock

import pytest

from xboing.engine.events import (
    AmmoCollectedEvent,
    BombExplodedEvent,
    PaddleGrowEvent,
    PaddleShrinkEvent,
    SpecialReverseChangedEvent,
    SpecialStickyChangedEvent,
)
from xboing.game.block_types import (
    BOMB_BLK,
    BULLET_BLK,
    MAXAMMO_BLK,
    PAD_EXPAND_BLK,
    PAD_SHRINK_BLK,
    REVERSE_BLK,
    STICKY_BLK,
)
from xboing.game.game_state import GameState
from xboing.game.paddle import Paddle
from xboing.game.power_up_manager import PowerUpManager


@pytest.fixture
def paddle():
    """Create a paddle for testing."""
    return Paddle(x=400, y=550)


@pytest.fixture
def game_state():
    """Create a game state for testing."""
    return GameState()


@pytest.fixture
def manager(game_state, paddle):
    """Create a power-up manager for testing."""
    return PowerUpManager(game_state, paddle)


@pytest.fixture
def dummy_block():
    """Create a dummy block for testing (unused, so using Mock)."""
    return Mock()


class TestPowerUpManagerInitialization:
    """Tests for PowerUpManager initialization."""

    def test_initialization(self, manager, game_state, paddle):
        """Test that PowerUpManager initializes correctly."""
        assert manager.game_state is game_state
        assert manager.paddle is paddle
        assert manager.sticky is False
        assert manager.reverse is False

    def test_logger_configured(self, manager):
        """Test that logger is properly configured."""
        assert manager.logger.name == "xboing.PowerUpManager"


class TestPowerUpManagerBombEffect:
    """Tests for bomb power-up effect."""

    def test_bomb_effect_returns_event(self, manager, dummy_block):
        """Test that bomb effect returns BombExplodedEvent."""
        events = manager.handle_power_up_effect(BOMB_BLK, dummy_block)

        assert len(events) == 1
        assert isinstance(events[0], BombExplodedEvent)

    def test_bomb_effect_does_not_change_state(self, manager, dummy_block):
        """Test that bomb effect doesn't change manager state."""
        initial_sticky = manager.sticky
        initial_reverse = manager.reverse

        manager.handle_power_up_effect(BOMB_BLK, dummy_block)

        assert manager.sticky == initial_sticky
        assert manager.reverse == initial_reverse


class TestPowerUpManagerAmmoEffect:
    """Tests for ammo power-up effects."""

    def test_bullet_block_adds_ammo(self, manager, game_state, dummy_block):
        """Test that bullet block adds ammo."""
        initial_ammo = game_state.ammo

        events = manager.handle_power_up_effect(BULLET_BLK, dummy_block)

        assert game_state.ammo > initial_ammo
        assert any(isinstance(e, AmmoCollectedEvent) for e in events)

    def test_maxammo_block_adds_ammo(self, manager, game_state, dummy_block):
        """Test that max ammo block adds ammo."""
        initial_ammo = game_state.ammo

        events = manager.handle_power_up_effect(MAXAMMO_BLK, dummy_block)

        assert game_state.ammo > initial_ammo
        assert any(isinstance(e, AmmoCollectedEvent) for e in events)


class TestPowerUpManagerPaddleSizeEffects:
    """Tests for paddle size power-up effects."""

    def test_paddle_grow_increases_size(self, manager, paddle, dummy_block):
        """Test that paddle grow increases paddle size."""
        paddle.set_size(Paddle.SIZE_MEDIUM)
        initial_size = paddle.size

        events = manager.handle_power_up_effect(PAD_EXPAND_BLK, dummy_block)

        assert paddle.size == initial_size + 1
        assert any(isinstance(e, PaddleGrowEvent) for e in events)

    def test_paddle_grow_at_max_size(self, manager, paddle, dummy_block):
        """Test paddle grow when already at maximum size."""
        paddle.set_size(Paddle.SIZE_LARGE)

        events = manager.handle_power_up_effect(PAD_EXPAND_BLK, dummy_block)

        # Size should stay at max
        assert paddle.size == Paddle.SIZE_LARGE

        # Event should indicate at_max
        assert len(events) == 1
        grow_event = events[0]
        assert isinstance(grow_event, PaddleGrowEvent)
        assert grow_event.at_max is True

    def test_paddle_shrink_decreases_size(self, manager, paddle, dummy_block):
        """Test that paddle shrink decreases paddle size."""
        paddle.set_size(Paddle.SIZE_MEDIUM)
        initial_size = paddle.size

        events = manager.handle_power_up_effect(PAD_SHRINK_BLK, dummy_block)

        assert paddle.size == initial_size - 1
        assert any(isinstance(e, PaddleShrinkEvent) for e in events)

    def test_paddle_shrink_at_min_size(self, manager, paddle, dummy_block):
        """Test paddle shrink when already at minimum size."""
        paddle.set_size(Paddle.SIZE_SMALL)

        events = manager.handle_power_up_effect(PAD_SHRINK_BLK, dummy_block)

        # Size should stay at min
        assert paddle.size == Paddle.SIZE_SMALL

        # Event should indicate at_min
        assert len(events) == 1
        shrink_event = events[0]
        assert isinstance(shrink_event, PaddleShrinkEvent)
        assert shrink_event.at_min is True

    def test_paddle_size_transitions(self, manager, paddle, dummy_block):
        """Test paddle size transitions through all sizes."""
        # Start at small
        paddle.set_size(Paddle.SIZE_SMALL)
        assert paddle.size == Paddle.SIZE_SMALL

        # Grow to medium
        manager.handle_power_up_effect(PAD_EXPAND_BLK, dummy_block)
        assert paddle.size == Paddle.SIZE_MEDIUM

        # Grow to large
        manager.handle_power_up_effect(PAD_EXPAND_BLK, dummy_block)
        assert paddle.size == Paddle.SIZE_LARGE

        # Shrink to medium
        manager.handle_power_up_effect(PAD_SHRINK_BLK, dummy_block)
        assert paddle.size == Paddle.SIZE_MEDIUM

        # Shrink to small
        manager.handle_power_up_effect(PAD_SHRINK_BLK, dummy_block)
        assert paddle.size == Paddle.SIZE_SMALL


class TestPowerUpManagerReverseEffect:
    """Tests for reverse controls power-up effect."""

    def test_reverse_toggles_from_false_to_true(self, manager, dummy_block):
        """Test that reverse toggles from false to true."""
        assert manager.reverse is False

        events = manager.handle_power_up_effect(REVERSE_BLK, dummy_block)

        assert manager.reverse is True
        assert any(isinstance(e, SpecialReverseChangedEvent) for e in events)
        assert any(
            e.active is True
            for e in events
            if isinstance(e, SpecialReverseChangedEvent)
        )

    def test_reverse_toggles_from_true_to_false(self, manager, dummy_block):
        """Test that reverse toggles from true to false."""
        manager.reverse = True

        events = manager.handle_power_up_effect(REVERSE_BLK, dummy_block)

        assert manager.reverse is False
        assert any(isinstance(e, SpecialReverseChangedEvent) for e in events)
        assert any(
            e.active is False
            for e in events
            if isinstance(e, SpecialReverseChangedEvent)
        )

    def test_reverse_multiple_toggles(self, manager, dummy_block):
        """Test multiple reverse toggles."""
        # Start false
        assert manager.reverse is False

        # Toggle to true
        manager.handle_power_up_effect(REVERSE_BLK, dummy_block)
        assert manager.reverse is True

        # Toggle to false
        manager.handle_power_up_effect(REVERSE_BLK, dummy_block)
        assert manager.reverse is False

        # Toggle to true again
        manager.handle_power_up_effect(REVERSE_BLK, dummy_block)
        assert manager.reverse is True


class TestPowerUpManagerStickyEffect:
    """Tests for sticky paddle power-up effect."""

    def test_sticky_activates(self, manager, paddle, dummy_block):
        """Test that sticky activates correctly."""
        assert manager.sticky is False
        assert paddle.sticky is False

        events = manager.handle_power_up_effect(STICKY_BLK, dummy_block)

        assert manager.sticky is True
        assert paddle.sticky is True
        assert any(isinstance(e, SpecialStickyChangedEvent) for e in events)
        assert any(
            e.active is True for e in events if isinstance(e, SpecialStickyChangedEvent)
        )

    def test_sticky_when_already_active(self, manager, paddle, dummy_block):
        """Test sticky activation when already active."""
        manager.sticky = True
        paddle.sticky = True

        events = manager.handle_power_up_effect(STICKY_BLK, dummy_block)

        # Should still be active
        assert manager.sticky is True
        assert paddle.sticky is True
        assert any(isinstance(e, SpecialStickyChangedEvent) for e in events)


class TestPowerUpManagerStateManagement:
    """Tests for power-up state management methods."""

    def test_set_sticky_true(self, manager, paddle):
        """Test setting sticky to true."""
        manager.set_sticky(True)

        assert manager.sticky is True
        assert paddle.sticky is True

    def test_set_sticky_false(self, manager, paddle):
        """Test setting sticky to false."""
        manager.sticky = True
        paddle.sticky = True

        manager.set_sticky(False)

        assert manager.sticky is False
        assert paddle.sticky is False

    def test_set_reverse_true(self, manager):
        """Test setting reverse to true."""
        manager.set_reverse(True)

        assert manager.reverse is True

    def test_set_reverse_false(self, manager):
        """Test setting reverse to false."""
        manager.reverse = True

        manager.set_reverse(False)

        assert manager.reverse is False

    def test_is_sticky_active_when_active(self, manager):
        """Test is_sticky_active returns True when active."""
        manager.sticky = True

        assert manager.is_sticky_active() is True

    def test_is_sticky_active_when_inactive(self, manager):
        """Test is_sticky_active returns False when inactive."""
        manager.sticky = False

        assert manager.is_sticky_active() is False

    def test_is_reverse_active_when_active(self, manager):
        """Test is_reverse_active returns True when active."""
        manager.reverse = True

        assert manager.is_reverse_active() is True

    def test_is_reverse_active_when_inactive(self, manager):
        """Test is_reverse_active returns False when inactive."""
        manager.reverse = False

        assert manager.is_reverse_active() is False


class TestPowerUpManagerReset:
    """Tests for power-up reset functionality."""

    def test_reset_clears_sticky(self, manager, paddle):
        """Test that reset clears sticky state."""
        manager.sticky = True
        paddle.sticky = True

        manager.reset_power_ups()

        assert manager.sticky is False
        assert paddle.sticky is False

    def test_reset_clears_reverse(self, manager):
        """Test that reset clears reverse state."""
        manager.reverse = True

        manager.reset_power_ups()

        assert manager.reverse is False

    def test_reset_clears_all_power_ups(self, manager, paddle):
        """Test that reset clears all power-up states."""
        # Activate all power-ups
        manager.sticky = True
        paddle.sticky = True
        manager.reverse = True

        # Reset
        manager.reset_power_ups()

        # All should be cleared
        assert manager.sticky is False
        assert paddle.sticky is False
        assert manager.reverse is False

    def test_reset_does_not_crash_when_already_reset(self, manager):
        """Test that reset can be called when already reset."""
        manager.reset_power_ups()  # Should not raise
        manager.reset_power_ups()  # Should not raise again

    def test_reset_logs_message(self, manager, caplog):
        """Test that reset logs a message."""
        caplog.set_level(logging.DEBUG)

        manager.reset_power_ups()

        assert "All power-ups reset" in caplog.text


class TestPowerUpManagerIntegration:
    """Integration tests for PowerUpManager."""

    def test_multiple_power_up_sequence(self, manager, paddle, dummy_block):
        """Test a sequence of multiple power-ups."""
        # Start clean (paddle starts at SIZE_LARGE by default)
        assert manager.sticky is False
        assert manager.reverse is False
        initial_size = paddle.size

        # Activate sticky
        manager.handle_power_up_effect(STICKY_BLK, dummy_block)
        assert manager.sticky is True

        # Activate reverse
        manager.handle_power_up_effect(REVERSE_BLK, dummy_block)
        assert manager.reverse is True

        # Shrink paddle (since it starts at SIZE_LARGE)
        manager.handle_power_up_effect(PAD_SHRINK_BLK, dummy_block)
        assert paddle.size == initial_size - 1

        # All should still be active
        assert manager.sticky is True
        assert manager.reverse is True
        assert paddle.size == initial_size - 1

    def test_reset_after_power_ups(self, manager, paddle, dummy_block):
        """Test reset after activating multiple power-ups."""
        # Activate multiple power-ups
        manager.handle_power_up_effect(STICKY_BLK, dummy_block)
        manager.handle_power_up_effect(REVERSE_BLK, dummy_block)
        manager.handle_power_up_effect(PAD_EXPAND_BLK, dummy_block)

        # Verify active
        assert manager.sticky is True
        assert manager.reverse is True

        # Reset
        manager.reset_power_ups()

        # Sticky and reverse should be cleared
        assert manager.sticky is False
        assert manager.reverse is False

        # Note: paddle size is NOT reset by reset_power_ups()
        # (paddle size persists across resets in the original game)

    def test_sticky_and_reverse_interaction(self, manager, dummy_block):
        """Test that sticky and reverse are independent."""
        # Activate sticky
        manager.handle_power_up_effect(STICKY_BLK, dummy_block)
        assert manager.sticky is True
        assert manager.reverse is False

        # Activate reverse
        manager.handle_power_up_effect(REVERSE_BLK, dummy_block)
        assert manager.sticky is True
        assert manager.reverse is True

        # Deactivate reverse
        manager.handle_power_up_effect(REVERSE_BLK, dummy_block)
        assert manager.sticky is True
        assert manager.reverse is False

        # Deactivate sticky
        manager.set_sticky(False)
        assert manager.sticky is False
        assert manager.reverse is False
