from engine.events import LevelChangedEvent


class LevelDisplay:
    """
    UI component for displaying the current level number using LED-style digits.
    Subscribes to LevelChangedEvent and renders itself in the level window region.
    Allows manual x positioning for layout compatibility.
    """
    def __init__(self, event_bus, layout, digit_display, x=510):
        self.event_bus = event_bus
        self.layout = layout
        self.digit_display = digit_display
        self.level = 1
        self.x = x
        # Subscribe to level change events
        self.event_bus.subscribe(LevelChangedEvent, self.on_level_changed)

    def on_level_changed(self, event):
        self.level = event.level

    def draw(self, surface):
        score_rect = self.layout.get_score_rect()
        # Render the level using DigitDisplay
        level_surf = self.digit_display.render_number(self.level, spacing=2, scale=1.0)
        y = score_rect.y + (score_rect.height - level_surf.get_height()) // 2
        surface.blit(level_surf, (self.x, y)) 