from unittest.mock import Mock

import pygame

from xboing.ui.ui_manager import UIManager


def test_ui_manager_registration_and_draw_order():
    ui_manager = UIManager()
    # Create mocks for bars and views
    top_bar = Mock()
    bottom_bar = Mock()
    view1 = Mock()
    view2 = Mock()
    surface = Mock()

    # Register bars and views
    ui_manager.register_top_bar(top_bar)
    ui_manager.register_bottom_bar(bottom_bar)
    ui_manager.register_view("game", view1)
    ui_manager.register_view("instructions", view2)

    # Initial view should be 'game'
    assert ui_manager.current_view is view1
    assert ui_manager.current_name == "game"

    # Switch to 'instructions' view
    ui_manager.set_view("instructions")
    assert ui_manager.current_view is view2
    assert ui_manager.current_name == "instructions"

    # Draw all
    ui_manager.draw_all(surface)
    view2.draw.assert_called_once_with(surface)
    top_bar.draw.assert_called_once_with(surface)
    bottom_bar.draw.assert_called_once_with(surface)


def test_ui_manager_setup_ui_and_event_handling():
    ui_manager = UIManager()
    # Create mocks for bars and views
    top_bar = Mock()
    bottom_bar = Mock()
    view1 = Mock()
    view2 = Mock()

    # Add handle_events to mocks
    top_bar.handle_events = Mock()
    bottom_bar.handle_events = Mock()
    # Use setup_ui
    ui_manager.setup_ui(
        views={"game": view1, "instructions": view2},
        top_bar=top_bar,
        bottom_bar=bottom_bar,
        initial_view="game",
    )
    assert ui_manager.current_view is view1
    assert ui_manager.current_name == "game"
    # Switch view
    ui_manager.set_view("instructions")
    assert ui_manager.current_view is view2
    # Test handle_events with mock Pygame events
    fake_event1 = Mock()
    fake_event1.type = pygame.USEREVENT
    fake_event1.event = None
    fake_event2 = Mock()
    fake_event2.type = pygame.KEYDOWN
    fake_event2.event = None
    fake_events = [fake_event1, fake_event2]
    ui_manager.handle_events(fake_events)
    # Should call handle_events on top_bar and bottom_bar
    top_bar.handle_events.assert_called_once_with(fake_events)
    bottom_bar.handle_events.assert_called_once_with(fake_events)
