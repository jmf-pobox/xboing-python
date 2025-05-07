import pytest
from unittest.mock import Mock
from src.ui.ui_manager import UIManager

def test_ui_manager_registration_and_draw_order():
    ui_manager = UIManager()
    # Create mocks for bars, content view manager, overlays
    top_bar = Mock()
    bottom_bar = Mock()
    content_view_manager = Mock()
    overlay1 = Mock()
    overlay2 = Mock()
    surface = Mock()

    # Register components
    ui_manager.register_top_bar(top_bar)
    ui_manager.register_bottom_bar(bottom_bar)
    ui_manager.register_content_view_manager(content_view_manager)
    ui_manager.add_overlay(overlay1)
    ui_manager.add_overlay(overlay2)

    # Call draw_all
    ui_manager.draw_all(surface)

    # Check draw order: content_view_manager, top_bar, bottom_bar, overlays
    content_view_manager.draw.assert_called_once_with(surface)
    top_bar.draw.assert_called_once_with(surface)
    bottom_bar.draw.assert_called_once_with(surface)
    overlay1.draw.assert_called_once_with(surface)
    overlay2.draw.assert_called_once_with(surface) 