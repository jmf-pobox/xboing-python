class BottomBarView:
    def __init__(self, message_display_component, special_display_component, timer_display_component):
        self.message_display_component = message_display_component
        self.special_display_component = special_display_component
        self.timer_display_component = timer_display_component

    def draw(self, surface):
        self.message_display_component.draw(surface)
        self.special_display_component.draw(surface)
        self.timer_display_component.draw(surface) 