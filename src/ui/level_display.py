from engine.events import LevelChangedEvent


class LevelDisplay:
    """
    UI component for displaying the current level number using LED-style digits.
    Subscribes to LevelChangedEvent and renders itself in the level window region.
    Allows manual x positioning for layout compatibility.
    """

    def __init__(self, layout, digit_display, x=510):
        self.layout = layout
        self.digit_display = digit_display
        self.level = 1
        self.x = x

    def handle_events(self, events):
        for event in events:
            if hasattr(event, "event") and isinstance(event.event, LevelChangedEvent):
                self.level = event.event.level

    def draw(self, surface):
        score_rect = self.layout.get_score_rect()
        # Render the level using DigitRenderer
        level_surf = self.digit_display.render_number(self.level, spacing=2, scale=1.0)
        y = score_rect.y + (score_rect.height - level_surf.get_height()) // 2
        surface.blit(level_surf, (self.x, y))
