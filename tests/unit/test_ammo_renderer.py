import pygame

from xboing.renderers.ammo_renderer import AmmoRenderer


def test_ammo_renderer_renders_correct_surface(monkeypatch):
    # Patch bullet image
    fake_bullet = pygame.Surface((8, 16))
    monkeypatch.setattr(AmmoRenderer, "_load_bullet_image", lambda self: fake_bullet)
    renderer = AmmoRenderer()
    # Test rendering with 0 ammo
    surf = renderer.render(0, spacing=2, max_ammo=5)
    assert surf.get_width() == (8 * 5) + (2 * 4)
    assert surf.get_height() == 16
    # Test rendering with partial ammo
    surf = renderer.render(2, spacing=2, max_ammo=5)
    assert surf.get_width() == (8 * 5) + (2 * 4)
    # Test rendering with max ammo
    surf = renderer.render(5, spacing=2, max_ammo=5)
    assert surf.get_width() == (8 * 5) + (2 * 4)
    # Test cache works
    surf2 = renderer.render(5, spacing=2, max_ammo=5)
    assert surf is surf2
