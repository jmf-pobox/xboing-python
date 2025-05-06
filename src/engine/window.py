"""
Window management abstraction over SDL2/pygame.

This module provides window creation, management, and event handling,
abstracting the underlying SDL2/pygame implementation.
"""

import pygame


class Window:
    """Window management for the game, abstracting pygame's display system."""

    def __init__(
        self, width, height, title="- XBoing II -", fullscreen=False, resizable=False
    ):
        """
        Initialize the game window.

        Args:
            width (int): Window width in pixels
            height (int): Window height in pixels
            title (str): Window title
            fullscreen (bool): Whether to start in fullscreen mode
            resizable (bool): Whether the window is resizable
        """
        pygame.init()

        # Set up display flags
        flags = 0
        if fullscreen:
            flags |= pygame.FULLSCREEN
        if resizable:
            flags |= pygame.RESIZABLE

        # Create the window
        self.surface = pygame.display.set_mode((width, height), flags)
        pygame.display.set_caption(title)

        # Store window properties
        self.width = width
        self.height = height
        self.fullscreen = fullscreen
        self.running = True

        # Initialize clock for framerate management
        self.clock = pygame.time.Clock()
        self.target_fps = 60

    def set_icon(self, icon_surface):
        """Set the window icon."""
        pygame.display.set_icon(icon_surface)

    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode."""
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.surface = pygame.display.set_mode(
                (self.width, self.height), pygame.FULLSCREEN
            )
        else:
            self.surface = pygame.display.set_mode((self.width, self.height))

    def clear(self, color=(0, 0, 0)):
        """Clear the window with the specified color."""
        self.surface.fill(color)

    def update(self):
        """Update the display and control framerate."""
        pygame.display.flip()
        self.clock.tick(self.target_fps)

    def set_fps(self, fps):
        """Set the target framerate."""
        self.target_fps = fps

    def get_fps(self):
        """Get the current framerate."""
        return self.clock.get_fps()

    def handle_events(self, events=None):
        """
        Process window events.

        Returns:
            bool: False if the window should close, True otherwise
        """
        if events is None:
            events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_F11:
                    self.toggle_fullscreen()

        return self.running

    def cleanup(self):
        """Clean up resources and shut down pygame."""
        pygame.quit()
