class TopBarView:
    def __init__(
        self,
        score_display,
        lives_display_component,
        level_display_component,
        timer_display_component,
        message_display_component,
        special_display_component,
    ):
        self.score_display = score_display
        self.lives_display_component = lives_display_component
        self.level_display_component = level_display_component
        self.timer_display_component = timer_display_component
        self.message_display_component = message_display_component
        self.special_display_component = special_display_component

    def handle_events(self, events):
        # Forward events to all components that have a handle_events method
        if hasattr(self.score_display, 'handle_events'):
            self.score_display.handle_events(events)
        if hasattr(self.lives_display_component, 'handle_events'):
            self.lives_display_component.handle_events(events)
        if hasattr(self.level_display_component, 'handle_events'):
            self.level_display_component.handle_events(events)
        if hasattr(self.timer_display_component, 'handle_events'):
            self.timer_display_component.handle_events(events)
        if hasattr(self.message_display_component, 'handle_events'):
            self.message_display_component.handle_events(events)
        if hasattr(self.special_display_component, 'handle_events'):
            self.special_display_component.handle_events(events)

    def draw(self, surface):
        self.score_display.draw(surface)
        self.lives_display_component.draw(surface)
        self.level_display_component.draw(surface)
        self.timer_display_component.draw(surface)
        self.message_display_component.draw(surface)
        self.special_display_component.draw(surface)
