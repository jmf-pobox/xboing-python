import logging
from typing import Any, List

import pygame

from engine.events import (
    ApplauseEvent,
    BallLostEvent,
    BallShotEvent,
    BlockHitEvent,
    BombExplodedEvent,
    LevelCompleteEvent,
    MessageChangedEvent,
    PaddleHitEvent,
    PowerUpCollectedEvent,
    WallHitEvent,
)
from game.ball import Ball

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class GameController:
    """
    Handles gameplay input, updates, and transitions for the GameView.
    Handles paddle, ball, block, and debug logic.

    **Event decoupling pattern:**
    GameState and other model methods do not post events directly. Instead, they return a list of event instances
    representing state changes. GameController is responsible for posting these events to the Pygame event queue
    using the post_game_state_events helper. This enables headless testing and decouples model logic from the event system.
    """

    BALL_RADIUS = (
        8  # Approximated from original game (move from main.py for consistency)
    )

    def __init__(
        self,
        game_state: Any,
        level_manager: Any,
        balls: Any,
        paddle: Any,
        block_manager: Any,
        input_manager: Any = None,
        layout: Any = None,
        renderer: Any = None,
        event_sound_map: Any = None,
    ) -> None:
        self.game_state = game_state
        self.level_manager = level_manager
        self.balls = balls
        self.paddle = paddle
        self.block_manager = block_manager
        self.input_manager = input_manager
        self.layout = layout
        self.renderer = renderer
        self.event_sound_map = event_sound_map
        self.waiting_for_launch = True
        self.level_complete = False

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        """
        Handle Pygame events for gameplay, including launching balls and handling BallLostEvent.

        Args:
            events: List of Pygame events to process.
        """
        for event in events:
            # Launch balls from paddle when mouse button is clicked
            if event.type == 1025 and self.waiting_for_launch:  # pygame.MOUSEBUTTONDOWN
                logger.debug("Launching ball(s) from paddle.")
                for i, ball in enumerate(self.balls):
                    logger.debug(f"Calling release_from_paddle on ball {i}")
                    ball.release_from_paddle()
                self.waiting_for_launch = False
                # GameState.set_timer now returns events, which must be posted by the controller
                changes = self.game_state.set_timer(
                    self.level_manager.get_time_remaining()
                )
                self.post_game_state_events(changes)
                self.level_manager.start_timer()
                pygame.event.post(
                    pygame.event.Event(pygame.USEREVENT, {"event": BallShotEvent()})
                )
                level_info = self.level_manager.get_level_info()
                level_title = level_info["title"]
                pygame.event.post(
                    pygame.event.Event(
                        pygame.USEREVENT,
                        {
                            "event": MessageChangedEvent(
                                level_title, color=(0, 255, 0), alignment="left"
                            )
                        },
                    )
                )
                logger.debug("Ball(s) launched and timer started.")

            # Check for BallLostEvent in the correct way
            if event.type == pygame.USEREVENT and isinstance(
                event.event, BallLostEvent
            ):
                logger.debug("BallLostEvent detected in GameController.")
                self.handle_life_loss()

    def update(self, delta_ms: float) -> None:
        """
        Update gameplay logic.

        Args:
            delta_ms: Time elapsed since last update in milliseconds.
        """
        if not self.input_manager or not self.layout:
            logger.warning(
                "GameController.update called without input_manager or layout."
            )
            return
        self.handle_paddle_input(delta_ms)
        self.handle_mouse_paddle_control()
        self.update_blocks_and_timer(delta_ms)
        self.update_balls_and_collisions(delta_ms)
        self.check_level_complete()
        self.handle_debug_x_key()

    def handle_paddle_input(self, delta_ms: float) -> None:
        """
        Handle paddle movement and input.

        Args:
            delta_ms: Time elapsed since last update in milliseconds.
        """
        if not self.input_manager or not self.layout:
            return
        paddle_direction = 0
        if self.input_manager.is_key_pressed(pygame.K_LEFT):
            paddle_direction = -1
        elif self.input_manager.is_key_pressed(pygame.K_RIGHT):
            paddle_direction = 1
        play_rect = self.layout.get_play_rect() if self.layout else None
        if play_rect:
            self.paddle.set_direction(paddle_direction)
            self.paddle.update(delta_ms, play_rect.width, play_rect.x)

    def handle_mouse_paddle_control(self) -> None:
        """
        Handle mouse-based paddle movement.
        """
        if not self.input_manager or not self.layout:
            return
        play_rect = self.layout.get_play_rect()
        mouse_pos = self.input_manager.get_mouse_position()
        if self.input_manager.is_mouse_button_pressed(0):
            local_x = mouse_pos[0] - play_rect.x - self.paddle.width // 2
            self.paddle.move_to(local_x, play_rect.width, play_rect.x)

    def update_blocks_and_timer(self, delta_ms: float) -> None:
        """
        Update blocks and timer if appropriate.

        Args:
            delta_ms: Time elapsed since last update in milliseconds.
        """
        self.block_manager.update(delta_ms)
        if (
            not self.waiting_for_launch
            and not self.game_state.is_game_over()
            and not self.level_complete
        ):
            self.level_manager.update(delta_ms)
            changes = self.game_state.set_timer(self.level_manager.get_time_remaining())
            self.post_game_state_events(changes)

    def update_balls_and_collisions(self, delta_ms: float) -> None:
        """
        Update balls, check for collisions, and handle block effects.

        Args:
            delta_ms: Time elapsed since last update in milliseconds.
        """
        active_balls = []
        for ball in self.balls:
            play_rect = self.layout.get_play_rect()
            is_active, hit_paddle, hit_wall = ball.update(
                delta_ms,
                play_rect.width,
                play_rect.height,
                self.paddle,
                play_rect.x,
                play_rect.y,
            )
            if is_active:
                points, broken, effects = self.block_manager.check_collisions(ball)
                if points != 0:
                    changes = self.game_state.add_score(points)
                    self.post_game_state_events(changes)
                if broken > 0:
                    pygame.event.post(
                        pygame.event.Event(pygame.USEREVENT, {"event": BlockHitEvent()})
                    )
                for effect in effects:
                    if effect == getattr(self.block_manager, "TYPE_EXTRABALL", None):
                        new_ball = Ball(ball.x, ball.y, ball.radius, (255, 255, 255))
                        new_ball.vx = -ball.vx
                        new_ball.vy = ball.vy
                        self.balls.append(new_ball)
                        pygame.event.post(
                            pygame.event.Event(
                                pygame.USEREVENT, {"event": PowerUpCollectedEvent()}
                            )
                        )
                    elif effect == getattr(self.block_manager, "TYPE_MULTIBALL", None):
                        for _ in range(2):
                            new_ball = Ball(
                                ball.x, ball.y, ball.radius, (255, 255, 255)
                            )
                            speed = (ball.vx**2 + ball.vy**2) ** 0.5
                            new_ball.vx = speed * (ball.vx / speed) * 0.8
                            new_ball.vy = speed * (ball.vy / speed) * 0.8
                            self.balls.append(new_ball)
                        pygame.event.post(
                            pygame.event.Event(
                                pygame.USEREVENT, {"event": PowerUpCollectedEvent()}
                            )
                        )
                    elif effect == getattr(self.block_manager, "TYPE_BOMB", None):
                        pygame.event.post(
                            pygame.event.Event(
                                pygame.USEREVENT, {"event": BombExplodedEvent()}
                            )
                        )
                    elif effect in [
                        getattr(self.block_manager, "TYPE_PAD_EXPAND", None),
                        getattr(self.block_manager, "TYPE_PAD_SHRINK", None),
                    ]:
                        if effect == getattr(
                            self.block_manager, "TYPE_PAD_EXPAND", None
                        ):
                            self.paddle.width = int(
                                min(self.paddle.width * 1.5, self.paddle.width * 2)
                            )
                        else:
                            self.paddle.width = int(
                                max(self.paddle.width * 0.5, self.paddle.width / 2)
                            )
                        self.paddle.rect.width = self.paddle.width
                        pygame.event.post(
                            pygame.event.Event(
                                pygame.USEREVENT, {"event": PowerUpCollectedEvent()}
                            )
                        )
                    elif effect == getattr(self.block_manager, "TYPE_TIMER", None):
                        self.level_manager.add_time(20)
                        pygame.event.post(
                            pygame.event.Event(
                                pygame.USEREVENT, {"event": PowerUpCollectedEvent()}
                            )
                        )
                if hit_paddle:
                    pygame.event.post(
                        pygame.event.Event(
                            pygame.USEREVENT, {"event": PaddleHitEvent()}
                        )
                    )
                if hit_wall:
                    pygame.event.post(
                        pygame.event.Event(pygame.USEREVENT, {"event": WallHitEvent()})
                    )
                active_balls.append(ball)
            else:
                logger.debug(
                    f"Ball lost at position ({ball.x}, {ball.y}). Firing BallLostEvent."
                )
                pygame.event.post(
                    pygame.event.Event(pygame.USEREVENT, {"event": BallLostEvent()})
                )

        # Log the number of active balls
        logger.debug(f"Active balls after update: {len(active_balls)}")
        self.balls[:] = active_balls

    def handle_life_loss(self) -> None:
        """
        Handle the loss of a life, update game state, and post relevant events.
        """
        logger.debug(
            f"handle_life_loss called. Current lives: {self.game_state.lives}, Balls in play: {len(self.balls)}"
        )

        if self.game_state.is_game_over():
            logger.debug("Game is already over, ignoring life loss.")
            return  # Prevent further life loss after game over

        # Always show "Balls Terminated!" message a ball / life is lost
        self.level_manager.stop_timer()
        changes = self.game_state.lose_life()
        self.post_game_state_events(changes)
        logger.debug(f"Life lost. Remaining lives: {self.game_state.lives}")
        pygame.event.post(
            pygame.event.Event(
                pygame.USEREVENT,
                {
                    "event": MessageChangedEvent(
                        "Balls Terminated!", color=(0, 255, 0), alignment="left"
                    )
                },
            )
        )

        # If lives remain, add a new ball regardless of other balls in play
        if self.game_state.lives > 0:
            logger.debug(f"Lives remain ({self.game_state.lives}), adding a new ball.")
            new_ball = self.create_new_ball()
            logger.debug(
                f"New ball created at position ({new_ball.x}, {new_ball.y}), stuck_to_paddle: {new_ball.stuck_to_paddle}"
            )
            self.balls.append(new_ball)
            logger.debug(f"Total balls after adding new ball: {len(self.balls)}")
            self.waiting_for_launch = True
            logger.debug(f"waiting_for_launch set to {self.waiting_for_launch}")
        # If no lives remain, set game over
        else:
            logger.debug("No lives remain, setting game over.")
            changes = self.game_state.set_game_over(True)
            self.post_game_state_events(changes)

    def check_level_complete(self) -> None:
        """
        Check if the level is complete and fire events if so.
        """
        level_complete = self.level_manager.is_level_complete()
        if level_complete and not self.level_complete:
            logger.info(
                "Level complete detected in GameController. Firing ApplauseEvent and LevelCompleteEvent."
            )
            self.level_complete = True
            pygame.event.post(
                pygame.event.Event(pygame.USEREVENT, {"event": ApplauseEvent()})
            )
            pygame.event.post(
                pygame.event.Event(pygame.USEREVENT, {"event": LevelCompleteEvent()})
            )

    def handle_debug_x_key(self) -> None:
        """
        Handle the debug 'x' key to break all breakable blocks and advance the level.
        """
        if not self.input_manager:
            return
        if self.input_manager.is_key_down(pygame.K_x):
            if not self.game_state.is_game_over() and not self.level_complete:
                broken_count = 0
                for block in self.block_manager.blocks:
                    if (
                        getattr(block, "type", None) != 2
                        and getattr(block, "health", 0) > 0
                    ):  # Skip unbreakable
                        block.hit()
                        if getattr(block, "health", 0) == 0:
                            broken_count += 1
                logger.info(
                    f"DEBUG: X key cheat used, broke {broken_count} blocks and triggered level complete."
                )
                self.level_complete = True
                pygame.event.post(
                    pygame.event.Event(pygame.USEREVENT, {"event": BombExplodedEvent()})
                )
                pygame.event.post(
                    pygame.event.Event(
                        pygame.USEREVENT, {"event": LevelCompleteEvent()}
                    )
                )

    def create_new_ball(self) -> Ball:
        """
        Create a new ball stuck to the paddle, using the controller's paddle and BALL_RADIUS.

        Returns:
            Ball: The newly created Ball object.
        """
        logger.debug(
            f"Creating new ball at paddle position: ({self.paddle.rect.centerx}, {self.paddle.rect.top - self.BALL_RADIUS - 1})"
        )
        ball = Ball(
            self.paddle.rect.centerx,
            self.paddle.rect.top - self.BALL_RADIUS - 1,
            self.BALL_RADIUS,
            (255, 255, 255),
        )
        ball.stuck_to_paddle = True
        ball.paddle_offset = 0
        ball.birth_animation = True
        ball.animation_frame = 0
        ball.frame_counter = 0
        logger.debug(
            f"New ball created with properties: stuck_to_paddle={ball.stuck_to_paddle}, paddle_offset={ball.paddle_offset}, birth_animation={ball.birth_animation}"
        )
        return ball

    def handle_event(self, event: Any) -> None:
        """
        Handle a single event (protocol stub for future use).

        Args:
            event: A single event object (type may vary).
        """
        if isinstance(event, BallLostEvent):
            logger.debug("BallLostEvent detected in GameController via handle_event.")
            self.handle_life_loss()
        # Add more event handling as needed

    def post_game_state_events(self, changes: List[Any]) -> None:
        """
        Post all events returned by GameState/model methods to the Pygame event queue.
        This implements the decoupled event firing pattern: models return events, controllers post them.

        Args:
            changes: List of event objects to post to the Pygame event queue.
        """
        for event in changes:
            pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"event": event}))

    def restart_game(self) -> None:
        """
        Restart the game state and post relevant events.
        """
        changes = self.game_state.restart()
        self.post_game_state_events(changes)

    def full_restart_game(self) -> None:
        """
        Fully restart the game state and post relevant events.
        """
        changes = self.game_state.full_restart(self.level_manager)
        self.post_game_state_events(changes)
