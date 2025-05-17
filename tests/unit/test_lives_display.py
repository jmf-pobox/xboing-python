import logging
from unittest import mock

import pytest

from renderers.lives_renderer import LivesRenderer


@pytest.fixture(autouse=True)
def patch_pygame(monkeypatch):
    # Mock for the ball image with correct get_width/get_height
    mock_ball_image = mock.MagicMock()
    mock_ball_image.get_width.return_value = 10
    mock_ball_image.get_height.return_value = 10
    # convert_alpha returns the same mock
    mock_ball_image.convert_alpha.return_value = mock_ball_image
    monkeypatch.setattr("pygame.image.load", lambda path: mock_ball_image)
    # Patch pygame.Surface to return a new mock for each call
    surface_mocks = []

    def surface_factory(size, flags=0):
        s = mock.MagicMock()
        s.get_width.return_value = size[0]
        s.get_height.return_value = size[1]
        surface_mocks.append((s, size))
        return s

    monkeypatch.setattr("pygame.Surface", surface_factory)
    monkeypatch.setattr(
        "pygame.transform.smoothscale", lambda img, size: mock_ball_image
    )
    return surface_mocks


def test_render_surface_size_and_visibility(monkeypatch, patch_pygame):
    display = LivesRenderer()
    patch_pygame.clear()  # Clear any previous calls
    surf = display.render(num_lives=2, spacing=5, scale=1.0, max_lives=3)
    # Surface size: (ball_width * max_lives) + (spacing * (max_lives-1))
    expected_width = (10 * 3) + (5 * 2)
    expected_height = 10
    print("Surface sizes created:", [size for s, size in patch_pygame])
    # Find the surface created for the display
    found = any(size == (expected_width, expected_height) for s, size in patch_pygame)
    assert (
        found
    ), f"Expected surface of size {(expected_width, expected_height)} to be created"
    assert surf is not None


def test_render_all_visible(monkeypatch, patch_pygame):
    display = LivesRenderer()
    surf = display.render(num_lives=3, spacing=2, scale=1.0, max_lives=3)
    assert surf is not None


def test_render_none_visible(monkeypatch, patch_pygame):
    display = LivesRenderer()
    surf = display.render(num_lives=0, spacing=2, scale=1.0, max_lives=3)
    assert surf is not None


def test_cache(monkeypatch, patch_pygame):
    display = LivesRenderer()
    surf1 = display.render(2, 4, 1.0, 3)
    surf2 = display.render(2, 4, 1.0, 3)
    # Should be cached (same object)
    assert surf1 is surf2
    # Different parameters should not be cached as the same
    surf3 = display.render(1, 4, 1.0, 3)
    assert surf3 is not surf1
    # Check the cache keys
    assert (2, 4, 1.0, 3) in display._surface_cache
    assert (1, 4, 1.0, 3) in display._surface_cache


def test_fallback_empty_surface(monkeypatch):
    # Patch image load to always fail
    monkeypatch.setattr(
        "pygame.image.load", lambda path: (_ for _ in ()).throw(FileNotFoundError())
    )
    monkeypatch.setattr("os.path.exists", lambda path: False)
    # Patch pygame.Surface to return a new mock
    monkeypatch.setattr("pygame.Surface", lambda size, flags=0: mock.MagicMock())
    display = LivesRenderer()
    surf = display.render(2, 4, 1.0, 3)
    # Should return a mock surface (empty)
    assert surf is not None


def test_logging_warning_for_missing_image(monkeypatch, caplog):
    monkeypatch.setattr(
        "pygame.image.load", lambda path: (_ for _ in ()).throw(FileNotFoundError())
    )
    monkeypatch.setattr("os.path.exists", lambda path: False)
    # Patch pygame.Surface to return a new mock
    monkeypatch.setattr("pygame.Surface", lambda size, flags=0: mock.MagicMock())
    with caplog.at_level(logging.WARNING, logger="xboing.lives_display"):
        display = LivesRenderer()
        assert display is not None
    assert any(
        "Could not load ball image for lives display" in r.getMessage()
        for r in caplog.records
    )


def test_invisible_balls_on_left(monkeypatch, patch_pygame):
    # This test checks the logic for invisible balls on the left
    display = LivesRenderer()
    # Patch surface.blit to record calls
    calls = []

    def fake_blit(img, pos):
        calls.append(pos)

    mock_surface = mock.MagicMock()
    mock_surface.get_width.return_value = 10
    mock_surface.get_height.return_value = 10
    mock_surface.blit.side_effect = fake_blit
    monkeypatch.setattr("pygame.image.load", lambda path: mock_surface)
    monkeypatch.setattr("pygame.Surface", lambda size, flags=0: mock_surface)
    monkeypatch.setattr("pygame.transform.smoothscale", lambda img, size: mock_surface)
    display = LivesRenderer()
    display.ball_image = mock_surface
    display.ball_width = 10
    display.ball_height = 10
    display._surface_cache = {}  # Clear cache
    display.render(num_lives=1, spacing=0, scale=1.0, max_lives=3)
    # Only the last position should be used for blit
    assert calls == [(20, 0)]  # (2*10, 0) is the rightmost ball
