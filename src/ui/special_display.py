from engine.events import (
    SpecialFastGunChangedEvent,
    SpecialKillerChangedEvent,
    SpecialNoWallChangedEvent,
    SpecialReverseChangedEvent,
    SpecialSaveChangedEvent,
    SpecialStickyChangedEvent,
    SpecialX2ChangedEvent,
    SpecialX4ChangedEvent,
)


class SpecialDisplay:
    """
    UI component for displaying the status of special power-ups in the special window region.
    Subscribes to events for each special and renders their state as colored labels.
    """
    LABELS = [
        ("Reverse", "reverse"), ("Save", "save"), ("NoWall", "nowall"), ("x2", "x2"),
        ("Sticky", "sticky"), ("FastGun", "fastgun"), ("Killer", "killer"), ("x4", "x4"),
    ]
    EVENT_MAP = {
        'reverse': SpecialReverseChangedEvent,
        'sticky': SpecialStickyChangedEvent,
        'save': SpecialSaveChangedEvent,
        'fastgun': SpecialFastGunChangedEvent,
        'nowall': SpecialNoWallChangedEvent,
        'killer': SpecialKillerChangedEvent,
        'x2': SpecialX2ChangedEvent,
        'x4': SpecialX4ChangedEvent,
    }

    def __init__(self, event_bus, layout, renderer, font):
        self.event_bus = event_bus
        self.layout = layout
        self.renderer = renderer
        self.font = font
        # State for each special (all off by default)
        self.state = {key: False for _, key in self.LABELS}
        # Subscribe to events
        for key, event_cls in self.EVENT_MAP.items():
            self.event_bus.subscribe(event_cls, self._make_handler(key))

    def _make_handler(self, key):
        def handler(event):
            self.state[key] = event.active
        return handler

    def draw(self, surface):
        special_rect = self.layout.special_window.rect.rect
        x0, y0 = special_rect.x + 5, special_rect.y + 3
        col_width = 49
        row_height = self.font.get_height() + 5
        for idx, (label, key) in enumerate(self.LABELS):
            col = idx % 4
            row = idx // 4
            x = x0 + col * col_width
            y = y0 + row * row_height
            color = (255, 255, 0) if self.state[key] else (255, 255, 255)
            self.renderer.draw_text(label, self.font, color, x, y, centered=False) 