import os

import pygame
from utils.asset_loader import load_image
from utils.asset_paths import get_backgrounds_dir, get_images_dir

from .content_view import ContentView


class InstructionsView(ContentView):
    def __init__(self, layout, renderer, font, headline_font, text_font, amber_color=(255, 191, 63)):
        self.layout = layout
        self.renderer = renderer
        self.font = font
        self.headline_font = headline_font
        self.text_font = text_font
        self.amber_color = amber_color
        # Manually broken lines to match the original game's style
        self.lines = [
            # Paragraph 1 (3 lines)
            "XBoing is a blockout game where you use a paddle to bounce",
            "a proton ball around an arena full of nasties while keeping",
            "the ball from leaving the arena via the bottom rebound wall.",
            # Paragraph 2 (4 lines)
            "Each block has a point value associated with it. Some blocks",
            "may award you more points for hitting them a number of times.",
            "Some blocks may toggle extra time/points or even special effects",
            "such as no walls, machine gun, sticky paddle, reverse controls, etc.",
            # Paragraph 3 (2 lines)
            "Your paddle is equipped with special bullets that can disintegrate",
            "a block. You only have a limited supply of bullets so use them wisely.",
            # Paragraph 4 (4 lines)
            "The multiple ball block will give you an extra ball to play with in",
            "the arena. This ball will act like any other ball except that when",
            "it dies it will not force a new ball to start. You can shoot your",
            "own ball so watch out. The death symbol is not too healthy either.",
            # Paragraph 5 (2 lines)
            "Sometimes a special block may appear or be added to another block",
            "that will affect the gameplay if hit. They also disappear randomly.",
            # Paragraph 6 (1 line)
            "Please read the manual for more information on how to play."
        ]
        # Use asset loader utility and asset_paths to load mnbgrnd.png
        backgrounds_dir = get_backgrounds_dir()
        bg_path = os.path.join(backgrounds_dir, "mnbgrnd.png")
        self.bg_image = load_image(bg_path, alpha=False)
        
        # Load xboing.png logo from the main images directory
        images_dir = get_images_dir()
        logo_path = os.path.join(images_dir, "xboing.png")
        self.logo_image = load_image(logo_path, alpha=True)

    def draw(self, surface):
        play_rect = self.layout.get_play_rect()

        # Create a temporary surface for the play window
        play_surf = pygame.Surface((play_rect.width, play_rect.height))
        # Draw the mnbgrnd.png background, tiled, to play_surf
        if self.bg_image:
            img_w, img_h = self.bg_image.get_width(), self.bg_image.get_height()
            for y in range(0, play_rect.height, img_h):
                for x in range(0, play_rect.width, img_w):
                    play_surf.blit(self.bg_image, (x, y))
        else:
            # fallback: fill with dark color
            play_surf.fill((40, 40, 50))
        centerx = play_rect.width // 2

        # Draw XBoing logo image if available
        y = 20
        if self.logo_image:
            # Scale logo to fit nicely (max width 320, max height 100)
            max_logo_width = min(320, play_rect.width - 40)
            max_logo_height = 100
            logo_w, logo_h = self.logo_image.get_width(), self.logo_image.get_height()
            scale = min(max_logo_width / logo_w, max_logo_height / logo_h, 1.0)
            scaled_w, scaled_h = int(logo_w * scale), int(logo_h * scale)
            logo_surf = pygame.transform.smoothscale(self.logo_image, (scaled_w, scaled_h))
            logo_rect = logo_surf.get_rect(center=(centerx, y + scaled_h // 2))
            play_surf.blit(logo_surf, logo_rect)
            y = logo_rect.bottom + 10
        else:
            # fallback: text logo
            logo_font = self.headline_font
            logo_text = "XBoing"
            logo_surf = logo_font.render(logo_text, True, (255, 255, 255))
            logo_rect = logo_surf.get_rect(center=(centerx, 40))
            play_surf.blit(logo_surf, logo_rect)
            y = logo_rect.bottom + 10

        # Draw red headline
        headline = " - Instructions - "
        headline_surf = self.headline_font.render(headline, True, (255, 0, 0))
        headline_rect = headline_surf.get_rect(center=(centerx, y))
        play_surf.blit(headline_surf, headline_rect)
        y = headline_rect.bottom + 20
        # Calculate total height of all lines
        line_height = self.text_font.get_height()
        total_lines = len(self.lines)
        total_text_height = total_lines * line_height + (total_lines - 1) * 6
        # Vertically center the block of text in the remaining play area
        text_start_y = (play_rect.height - total_text_height) // 2
        # Adjust so it doesn't overlap the headline/logo
        text_start_y = max(text_start_y, y)
        # Draw each line centered, with extra space between paragraphs
        green1 = (0, 255, 0)
        green2 = (0, 200, 0)
        paragraph_ends = [2, 6, 8, 12, 14]  # Indices after which to add a blank line
        y_offset = 0
        for i, line in enumerate(self.lines):
            color = green1 if (i // 3) % 2 == 0 else green2  # Alternate by paragraph
            line_surf = self.text_font.render(line, True, color)
            line_rect = line_surf.get_rect(center=(centerx, text_start_y + y_offset))
            play_surf.blit(line_surf, line_rect)
            y_offset += line_height + 6
            if i in paragraph_ends:
                y_offset += 18  # Extra space between paragraphs
        # Draw amber line at bottom
        amber = self.amber_color
        amber_text = "Insert coin to start the game"
        amber_surf = self.text_font.render(amber_text, True, amber)
        amber_rect = amber_surf.get_rect(center=(centerx, play_rect.height - 40))
        play_surf.blit(amber_surf, amber_rect)
        # Blit the play window surface to the main surface at play_rect.topleft
        surface.blit(play_surf, play_rect.topleft)

    def handle_event(self, event):
        pass  # InstructionsView may handle events in the future
    def activate(self):
        pass
    def deactivate(self):
        pass 