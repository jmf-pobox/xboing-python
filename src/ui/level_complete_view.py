import pygame
from .content_view import ContentView

class LevelCompleteView(ContentView):
    def __init__(self, layout, renderer, font, small_font, game_state, level_manager, on_advance_callback=None):
        self.layout = layout
        self.renderer = renderer
        self.font = font
        self.small_font = small_font
        self.game_state = game_state
        self.level_manager = level_manager
        self.on_advance_callback = on_advance_callback
        self._compute_bonuses()
        self.active = False

    def _compute_bonuses(self):
        # Gather stats and compute bonuses (stub, to be filled in with real logic)
        self.level_num = self.game_state.level
        self.level_title = self.level_manager.get_level_info().get('title', f"Level {self.level_num}")
        # Example stats (replace with real calculations)
        self.coin_bonus = 0  # TODO: integrate real coin bonus logic
        self.super_bonus = False
        self.level_bonus = self.level_num * 100  # Example
        self.bullet_bonus = 0  # TODO: integrate real bullet bonus logic
        self.time_bonus = self.level_manager.get_time_remaining() * 10  # Example
        self.total_bonus = self.coin_bonus + (50000 if self.super_bonus else 0) + self.level_bonus + self.bullet_bonus + self.time_bonus
        self.final_score = self.game_state.score + self.total_bonus

    def activate(self):
        self.active = True
        self._compute_bonuses()

    def deactivate(self):
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if self.on_advance_callback:
                self.on_advance_callback()

    def draw(self, surface):
        play_rect = self.layout.get_play_rect()
        overlay = pygame.Surface((play_rect.width, play_rect.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))  # Semi-transparent black
        surface.blit(overlay, play_rect.topleft)
        centerx = play_rect.width // 2
        y = 60
        # Headline
        headline = "LEVEL COMPLETE!"
        headline_surf = self.font.render(headline, True, (50, 255, 50))
        headline_rect = headline_surf.get_rect(center=(centerx, y))
        surface.blit(headline_surf, (play_rect.x + headline_rect.x, play_rect.y + headline_rect.y))
        y = headline_rect.bottom + 20
        # Level title
        title_surf = self.small_font.render(self.level_title, True, (200, 200, 255))
        title_rect = title_surf.get_rect(center=(centerx, y))
        surface.blit(title_surf, (play_rect.x + title_rect.x, play_rect.y + title_rect.y))
        y = title_rect.bottom + 30
        # Bonus breakdown
        lines = [
            f"Coin Bonus: {self.coin_bonus}",
            f"Super Bonus: {'50000' if self.super_bonus else '0'}",
            f"Level Bonus: {self.level_bonus}",
            f"Bullet Bonus: {self.bullet_bonus}",
            f"Time Bonus: {self.time_bonus}",
            f"Total Bonus: {self.total_bonus}",
            f"Final Score: {self.final_score}",
        ]
        for line in lines:
            line_surf = self.small_font.render(line, True, (255, 255, 200))
            line_rect = line_surf.get_rect(center=(centerx, y))
            surface.blit(line_surf, (play_rect.x + line_rect.x, play_rect.y + line_rect.y))
            y = line_rect.bottom + 10
        # Prompt
        prompt = "Press SPACE for next level"
        prompt_surf = self.small_font.render(prompt, True, (200, 200, 200))
        prompt_rect = prompt_surf.get_rect(center=(centerx, play_rect.height - 40))
        surface.blit(prompt_surf, (play_rect.x + prompt_rect.x, play_rect.y + prompt_rect.y)) 