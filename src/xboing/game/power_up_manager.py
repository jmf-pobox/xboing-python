"""Power-up manager for XBoing.

This module manages power-up state and effects including sticky paddle,
reverse controls, paddle size changes, and special block effects.
It centralizes power-up logic that was previously scattered across
CollisionHandlers and GameController.
"""

import logging
from typing import List

from xboing.engine.events import (
    BombExplodedEvent,
    PaddleGrowEvent,
    PaddleShrinkEvent,
    SpecialReverseChangedEvent,
    SpecialStickyChangedEvent,
)
from xboing.game.block import Block
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


class PowerUpManager:
    """Manages power-up state and effects for the game.

    This manager is responsible for:
    - Sticky paddle state
    - Reverse controls state
    - Paddle size changes (grow/shrink)
    - Special block effects (bomb, ammo, etc.)
    - Power-up event generation

    It separates power-up concerns from collision handling and game control,
    making the code more maintainable and testable.
    """

    def __init__(self, game_state: GameState, paddle: Paddle) -> None:
        """Initialize the power-up manager.

        Args:
            game_state: The game state instance for score/ammo management.
            paddle: The paddle instance for size/sticky state management.

        """
        self.game_state = game_state
        self.paddle = paddle
        self.sticky = False
        self.reverse = False
        self.logger = logging.getLogger("xboing.PowerUpManager")

    def handle_power_up_effect(self, effect: str, block: Block) -> List[object]:
        """Handle a power-up effect and return events to post.

        Args:
            effect: The block effect type constant (BOMB_BLK, STICKY_BLK, etc.).
            block: The block object that was hit (unused but kept for consistency).

        Returns:
            List of events to post (BombExplodedEvent, PaddleGrowEvent, etc.).

        """
        events: List[object] = []
        del block  # Remove unused argument warning

        if effect == BOMB_BLK:
            events.append(BombExplodedEvent())
            self.logger.debug("Bomb block hit - explosion event added")

        elif effect in (BULLET_BLK, MAXAMMO_BLK):
            # Add ammo through game state
            ammo_events = self.game_state.add_ammo()
            events.extend(ammo_events)
            self.logger.debug(f"Ammo block hit - added ammo ({effect})")

        elif effect == PAD_EXPAND_BLK:
            events.extend(self._handle_paddle_grow())

        elif effect == PAD_SHRINK_BLK:
            events.extend(self._handle_paddle_shrink())

        elif effect == REVERSE_BLK:
            events.extend(self._handle_reverse_toggle())

        elif effect == STICKY_BLK:
            events.extend(self._handle_sticky_activate())

        return events

    def _handle_paddle_grow(self) -> List[object]:
        """Handle paddle grow power-up.

        Returns:
            List containing PaddleGrowEvent.

        """
        events: List[object] = []

        if self.paddle.size < Paddle.SIZE_LARGE:
            self.paddle.set_size(self.paddle.size + 1)
            at_max = self.paddle.size == Paddle.SIZE_LARGE
        else:
            at_max = True

        events.append(PaddleGrowEvent(size=self.paddle.width, at_max=at_max))
        self.logger.debug(f"Paddle grow - size now {self.paddle.size}, at_max={at_max}")

        return events

    def _handle_paddle_shrink(self) -> List[object]:
        """Handle paddle shrink power-up.

        Returns:
            List containing PaddleShrinkEvent.

        """
        events: List[object] = []

        if self.paddle.size > Paddle.SIZE_SMALL:
            self.paddle.set_size(self.paddle.size - 1)
            at_min = self.paddle.size == Paddle.SIZE_SMALL
        else:
            at_min = True

        events.append(PaddleShrinkEvent(size=self.paddle.width, at_min=at_min))
        self.logger.debug(
            f"Paddle shrink - size now {self.paddle.size}, at_min={at_min}"
        )

        return events

    def _handle_reverse_toggle(self) -> List[object]:
        """Handle reverse controls toggle power-up.

        Returns:
            List containing SpecialReverseChangedEvent.

        """
        events: List[object] = []

        self.reverse = not self.reverse
        events.append(SpecialReverseChangedEvent(active=self.reverse))
        self.logger.debug(f"Reverse toggled - now {self.reverse}")

        return events

    def _handle_sticky_activate(self) -> List[object]:
        """Handle sticky paddle activation power-up.

        Returns:
            List containing SpecialStickyChangedEvent.

        """
        events: List[object] = []

        self.sticky = True
        self.paddle.sticky = True
        events.append(SpecialStickyChangedEvent(active=True))
        self.logger.debug("Sticky activated")

        return events

    def set_sticky(self, value: bool) -> None:
        """Set the sticky paddle state.

        Args:
            value: The new sticky state.

        """
        self.sticky = value
        self.paddle.sticky = value
        self.logger.debug(f"Sticky set to {value}")

    def set_reverse(self, value: bool) -> None:
        """Set the reverse controls state.

        Args:
            value: The new reverse state.

        """
        self.reverse = value
        self.logger.debug(f"Reverse set to {value}")

    def is_sticky_active(self) -> bool:
        """Check if sticky paddle is currently active.

        Returns:
            True if sticky is active, False otherwise.

        """
        return self.sticky

    def is_reverse_active(self) -> bool:
        """Check if reverse controls are currently active.

        Returns:
            True if reverse is active, False otherwise.

        """
        return self.reverse

    def reset_power_ups(self) -> None:
        """Reset all power-up states (for new level or life loss).

        This disables sticky and reverse, and resets paddle to normal size.
        """
        self.sticky = False
        self.paddle.sticky = False
        self.reverse = False
        self.logger.debug("All power-ups reset")
