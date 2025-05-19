"""GameView: Main gameplay content view for XBoing.

Handles rendering of blocks, paddle, balls, and play area walls.
"""

import pygame

from xboing.engine.graphics import Renderer
from xboing.game.ball_manager import BallManager
from xboing.game.block_manager import BlockManager
from xboing.game.bullet_manager import BulletManager
from xboing.game.paddle import Paddle
from xboing.layout.game_layout import GameLayout
from xboing.renderers.bullet_renderer import BulletRenderer

from .view import View


class GameView(View):
    """Main gameplay content view.

    Renders blocks, paddle, balls, and play area walls.
    """

    def __init__(
        self,
        layout: GameLayout,
        block_manager: BlockManager,
        paddle: Paddle,
        ball_manager: BallManager,
        renderer: Renderer,
        bullet_manager: BulletManager,
        bullet_renderer: BulletRenderer,
    ) -> None:
        """Initialize the GameView.

        Args:
        ----
            layout (GameLayout): The GameLayout instance.
            block_manager (BlockManager): The block manager for the current level.
            paddle (Paddle): The player paddle object.
            ball_manager (BallManager): The BallManager instance managing all balls.
            renderer (Renderer): The main renderer instance.
            bullet_manager (BulletManager): The BulletManager instance managing all bullets.
            bullet_renderer (BulletRenderer): The BulletRenderer instance for rendering bullets.

        """
        self.layout: GameLayout = layout
        self.block_manager: BlockManager = block_manager
        self.paddle: Paddle = paddle
        self.ball_manager = ball_manager
        self.renderer: Renderer = renderer
        self.bullet_manager = bullet_manager
        self.bullet_renderer = bullet_renderer

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the blocks, paddle, balls, and play area walls.

        Args:
        ----
            surface (pygame.Surface): The Pygame surface to draw on.

        """
        # Draw the blocks
        self.block_manager.draw(surface)

        # Draw the paddle
        self.paddle.draw(surface)

        # Draw all balls
        for ball in self.ball_manager.balls:
            ball.draw(surface)

        # Draw the walls inside the play area
        play_rect = self.layout.get_play_rect()
        wall_color = (100, 100, 100)
        pygame.draw.rect(
            surface,
            wall_color,
            pygame.Rect(play_rect.x, play_rect.y, play_rect.width, 2),
        )  # Top
        pygame.draw.rect(
            surface,
            wall_color,
            pygame.Rect(play_rect.x, play_rect.y, 2, play_rect.height),
        )  # Left
        pygame.draw.rect(
            surface,
            wall_color,
            pygame.Rect(
                play_rect.x + play_rect.width - 2, play_rect.y, 2, play_rect.height
            ),
        )  # Right

        # Draw all bullets
        self.bullet_renderer.render(surface, self.bullet_manager)

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle a single Pygame event (currently a stub).

        Args:
        ----
            event (pygame.event.Event): The Pygame event to handle.

        """
        # No-op for now

    def activate(self) -> None:
        """Activate the view (currently a stub)."""
        # No-op for now

    def deactivate(self) -> None:
        """Deactivate the view (currently a stub)."""
        # No-op for now
