"""Collision handlers for game objects in XBoing Python.

This module defines handlers for different types of collisions between game objects.
It encapsulates the collision response logic, separating it from the game controller.
"""

import logging
from typing import Any, List, Optional

import pygame

from xboing.engine.events import (
    BallLostEvent,
    BlockHitEvent,
    PaddleHitEvent,
)
from xboing.game.ball_manager import BallManager
from xboing.game.block import Block
from xboing.game.block_manager import BlockManager
from xboing.game.block_types import SPECIAL_BLOCK_TYPES
from xboing.game.bullet_manager import BulletManager
from xboing.game.game_state import GameState
from xboing.game.paddle import Paddle
from xboing.game.power_up_manager import PowerUpManager


class CollisionHandlers:
    """Handlers for different types of collisions between game objects."""

    def __init__(
        self,
        game_state: GameState,
        paddle: Paddle,
        ball_manager: BallManager,
        bullet_manager: BulletManager,
        power_up_manager: PowerUpManager,
        block_manager: Optional[BlockManager] = None,
    ) -> None:
        """Initialize the collision handlers.

        Args:
            game_state: The game state instance.
            paddle: The paddle instance.
            ball_manager: The ball manager instance.
            bullet_manager: The bullet manager instance.
            power_up_manager: The power-up manager instance.
            block_manager: The block manager instance.

        """
        self.game_state = game_state
        self.paddle = paddle
        self.ball_manager = ball_manager
        self.bullet_manager = bullet_manager
        self.power_up_manager = power_up_manager
        self.block_manager = block_manager
        self.logger = logging.getLogger("xboing.CollisionHandlers")

    def handle_ball_block_collision(
        self, ball: Any, block: Any
    ) -> List[pygame.event.Event]:
        """Handle collision between a ball and a block.

        Args:
            ball: The ball involved in the collision.
            block: The block involved in the collision.

        Returns:
            List of events to be posted by the caller.

        """
        events: List[pygame.event.Event] = []

        if not ball.is_active() or not block.is_active():
            return events

        # Skip blocks that are not in normal state
        if block.state != "normal":
            return events

        # Skip blocks that have already been hit this frame
        if block.hit_this_frame:
            return events

        # Reflect the ball off the block
        if self.block_manager:
            # Get ball position
            ball_x, ball_y = ball.get_position()
            # Call the block manager's reflect_ball method to handle the physics
            self.block_manager.reflect_ball(ball, ball_x, ball_y, block)

        # Get collision results directly from the block
        broken, points, effect = block.hit()

        # Update score if points were earned
        if points > 0:
            changes = self.game_state.add_score(points)
            events.extend(self._create_events_from_changes(changes))

        # Handle block effects
        if broken:
            if effect in SPECIAL_BLOCK_TYPES:
                events.extend(self.handle_block_effects(effect, block))
            else:
                # Add BlockHitEvent for normal blocks
                events.append(
                    pygame.event.Event(pygame.USEREVENT, {"event": BlockHitEvent()})
                )

        return events

    def handle_ball_paddle_collision(
        self, ball: Any, paddle: Any
    ) -> List[pygame.event.Event]:
        """Handle collision between a ball and the paddle.

        Args:
            ball: The ball involved in the collision.
            paddle: The paddle involved in the collision.

        Returns:
            List of events to be posted by the caller.

        """
        events: List[pygame.event.Event] = [
            pygame.event.Event(pygame.USEREVENT, {"event": PaddleHitEvent()})
        ]

        if self.power_up_manager.is_sticky_active() and not ball.stuck_to_paddle:
            ball.stuck_to_paddle = True
            ball.paddle_offset = ball.x - paddle.rect.centerx

        return events

    def handle_bullet_block_collision(
        self, bullet: Any, block: Any
    ) -> List[pygame.event.Event]:
        """Handle collision between a bullet and a block.

        Args:
            bullet: The bullet involved in the collision.
            block: The block involved in the collision.

        Returns:
            List of events to be posted by the caller.

        """
        events: List[pygame.event.Event] = []

        if not bullet.is_active() or not block.is_active() or not self.block_manager:
            return events

        points, broken, effects = self.block_manager.check_collisions(bullet)

        if points != 0:
            changes = self.game_state.add_score(points)
            events.extend(self._create_events_from_changes(changes))

        if broken > 0:
            if not any(effect in SPECIAL_BLOCK_TYPES for effect in effects):
                events.append(
                    pygame.event.Event(pygame.USEREVENT, {"event": BlockHitEvent()})
                )
            else:
                # Handle special block effects
                for effect in effects:
                    if effect in SPECIAL_BLOCK_TYPES:
                        events.extend(self.handle_block_effects(effect, block))

        if not bullet.active:
            self.bullet_manager.remove_bullet(bullet)

        return events

    def handle_bullet_ball_collision(
        self, bullet: Any, ball: Any
    ) -> List[pygame.event.Event]:
        """Handle collision between a bullet and a ball.

        Args:
            bullet: The bullet involved in the collision.
            ball: The ball involved in the collision.

        Returns:
            List of events to be posted by the caller.

        """
        events: List[pygame.event.Event] = []

        if bullet.is_active() and ball.is_active():
            bullet.set_active(False)
            ball.set_active(False)
            events.append(
                pygame.event.Event(pygame.USEREVENT, {"event": BallLostEvent()})
            )
            self.bullet_manager.remove_bullet(bullet)
            self.ball_manager.remove_ball(ball)

        return events

    def handle_block_effects(
        self, effect: str, block: Block
    ) -> List[pygame.event.Event]:
        """Handle special block effects and return appropriate events.

        Args:
            effect: The block effect type constant.
            block: The block object that was hit.

        Returns:
            List of events to be posted by the caller.

        """
        # Delegate to PowerUpManager for all power-up effects
        changes = self.power_up_manager.handle_power_up_effect(effect, block)
        return self._create_events_from_changes(changes)

    def set_sticky(self, value: bool) -> None:
        """Set the sticky paddle state.

        Args:
            value: The new sticky state.

        """
        self.power_up_manager.set_sticky(value)

    def set_reverse(self, value: bool) -> None:
        """Set the reverse paddle control state.

        Args:
            value: The new reverse state.

        """
        self.power_up_manager.set_reverse(value)

    @property
    def sticky(self) -> bool:
        """Get the sticky paddle state for backward compatibility.

        Returns:
            True if sticky is active, False otherwise.

        """
        return self.power_up_manager.is_sticky_active()

    @property
    def reverse(self) -> bool:
        """Get the reverse controls state for backward compatibility.

        Returns:
            True if reverse is active, False otherwise.

        """
        return self.power_up_manager.is_reverse_active()

    @staticmethod
    def _create_events_from_changes(changes: List[Any]) -> List[pygame.event.Event]:
        """Convert GameState/model event objects into pygame events.

        This implements the decoupled event firing pattern: models return event objects,
        which are converted to pygame events and returned to the caller for posting.

        Args:
            changes: List of event objects from GameState/model methods.

        Returns:
            List of pygame events to be posted by the caller.

        """
        return [
            pygame.event.Event(pygame.USEREVENT, {"event": change})
            for change in changes
        ]
