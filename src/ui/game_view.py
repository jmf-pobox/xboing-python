"""
GameView: Main gameplay content view for XBoing.
Handles rendering of blocks, paddle, balls, and play area walls.
"""

from typing import List

import pygame

from engine.graphics import Renderer
from game.ball import Ball
from game.paddle import Paddle
from game.sprite_block import SpriteBlockManager
from layout.game_layout import GameLayout

from .view import View


class GameView(View):
    """
    Main gameplay content view.
    Renders blocks, paddle, balls, and play area walls.
    """

    def __init__(
        self,
        layout: GameLayout,
        block_manager: SpriteBlockManager,
        paddle: Paddle,
        balls: List[Ball],
        renderer: Renderer,
    ) -> None:
        """
        Initialize the GameView.

        Args:
            layout (GameLayout): The GameLayout instance.
            block_manager (SpriteBlockManager): The block manager for the current level.
            paddle (Paddle): The player paddle object.
            balls (List[Ball]): List of active ball objects.
            renderer (Renderer): The main renderer instance.
        """
        self.layout: GameLayout = layout
        self.block_manager: SpriteBlockManager = block_manager
        self.paddle: Paddle = paddle
        self.balls: List[Ball] = balls
        self.renderer: Renderer = renderer

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the blocks, paddle, balls, and play area walls.

        Args:
            surface (pygame.Surface): The Pygame surface to draw on.
        """
        # Draw the blocks
        self.block_manager.draw(surface)

        # Draw the paddle
        self.paddle.draw(surface)

        # Draw all balls
        for ball in self.balls:
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

    def handle_event(self, event: pygame.event.Event) -> None:
        """
        Handle a single Pygame event (currently a stub).

        Args:
            event (pygame.event.Event): The Pygame event to handle.
        """
        pass  # GameView may handle events in the future

    def activate(self) -> None:
        """
        Activate the view (currently a stub).
        """
        pass

    def deactivate(self) -> None:
        """
        Deactivate the view (currently a stub).
        """
        pass
