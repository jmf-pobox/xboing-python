from engine.events import ScoreChangedEvent


class ScoreDisplay:
    """
    UI component for displaying the player's score using LED-style digits.
    Subscribes to ScoreChangedEvent and renders itself in the score window region.
    Allows manual x positioning for layout compatibility.
    Renders as a fixed-width, right-justified display (default 6 digits).
    """
    def __init__(self, event_bus, layout, digit_display, x=220, width=6):
        self.event_bus = event_bus
        self.layout = layout
        self.digit_display = digit_display
        self.score = 0
        self.x = x
        self.width = width
        # Subscribe to score change events
        self.event_bus.subscribe(ScoreChangedEvent, self.on_score_changed)

    def on_score_changed(self, event):
        self.score = event.score

    def draw(self, surface):
        score_rect = self.layout.get_score_rect()
        # Render the score as a fixed-width, right-justified number
        score_surf = self.digit_display.render_number(
            self.score, spacing=2, scale=1.0, width=self.width, right_justified=True
        )
        y = score_rect.y + (score_rect.height - score_surf.get_height()) // 2
        surface.blit(score_surf, (self.x, y)) 