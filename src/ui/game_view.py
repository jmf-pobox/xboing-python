import pygame

from .content_view import ContentView


class GameView(ContentView):
    def __init__(self, layout, block_manager, paddle, balls, renderer):
        self.layout = layout
        self.block_manager = block_manager
        self.paddle = paddle
        self.balls = balls
        self.renderer = renderer

    def draw(self, surface):
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

    def handle_event(self, event):
        pass  # GameView may handle events in the future

    def activate(self):
        pass

    def deactivate(self):
        pass 