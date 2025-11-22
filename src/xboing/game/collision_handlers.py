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

    def handle_ball_block_collision(self, ball: Any, block: Any) -> None:
        """Handle collision between a ball and a block.

        Args:
            ball: The ball involved in the collision.
            block: The block involved in the collision.

        """
        if not ball.is_active() or not block.is_active():
            return

        # Skip blocks that are not in normal state
        if block.state != "normal":
            return

        # Skip blocks that have already been hit this frame
        if block.hit_this_frame:
            return

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
            self.post_game_state_events(changes)

        # Handle block effects
        if broken:
            if effect in SPECIAL_BLOCK_TYPES:
                self.handle_block_effects(effect, block)
            else:
                # Post BlockHitEvent for normal blocks
                pygame.event.post(
                    pygame.event.Event(pygame.USEREVENT, {"event": BlockHitEvent()})
                )

    def handle_ball_paddle_collision(self, ball: Any, paddle: Any) -> None:
        """Handle collision between a ball and the paddle.

        Args:
            ball: The ball involved in the collision.
            paddle: The paddle involved in the collision.

        """
        pygame.event.post(
            pygame.event.Event(pygame.USEREVENT, {"event": PaddleHitEvent()})
        )
        if self.power_up_manager.is_sticky_active() and not ball.stuck_to_paddle:
            ball.stuck_to_paddle = True
            ball.paddle_offset = ball.x - paddle.rect.centerx

    def handle_bullet_block_collision(self, bullet: Any, block: Any) -> None:
        """Handle collision between a bullet and a block.

        Args:
            bullet: The bullet involved in the collision.
            block: The block involved in the collision.

        """
        if not bullet.is_active() or not block.is_active() or not self.block_manager:
            return
        points, broken, effects = self.block_manager.check_collisions(bullet)
        if points != 0:
            changes = self.game_state.add_score(points)
            self.post_game_state_events(changes)
        if broken > 0:
            if not any(effect in SPECIAL_BLOCK_TYPES for effect in effects):
                pygame.event.post(
                    pygame.event.Event(pygame.USEREVENT, {"event": BlockHitEvent()})
                )
            else:
                # Handle special block effects
                for effect in effects:
                    if effect in SPECIAL_BLOCK_TYPES:
                        self.handle_block_effects(effect, block)
        if not bullet.active:
            self.bullet_manager.remove_bullet(bullet)

    def handle_bullet_ball_collision(self, bullet: Any, ball: Any) -> None:
        """Handle collision between a bullet and a ball.

        Args:
            bullet: The bullet involved in the collision.
            ball: The ball involved in the collision.

        """
        if bullet.is_active() and ball.is_active():
            bullet.set_active(False)
            ball.set_active(False)
            pygame.event.post(
                pygame.event.Event(pygame.USEREVENT, {"event": BallLostEvent()})
            )
            self.bullet_manager.remove_bullet(bullet)
            self.ball_manager.remove_ball(ball)

    def handle_block_effects(self, effect: str, block: Block) -> None:
        """Handle special block effects and post appropriate events.

        Args:
            effect: The block effect type constant.
            block: The block object that was hit.

        """
        # Delegate to PowerUpManager for all power-up effects
        events = self.power_up_manager.handle_power_up_effect(effect, block)
        self.post_game_state_events(events)

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
    def post_game_state_events(changes: List[Any]) -> None:
        """Post all events returned by GameState/model methods to the Pygame event queue.

        This implements the decoupled event firing pattern: models return events, controllers post them.

        Args:
            changes: List of event objects to post to the Pygame event queue.

        """
        for event in changes:
            pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"event": event}))
