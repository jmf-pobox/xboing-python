"""Controller for main game logic, state updates, and event handling in XBoing."""

import logging
from typing import Any, List, Optional, Sequence

import pygame

from xboing.controllers.controller import Controller
from xboing.engine.events import (
    AmmoFiredEvent,
    ApplauseEvent,
    BallLostEvent,
    BallShotEvent,
    BlockHitEvent,
    BombExplodedEvent,
    LevelCompleteEvent,
    MessageChangedEvent,
    PaddleGrowEvent,
    PaddleHitEvent,
    PaddleShrinkEvent,
    PowerUpCollectedEvent,
    SpecialReverseChangedEvent,
    SpecialStickyChangedEvent,
    WallHitEvent,
    post_level_title_message,
)
from xboing.engine.graphics import Renderer
from xboing.engine.input import InputManager
from xboing.game.ball import Ball
from xboing.game.ball_manager import BallManager
from xboing.game.block_manager import BlockManager
from xboing.game.block_types import (
    BOMB_BLK,
    BULLET_BLK,
    EXTRABALL_BLK,
    MAXAMMO_BLK,
    MULTIBALL_BLK,
    PAD_EXPAND_BLK,
    PAD_SHRINK_BLK,
    REVERSE_BLK,
    SPECIAL_BLOCK_TYPES,
    STICKY_BLK,
    TIMER_BLK,
)
from xboing.game.bullet import Bullet
from xboing.game.bullet_manager import BulletManager
from xboing.game.game_state import GameState
from xboing.game.level_manager import LevelManager
from xboing.game.paddle import Paddle
from xboing.layout.game_layout import GameLayout

logger = logging.getLogger(__name__)


class GameController(Controller):
    """Handles gameplay input, updates, and transitions for the GameView.

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
        self.input_manager: InputManager = input_manager
        self.layout: GameLayout = layout
        self.renderer: Renderer = renderer
        self.level_complete: bool = False
        self._last_mouse_x: Optional[int] = None
        self.reverse: bool = False  # Reverse paddle control state
        self.sticky: bool = False  # Sticky paddle state
        self.bullet_manager: BulletManager = bullet_manager

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        """Handle Pygame events for gameplay, including launching balls and handling BallLostEvent.

        Args:
        ----
            events: List of Pygame events to process.

        """
        for event in events:
            logger.debug(f"[handle_events] Event received: {event}")
            # --- Section: Ammo Fired or Ball Launch (K key or mouse button) ---
            is_k_key = event.type == pygame.KEYDOWN and event.key == pygame.K_k
            is_mouse_button = event.type == pygame.MOUSEBUTTONDOWN  # Mouse button event
            if is_k_key or is_mouse_button:
                if self.ball_manager.has_ball_in_play():
                    # Fire ammo
                    logger.debug(
                        f"About to fire ammo via game_state: {self.game_state}"
                    )
                    changes = self.game_state.fire_ammo()
                    for change in changes:
                        pygame.event.post(
                            pygame.event.Event(pygame.USEREVENT, {"event": change})
                        )
                        if isinstance(change, AmmoFiredEvent):
                            x, _ = self.paddle.get_center()
                            play_rect = self.layout.get_play_rect()
                            bullet_radius = 4
                            y = self.paddle.rect.top - bullet_radius - 1
                            logger.warning(f"Firing bullet at y={y}")
                            logger.warning(
                                f"Playfield: {play_rect}, Paddle: {self.paddle.rect}"
                            )
                            bullet = Bullet(x, y, vy=-10.0, radius=bullet_radius)
                            self.bullet_manager.add_bullet(bullet)
                else:
                    # Launch ball(s)
                    balls = self.ball_manager.balls
                    logger.debug("[handle_events] launching ball(s)")
                    for ball in balls:
                        ball.release_from_paddle()
                    changes = self.game_state.set_timer(
                        self.level_manager.get_time_remaining()
                    )
                    self.post_game_state_events(changes)
                    self.level_manager.start_timer()
                    pygame.event.post(
                        pygame.event.Event(pygame.USEREVENT, {"event": BallShotEvent()})
                    )
                    level_info = self.level_manager.get_level_info()
                    level_title = str(level_info["title"])
                    post_level_title_message(level_title)
                    logger.debug("Ball(s) launched and timer started.")

            # --- Section: BallLostEvent Handling ---
            if event.type == pygame.USEREVENT and isinstance(
                event.event, BallLostEvent
            ):
                logger.debug("BallLostEvent detected in GameController.")
                self.handle_life_loss()

    def update(self, delta_ms: float) -> None:
        """Update gameplay logic.

        Args:
        ----
            delta_ms: Time elapsed since last update in milliseconds.

        """
        self.handle_paddle_arrow_key_movement(delta_ms)
        self.handle_paddle_mouse_movement()
        self.update_blocks_and_timer(delta_ms)
        self.update_balls_and_collisions(delta_ms)
        self.bullet_manager.update(delta_ms)
        self.check_level_complete()
        self.handle_debug_x_key()

    def handle_paddle_arrow_key_movement(self, delta_ms: float) -> None:
        """Handle paddle movement and input (arrow keys and j/k/l keys).

        Args:
        ----
            delta_ms: Time elapsed since last update in milliseconds.

        """
        paddle_direction = 0
        # Support both arrow keys and j/l keys for left/right
        left_keys = [pygame.K_LEFT, pygame.K_j]
        right_keys = [pygame.K_RIGHT, pygame.K_l]
        left_pressed = [k for k in left_keys if self.input_manager.is_key_pressed(k)]
        right_pressed = [k for k in right_keys if self.input_manager.is_key_pressed(k)]
        if self.reverse:
            if left_pressed:
                paddle_direction = 1
            elif right_pressed:
                paddle_direction = -1
        elif left_pressed:
            paddle_direction = -1
        elif right_pressed:
            paddle_direction = 1
        play_rect = self.layout.get_play_rect()
        if play_rect:
            self.paddle.set_direction(paddle_direction)
            self.paddle.update(delta_ms, play_rect.width, play_rect.x)
        else:
            self.paddle.set_direction(0)

    def handle_paddle_mouse_movement(self) -> None:
        """Handle mouse-based paddle movement, but only if the mouse has moved."""
        play_rect = self.layout.get_play_rect()
        mouse_pos = self.input_manager.get_mouse_position()
        mouse_x = mouse_pos[0]
        if self._last_mouse_x is not None and self._last_mouse_x != mouse_x:
            if self.reverse:
                center_x = play_rect.x + play_rect.width // 2
                mirrored_x = 2 * center_x - mouse_x
                local_x = mirrored_x - play_rect.x - self.paddle.width // 2
            else:
                local_x = mouse_x - play_rect.x - self.paddle.width // 2
            self.paddle.move_to(local_x, play_rect.width, play_rect.x)
        self._last_mouse_x = mouse_x

    def update_blocks_and_timer(self, delta_ms: float) -> None:
        """Update blocks and timer if appropriate.

        Args:
        ----
            delta_ms: Time elapsed since last update in milliseconds.

        """
        self.block_manager.update(delta_ms)
        if not self.game_state.is_game_over() and not self.level_complete:
            self.level_manager.update(delta_ms)
            changes = self.game_state.set_timer(self.level_manager.get_time_remaining())
            self.post_game_state_events(changes)

    def _handle_block_effects(
        self, effects: Sequence[str], ball: Optional[Ball] = None
    ) -> None:
        """Handle special block effects for both balls and bullets."""
        logger.debug(f"Handling block effects: len = {len(effects)}")
        for effect in effects:
            logger.debug(f"Handling block effect: {effect}")
            if effect == BULLET_BLK:
                logger.debug("Bulletblock hit: adding ammo.")
                changes = self.game_state.add_ammo()
                self.post_game_state_events(changes)
            elif effect == MAXAMMO_BLK:
                logger.debug("Max ammo block hit: adding ammo.")
                changes = self.game_state.add_ammo()
                self.post_game_state_events(changes)
            elif effect == EXTRABALL_BLK and ball is not None:
                new_ball = Ball(ball.x, ball.y, ball.radius, (255, 255, 255))
                new_ball.vx = -ball.vx
                new_ball.vy = ball.vy
                self.ball_manager.add_ball(new_ball)
                pygame.event.post(
                    pygame.event.Event(
                        pygame.USEREVENT, {"event": PowerUpCollectedEvent()}
                    )
                )
            elif effect == MULTIBALL_BLK and ball is not None:
                for _ in range(2):
                    new_ball = Ball(ball.x, ball.y, ball.radius, (255, 255, 255))
                    speed = (ball.vx**2 + ball.vy**2) ** 0.5
                    new_ball.vx = speed * (ball.vx / speed) * 0.8
                    new_ball.vy = speed * (ball.vy / speed) * 0.8
                    self.ball_manager.add_ball(new_ball)
                pygame.event.post(
                    pygame.event.Event(
                        pygame.USEREVENT, {"event": PowerUpCollectedEvent()}
                    )
                )
            elif effect == BOMB_BLK:
                pygame.event.post(
                    pygame.event.Event(pygame.USEREVENT, {"event": BombExplodedEvent()})
                )
            elif effect == PAD_EXPAND_BLK:
                old_size = self.paddle.size
                if old_size < Paddle.SIZE_LARGE:
                    self.paddle.set_size(old_size + 1)
                    at_max = self.paddle.size == Paddle.SIZE_LARGE
                    logger.debug(
                        f"Paddle expanded to size {self.paddle.size} (width={self.paddle.width})"
                    )
                    pygame.event.post(
                        pygame.event.Event(
                            pygame.USEREVENT,
                            {
                                "event": PaddleGrowEvent(
                                    self.paddle.width, at_max=at_max
                                )
                            },
                        )
                    )
                else:
                    logger.debug(
                        "Paddle already at maximum size; cannot expand further."
                    )
                    pygame.event.post(
                        pygame.event.Event(
                            pygame.USEREVENT,
                            {"event": PaddleGrowEvent(self.paddle.width, at_max=True)},
                        )
                    )
            elif effect == PAD_SHRINK_BLK:
                old_size = self.paddle.size
                if old_size > Paddle.SIZE_SMALL:
                    self.paddle.set_size(old_size - 1)
                    at_min = self.paddle.size == Paddle.SIZE_SMALL
                    logger.debug(
                        f"Paddle shrunk to size {self.paddle.size} (width={self.paddle.width})"
                    )
                    pygame.event.post(
                        pygame.event.Event(
                            pygame.USEREVENT,
                            {
                                "event": PaddleShrinkEvent(
                                    self.paddle.width, at_min=at_min
                                )
                            },
                        )
                    )
                else:
                    logger.debug(
                        "Paddle already at minimum size; cannot shrink further."
                    )
                    pygame.event.post(
                        pygame.event.Event(
                            pygame.USEREVENT,
                            {
                                "event": PaddleShrinkEvent(
                                    self.paddle.width, at_min=True
                                )
                            },
                        )
                    )
            elif effect == TIMER_BLK:
                self.level_manager.add_time(20)
                pygame.event.post(
                    pygame.event.Event(
                        pygame.USEREVENT, {"event": PowerUpCollectedEvent()}
                    )
                )
            elif effect == REVERSE_BLK:
                self.toggle_reverse()
                pygame.event.post(
                    pygame.event.Event(
                        pygame.USEREVENT,
                        {"event": SpecialReverseChangedEvent(self.reverse)},
                    )
                )
            elif effect == STICKY_BLK:
                logger.debug("Sticky block hit: enabling sticky paddle mode.")
                self.enable_sticky()

    def update_balls_and_collisions(self, delta_ms: float) -> None:
        """Update balls and bullets, check for collisions, and handle block effects."""
        active_balls = []
        # --- Bullet-block collision detection ---
        active_bullets = []
        for bullet in self.bullet_manager.bullets:
            points, broken, effects = self.block_manager.check_collisions(bullet)
            if points != 0:
                changes = self.game_state.add_score(points)
                self.post_game_state_events(changes)
            if broken > 0 and not any(
                effect in SPECIAL_BLOCK_TYPES for effect in effects
            ):
                pygame.event.post(
                    pygame.event.Event(pygame.USEREVENT, {"event": BlockHitEvent()})
                )
            elif broken > 0:
                self._handle_block_effects(effects)

            if bullet.active:
                active_bullets.append(bullet)
            else:
                self.bullet_manager.remove_bullet(bullet)

        # --- Ball-block collision detection ---
        for ball in self.ball_manager.balls:
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
                if broken > 0 and not any(
                    effect in SPECIAL_BLOCK_TYPES for effect in effects
                ):
                    pygame.event.post(
                        pygame.event.Event(pygame.USEREVENT, {"event": BlockHitEvent()})
                    )
                self._handle_block_effects(effects, ball=ball)
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
        self.ball_manager.remove_inactive_balls()

    def handle_life_loss(self) -> None:
        """Handle the loss of a life, update game state, and post relevant events."""
        logger.debug(
            f"handle_life_loss called. Current lives: {self.game_state.lives}, Balls in play: {len(self.ball_manager.balls)}"
        )

        # Always disable sticky on life loss
        self.disable_sticky()

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
            self.ball_manager.add_ball(new_ball)
            logger.debug(
                f"Total balls after adding new ball: {len(self.ball_manager.balls)}"
            )
        # If no lives remain, set game over
        else:
            logger.debug("No lives remain, setting game over.")
            changes = self.game_state.set_game_over(True)
            self.post_game_state_events(changes)

    def check_level_complete(self) -> None:
        """Check if the level is complete and fire events if so."""
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
        """Handle the debug 'x' key to break all breakable blocks and advance the level."""
        if (
            self.input_manager
            and self.input_manager.is_key_down(pygame.K_x)
            and not self.game_state.is_game_over()
            and not self.level_complete
        ):
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
                pygame.event.Event(pygame.USEREVENT, {"event": LevelCompleteEvent()})
            )

    def create_new_ball(self) -> Ball:
        """Create a new ball stuck to the paddle, using the controller's paddle and BALL_RADIUS.

        Returns
        -------
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
        """Handle a single event (protocol stub for future use).

        Args:
        ----
            event: A single event object (type may vary).

        """
        if isinstance(event, BallLostEvent):
            logger.debug("BallLostEvent detected in GameController via handle_event.")
            self.handle_life_loss()
        # Add more event handling as needed

    def post_game_state_events(self, changes: List[Any]) -> None:
        """Post all events returned by GameState/model methods to the Pygame event queue.

        This implements the decoupled event firing pattern: models return events, controllers post them.

        Args:
        ----
            changes: List of event objects to post to the Pygame event queue.

        """
        for event in changes:
            pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"event": event}))

    def full_restart_game(self) -> None:
        """Fully restart the game state and post relevant events."""
        changes = self.game_state.full_restart(self.level_manager)
        self.post_game_state_events(changes)

    def toggle_reverse(self) -> None:
        """Toggle the reverse paddle control state."""
        self.reverse = not self.reverse

    def set_reverse(self, value: bool) -> None:
        """Set the reverse paddle control state explicitly."""
        self.reverse = value

    def enable_sticky(self) -> None:
        """Enable sticky paddle and fire event."""
        self.sticky = True
        self.paddle.sticky = True
        pygame.event.post(
            pygame.event.Event(
                pygame.USEREVENT, {"event": SpecialStickyChangedEvent(True)}
            )
        )

    def disable_sticky(self) -> None:
        """Disable sticky paddle and fire event."""
        self.sticky = False
        self.paddle.sticky = False
        pygame.event.post(
            pygame.event.Event(
                pygame.USEREVENT, {"event": SpecialStickyChangedEvent(False)}
            )
        )

    def on_new_level_loaded(self) -> None:
        """Call this when a new level is loaded to reset sticky state."""
        self.disable_sticky()
