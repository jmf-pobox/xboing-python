import pytest
from ui.content_view_manager import ContentViewManager


class MockView:
    def __init__(self):
        self.drawn = False
    def draw(self, surface):
        self.drawn = True

@pytest.fixture
def manager():
    return ContentViewManager()

def test_register_and_set_view(manager):
    v1 = MockView()
    v2 = MockView()
    manager.register_view('a', v1)
    manager.register_view('b', v2)
    assert manager.current_view == v1
    manager.set_view('b')
    assert manager.current_view == v2
    assert manager.current_name == 'b'

def test_draw_delegation(manager):
    v = MockView()
    manager.register_view('main', v)
    manager.set_view('main')
    manager.draw(None)
    assert v.drawn

def test_set_view_invalid(manager):
    with pytest.raises(ValueError):
        manager.set_view('not_registered') 