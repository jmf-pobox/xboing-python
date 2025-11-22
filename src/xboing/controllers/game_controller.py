"""Controller for game play logic, state updates, and event handling in
XBoing.
"""

import logging
from typing import Any, List

import pygame

from xboing.controllers.controller import Controller
from xboing.controllers.game_input_controller import GameInputController
from xboing.controllers.paddle_input_controller import PaddleInputController
from xboing.engine.events import (
    BallLostEvent,
    SpecialReverseChangedEvent,
    SpecialStickyChangedEvent,
)
from xboing.engine.graphics import Renderer
from xboing.engine.input import InputManager
from xboing.game.ball import BALL_RADIUS, Ball
from xboing.game.ball_manager import BallManager
from xboing.game.block_manager import BlockManager
from xboing.game.bullet_manager import BulletManager
from xboing.game.collision import CollisionSystem, CollisionType
from xboing.game.collision_handlers import CollisionHandlers
from xboing.game.game_state import GameState
from xboing.game.game_state_manager import GameStateManager
from xboing.game.level_manager import LevelManager
from xboing.game.paddle import Paddle
from xboing.game.power_up_manager import PowerUpManager
from xboing.layout.game_layout import GameLayout

logger = logging.getLogger(__name__)


class GameController(Controller):
    """Handles gameplay input, updates, and transitions for the GameView.

    Handles paddle, ball, block, and debug logic.

    **Event decoupling pattern**
    GameState and other model methods do not post events directly. Instead, they return a list of event instances
    representing state changes. GameController is responsible for posting these events to the Pygame event queue
    using the post_game_state_events helper. This enables headless testing and decouples model logic from the event system.
    """

    def __init__(
        self,
        game_state: GameState,
        level_manager: LevelManager,
        ball_manager: BallManager,
        paddle: Paddle,
        block_manager: BlockManager,
        input_manager: InputManager,
        layout: GameLayout,
        renderer: Renderer,
        bullet_manager: BulletManager,
    ) -> None:
        """Initialize the GameController.

        Args:
        ----
            game_state: The main GameState instance.
            level_manager: The LevelManager instance.
            ball_manager: The BallManager instance for managing balls.
            paddle: The Paddle instance.
            block_manager: The BlockManager instance.
            input_manager: The InputManager instance.
            layout: The GameLayout instance.
            renderer: The Renderer instance.
            bullet_manager: The BulletManager instance for managing bullets.

        """
        self.game_state: GameState = game_state
        self.level_manager: LevelManager = level_manager
        self.ball_manager: BallManager = ball_manager
        self.paddle: Paddle = paddle
        self.block_manager: BlockManager = block_manager
        self.layout: GameLayout = layout
        self.renderer: Renderer = renderer
        self.bullet_manager: BulletManager = bullet_manager
        self.logger = logging.getLogger("xboing.GameController")

        # Create input controllers
        self.paddle_input = PaddleInputController(paddle, input_manager, layout)
        self.game_input = GameInputController(
            game_state,
            level_manager,
            ball_manager,
            paddle,
            block_manager,
            bullet_manager,
            input_manager,
            layout,
        )

        # Create game state manager
        self.game_state_manager = GameStateManager(game_state, level_manager)

        # Create power-up manager
        self.power_up_manager = PowerUpManager(game_state, paddle)

        # Create collision system
        self.collision_system = CollisionSystem()
        self.collision_handlers = CollisionHandlers(
            game_state,
            paddle,
            ball_manager,
            bullet_manager,
            self.power_up_manager,
            block_manager,
        )
        self._register_collision_handlers()

    def _register_collision_handlers(self) -> None:
        """Register all collision handlers for the game."""
        self.collision_system.register_collision_handler(
            CollisionType.BALL.value,
            CollisionType.BLOCK.value,
            self.collision_handlers.handle_ball_block_collision,
        )
        self.collision_system.register_collision_handler(
            CollisionType.BALL.value,
            CollisionType.PADDLE.value,
            self.collision_handlers.handle_ball_paddle_collision,
        )
        self.collision_system.register_collision_handler(
            CollisionType.BULLET.value,
            CollisionType.BLOCK.value,
            self.collision_handlers.handle_bullet_block_collision,
        )
        self.collision_system.register_collision_handler(
            CollisionType.BULLET.value,
            CollisionType.BALL.value,
            self.collision_handlers.handle_bullet_ball_collision,
        )

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        """Handle Pygame events for gameplay, including launching balls and handling BallLostEvent.

        Args:
        ----
            events: List of Pygame events to process.

        """
        # Check for game events
        for event in events:
            if event.type == pygame.USEREVENT:
                if isinstance(event.event, BallLostEvent):
                    logger.debug("BallLostEvent detected in GameController.")
                    self.handle_life_loss()
                elif isinstance(event.event, SpecialReverseChangedEvent):
                    # Sync paddle input controller when reverse changes via block collision
                    self.paddle_input.set_reverse(event.event.active)

        # Delegate event handling to the game input controller
        events_to_post = self.game_input.handle_events(events)

        # Post events returned by the game input controller
        for event in events_to_post:
            pygame.event.post(event)

    def update(self, delta_ms: float) -> None:
        """Update gameplay logic.

        Args:
        ----
            delta_ms: Time elapsed since the last update in milliseconds.

        """
        # Check if game is paused
        if self.game_input.is_paused():
            return

        # Update paddle position based on input
        self.paddle_input.update(delta_ms)

        # Update game objects
        self.update_blocks_and_timer(delta_ms)
        self.update_balls_and_collisions(delta_ms)
        self.bullet_manager.update(delta_ms)
        self.check_level_complete()

        # Handle debug keys
        debug_events = self.game_input.handle_debug_keys()
        for event in debug_events:
            pygame.event.post(event)

        # Update stuck ball timer
        stuck_ball_events = self.game_input.update_stuck_ball_timer(delta_ms)
        for event in stuck_ball_events:
            pygame.event.post(event)

    def update_blocks_and_timer(self, delta_ms: float) -> None:
        """Update blocks and timer if appropriate.

        Args:
        ----
            delta_ms: Time elapsed since the last update in milliseconds.

        """
        # Update blocks
        self.block_manager.update(delta_ms)

        # Delegate timer management to GameStateManager
        is_active = (
            not self.game_state.is_game_over()
            and not self.game_state.level_state.is_level_complete()
        )
        events = self.game_state_manager.update_timer(delta_ms, is_active)

        # Post events returned by GameStateManager
        self.post_game_state_events(events)

    def update_balls_and_collisions(self, delta_ms: float) -> None:
        """Update balls and bullets, check for collisions, and handle block effects using CollisionSystem."""
        logger.debug("Starting update_balls_and_collisions")
        # Update balls
        play_rect = self.layout.get_play_rect()
        logger.debug(f"Got play_rect: {play_rect}")
        balls_to_remove: List[Any] = []  # Track balls that need to be removed
        logger.debug(f"Number of balls to process: {len(self.ball_manager.balls)}")

        for ball in self.ball_manager.balls:
            logger.debug(f"Processing ball: {ball}")
            logger.debug("About to call ball.update")
            events = ball.update(
                delta_ms,
                play_rect.width,
                play_rect.height,
                self.paddle,
                play_rect.x,
                play_rect.y,
            )
            logger.debug(f"Ball update returned events: {events}")

            # Handle events returned from ball update
            for event in events:
                logger.debug(f"Processing event: {event}")
                pygame.event.post(
                    pygame.event.Event(pygame.USEREVENT, {"event": event})
                )
                # Mark ball for removal if it's lost, but don't handle life loss here
                if isinstance(event, BallLostEvent):
                    logger.debug("BallLostEvent detected")
                    balls_to_remove.append(ball)  # Mark ball for removal
                    break

        logger.debug("Removing marked balls")
        # Remove marked balls
        for ball in balls_to_remove:
            if ball in self.ball_manager.balls:  # Check if ball is still in the list
                self.ball_manager.remove_ball(ball)

        logger.debug("Updating bullets")
        # Update bullets
        self.bullet_manager.update(delta_ms)

        logger.debug("Registering collidables")
        # Register all collidables and check collisions
        self._register_all_collidables()
        logger.debug("Checking collisions")
        self.collision_system.check_collisions()

        logger.debug("Removing inactive objects")
        # Remove inactive balls and bullets
        self.ball_manager.remove_inactive_balls()
        for bullet in list(self.bullet_manager.bullets):
            if not bullet.is_active():
                self.bullet_manager.remove_bullet(bullet)

        logger.debug("Finished update_balls_and_collisions")

    def handle_life_loss(self) -> None:
        """Handle the loss of a life, update game state, and post relevant events."""
        logger.debug(
            f"handle_life_loss called. Current lives: {self.game_state.lives}, "
            f"Balls in play: {len(self.ball_manager.balls)}, "
            f"Active balls: {self.ball_manager.number_of_active_balls()}"
        )

        # Always disable sticky on life loss
        self.disable_sticky()

        # Delegate life loss logic to GameStateManager
        has_active_balls = self.ball_manager.active_ball()
        events = self.game_state_manager.handle_life_loss(has_active_balls)

        # Post events returned by GameStateManager
        self.post_game_state_events(events)

        # Create a new ball if we still have lives and no balls remain
        if not self.game_state.is_game_over() and not has_active_balls:
            new_ball = self.create_new_ball()
            self.ball_manager.add_ball(new_ball)
            logger.debug("Created new ball after life loss")

    def check_level_complete(self) -> None:
        """Check if the level is complete and handle level completion."""
        # Delegate level completion check to GameStateManager
        blocks_remaining = len(self.block_manager.blocks)
        events = self.game_state_manager.check_level_complete(blocks_remaining)

        # Post events returned by GameStateManager
        self.post_game_state_events(events)

    def create_new_ball(self) -> Ball:
        """Create a new ball at the paddle position.

        Returns
        -------
            A new Ball instance.

        """
        ball = Ball(
            x=self.paddle.rect.centerx,
            y=self.paddle.rect.top - BALL_RADIUS,
            radius=BALL_RADIUS,
        )
        # Stick the ball to the paddle
        ball.stuck_to_paddle = True
        ball.paddle_offset = 0.0
        return ball

    def handle_event(self, event: Any) -> None:
        """Handle a single event.

        Args:
        ----
            event: The event to handle.

        """
        if isinstance(event, BallLostEvent):
            self.handle_life_loss()

    @staticmethod
    def post_game_state_events(changes: List[Any]) -> None:
        """Post all events returned by GameState/model methods to the Pygame event queue.

        This implements the decoupled event firing pattern: models return events, controllers post them.

        Args:
        ----
            changes: List of event objects to post to the Pygame event queue.

        """
        for event in changes:
            pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"event": event}))

    def full_restart_game(self) -> None:
        """Perform a full game restart."""
        changes = self.game_state.full_restart(self.level_manager)
        self.post_game_state_events(changes)

    def toggle_reverse(self) -> None:
        """Toggle the reverse paddle control state."""
        new_value = not self.power_up_manager.is_reverse_active()
        self.power_up_manager.set_reverse(new_value)
        self.paddle_input.set_reverse(new_value)

    def set_reverse(self, value: bool) -> None:
        """Set the reverse paddle control state.

        Args:
            value: The new reverse state.

        """
        self.power_up_manager.set_reverse(value)
        self.paddle_input.set_reverse(value)

    def enable_sticky(self) -> None:
        """Enable sticky paddle mode."""
        self.power_up_manager.set_sticky(True)
        pygame.event.post(
            pygame.event.Event(
                pygame.USEREVENT, {"event": SpecialStickyChangedEvent(active=True)}
            )
        )

    def disable_sticky(self) -> None:
        """Disable sticky paddle mode."""
        if self.power_up_manager.is_sticky_active():
            self.power_up_manager.set_sticky(False)
            pygame.event.post(
                pygame.event.Event(
                    pygame.USEREVENT, {"event": SpecialStickyChangedEvent(active=False)}
                )
            )

    def on_new_level_loaded(self) -> None:
        """Handle new level loaded event."""
        self.disable_sticky()
        self.set_reverse(False)  # This already calls paddle_input.set_reverse(False)

    def _register_all_collidables(self) -> None:
        """Register all collidable objects with the collision system."""
        self.collision_system.clear()  # Clear existing collidables
        self.collision_system.add_collidable(self.paddle)
        for ball in self.ball_manager.balls:
            self.collision_system.add_collidable(ball)
        for block in self.block_manager.blocks:
            self.collision_system.add_collidable(block)
        for bullet in self.bullet_manager.bullets:
            self.collision_system.add_collidable(bullet)
