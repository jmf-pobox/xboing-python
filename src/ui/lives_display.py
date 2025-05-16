from engine.events import LivesChangedEvent


class LivesDisplayComponent:
    """
    UI component for displaying the player's remaining lives as ball images.
    Subscribes to LivesChangedEvent and renders itself in the lives window region.
    Allows manual x positioning for layout compatibility.
    """

    def __init__(self, layout, lives_display_util, x=365, max_lives=3):
        self.layout = layout
        self.lives_display_util = lives_display_util
        self.lives = max_lives
        self.max_lives = max_lives
        self.x = x

    def handle_events(self, events):
        for event in events:
            if hasattr(event, "event") and isinstance(event.event, LivesChangedEvent):
                self.lives = event.event.lives

    def draw(self, surface):
        score_rect = self.layout.get_score_rect()
        # Render the lives using the utility
        lives_surf = self.lives_display_util.render(
            self.lives, spacing=10, scale=1.0, max_lives=self.max_lives
        )
        y = score_rect.y + (score_rect.height - lives_surf.get_height()) // 2
        surface.blit(lives_surf, (self.x, y))
