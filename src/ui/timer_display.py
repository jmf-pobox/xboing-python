from engine.events import TimerUpdatedEvent


class TimerDisplay:
    """
    UI component for displaying the level timer in MM:SS format using a yellow font.
    Subscribes to TimerUpdatedEvent and renders itself in the time window region.
    Uses renderer.draw_text, not digit sprites.
    """

    def __init__(self, layout, renderer, font, x=0):
        self.layout = layout
        self.renderer = renderer
        self.font = font
        self.time_remaining = 0
        self.x = x

    def handle_events(self, events):
        for event in events:
            if hasattr(event, "event") and isinstance(event.event, TimerUpdatedEvent):
                self.time_remaining = event.event.time_remaining

    def draw(self, surface):
        # Get the time window rect from layout
        time_rect = self.layout.time_window.rect.rect

        # Format time as MM:SS
        minutes = self.time_remaining // 60
        seconds = self.time_remaining % 60
        time_str = f"{minutes:02d}:{seconds:02d}"

        # Render as green if the timer is high, red if low
        if self.time_remaining > 10:
            timer_color = (0, 255, 0)
        else:
            timer_color = (255, 50, 50)

        # Draw the timer text centered in the time window
        self.renderer.draw_text(
            time_str,
            self.font,
            timer_color,
            time_rect.x + (time_rect.width // 2),
            time_rect.y + (time_rect.height // 2),
            centered=True,
        )
