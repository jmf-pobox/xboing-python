from engine.events import MessageChangedEvent


class MessageDisplay:
    """
    UI component for displaying messages in the message window region.
    Subscribes to MessageChangedEvent and renders itself using renderer.draw_text.
    Style matches the timer: bright green, same font size.
    """

    def __init__(self, layout, renderer, font):
        self.layout = layout
        self.renderer = renderer
        self.font = font
        self.message = ""
        self.alignment = "left"

    def handle_events(self, events):
        for event in events:
            if hasattr(event, "event") and isinstance(event.event, MessageChangedEvent):
                self.message = event.event.message
                self.alignment = event.event.alignment

    def draw(self, surface):
        message_rect = self.layout.get_message_rect()
        y = message_rect.y + (message_rect.height // 2)
        if self.alignment == "center":
            x = message_rect.x + (message_rect.width // 2)
            centered = True
        else:
            x = message_rect.x + 10  # Left margin
            centered = False
        # Always use bright green, matching the timer
        color = (0, 255, 0)
        self.renderer.draw_text(
            self.message,
            self.font,
            color,
            x,
            y,
            centered=centered,
        )
