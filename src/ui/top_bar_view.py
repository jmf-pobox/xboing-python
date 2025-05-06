class TopBarView:
    def __init__(self, score_display, lives_display_component, level_display_component, timer_display_component, message_display_component, special_display_component):
        self.score_display = score_display
        self.lives_display_component = lives_display_component
        self.level_display_component = level_display_component
        self.timer_display_component = timer_display_component
        self.message_display_component = message_display_component
        self.special_display_component = special_display_component

    def draw(self, surface):
        self.score_display.draw(surface)
        self.lives_display_component.draw(surface)
        self.level_display_component.draw(surface)
        self.timer_display_component.draw(surface)
        self.message_display_component.draw(surface)
        self.special_display_component.draw(surface) 