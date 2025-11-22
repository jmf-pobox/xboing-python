"""Game input controller for handling game-level input.

This module defines the GameInputController class, which is responsible for
handling game-level input such as quit, pause, debug keys, ammo firing, and
ball launching.
"""

from typing import List

import pygame

from xboing.engine.events import (
    AmmoFiredEvent,
    ApplauseEvent,
    BallLostEvent,
    BallShotEvent,
    LevelCompleteEvent,
)
from xboing.engine.input import InputManager
from xboing.game.ball_manager import BallManager
from xboing.game.block_manager import BlockManager
from xboing.game.bullet import Bullet
from xboing.game.bullet_manager import BulletManager
from xboing.game.game_state import GameState
from xboing.game.level_manager import LevelManager
from xboing.game.paddle import Paddle
from xboing.layout.game_layout import GameLayout
from xboing.utils.event_helpers import post_level_title_message


class GameInputController:
    """Controller for handling game-level input."""

    def __init__(
        self,
        game_state: GameState,
        level_manager: LevelManager,
        ball_manager: BallManager,
        paddle: Paddle,
        block_manager: BlockManager,
        bullet_manager: BulletManager,
        input_manager: InputManager,
        layout: GameLayout,
    ) -> None:
        """Initialize the game input controller.

        Args:
            game_state: The game state.
            level_manager: The level manager.
            ball_manager: The ball manager.
            paddle: The paddle.
            block_manager: The block manager.
            bullet_manager: The bullet manager.
            input_manager: The input manager for getting input state.
            layout: The game layout.

        """
        self.game_state = game_state
        self.level_manager = level_manager
        self.ball_manager = ball_manager
        self.paddle = paddle
        self.block_manager = block_manager
        self.bullet_manager = bullet_manager
        self.input_manager = input_manager
        self.layout = layout
        self.paused = False
        self.stuck_ball_timer = 0.0
        self.ball_auto_active_delay_ms = 3000.0  # 3 seconds

    def handle_events(
        self, events: List[pygame.event.Event]
    ) -> List[pygame.event.Event]:
        """Handle game events.

        Args:
            events: List of Pygame events to process.

        Returns:
            List of events to post to the Pygame event queue.

        """
        events_to_post: List[pygame.event.Event] = []

        for event in events:
            # Handle quit event
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_q
            ):
                events_to_post.append(pygame.event.Event(pygame.QUIT))
                continue

            # Handle ammo firing or ball launching
            is_k_key = event.type == pygame.KEYDOWN and event.key == pygame.K_k
            is_mouse_button = event.type == pygame.MOUSEBUTTONDOWN
            if is_k_key or is_mouse_button:
                if self.ball_manager.has_ball_in_play():
                    # Fire ammo
                    if self.game_state.ammo > 0:  # Only fire if we have ammo
                        changes = self.game_state.fire_ammo()
                        for change in changes:
                            events_to_post.append(
                                pygame.event.Event(pygame.USEREVENT, {"event": change})
                            )
                        events_to_post.append(
                            pygame.event.Event(
                                pygame.USEREVENT,
                                {"event": AmmoFiredEvent(ammo=self.game_state.ammo)},
                            )
                        )
                        # Create and add bullet
                        bullet_x = self.paddle.rect.centerx
                        bullet_y = self.paddle.rect.top
                        bullet = Bullet(bullet_x, bullet_y)
                        self.bullet_manager.add_bullet(bullet)
                else:
                    # Launch ball(s)
                    balls = self.ball_manager.balls
                    for ball in balls:
                        ball.release_from_paddle()
                    self.stuck_ball_timer = 0.0  # Reset timer on manual launch
                    changes = self.game_state.set_timer(
                        self.game_state.level_state.get_bonus_time()
                    )
                    for change in changes:
                        events_to_post.append(
                            pygame.event.Event(pygame.USEREVENT, {"event": change})
                        )
                    events_to_post.append(
                        pygame.event.Event(pygame.USEREVENT, {"event": BallShotEvent()})
                    )
                    level_info = self.level_manager.get_level_info()
                    level_title = str(level_info["title"])
                    post_level_title_message(level_title)

            # Handle BallLostEvent - don't re-post it to avoid duplicate sound effects
            # The event is already in the event queue and will be handled by GameController
            if event.type == pygame.USEREVENT and isinstance(
                event.event, BallLostEvent
            ):
                # Don't add to events_to_post to avoid duplicate events
                pass

            # Handle pause toggle
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                self.paused = not self.paused

        return events_to_post

    def handle_debug_keys(self) -> List[pygame.event.Event]:
        """Handle debug keys.

        Returns:
            List of events to post to the Pygame event queue.

        """
        events_to_post: List[pygame.event.Event] = []

        # Handle debug X key (destroy all blocks)
        if self.input_manager.is_key_pressed(pygame.K_x):
            for block in self.block_manager.blocks:
                block.hit()
            self.block_manager.blocks.clear()
            self.game_state.level_state.set_level_complete()
            events_to_post.append(
                pygame.event.Event(pygame.USEREVENT, {"event": LevelCompleteEvent()})
            )
            events_to_post.append(
                pygame.event.Event(pygame.USEREVENT, {"event": ApplauseEvent()})
            )

        return events_to_post

    def update_stuck_ball_timer(self, delta_ms: float) -> List[pygame.event.Event]:
        """Update the stuck ball timer and auto-launch balls if needed.

        Args:
            delta_ms: Time elapsed since last update in milliseconds.

        Returns:
            List of events to post to the Pygame event queue.

        """
        events_to_post: List[pygame.event.Event] = []
        stuck_balls = [ball for ball in self.ball_manager.balls if ball.stuck_to_paddle]

        if stuck_balls:
            self.stuck_ball_timer += delta_ms
            if self.stuck_ball_timer >= self.ball_auto_active_delay_ms:
                for ball in stuck_balls:
                    ball.release_from_paddle()
                self.stuck_ball_timer = 0.0
                events_to_post.append(
                    pygame.event.Event(pygame.USEREVENT, {"event": BallShotEvent()})
                )
        else:
            self.stuck_ball_timer = 0.0

        return events_to_post

    def is_paused(self) -> bool:
        """Check if the game is paused.

        Returns:
            True if the game is paused, False otherwise.

        """
        return self.paused
