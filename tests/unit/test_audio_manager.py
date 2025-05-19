from unittest.mock import MagicMock

import pygame

from xboing.engine.audio_manager import AudioManager
from xboing.engine.events import AmmoFiredEvent, XBoingEvent


class BallLostEvent(XBoingEvent):
    sound_effect = "ball_lost"
    pass


class BlockHitEvent(XBoingEvent):
    sound_effect = "block_hit"
    pass


class UnrelatedEvent(XBoingEvent):
    pass


def make_manager():
    pygame.init()  # Initialize pygame for events
    mgr = AudioManager(sound_dir="/fake/dir")
    return mgr


def test_event_triggers_sound(monkeypatch):
    mgr = make_manager()
    fake_sound = MagicMock()
    mgr.sounds["ball_lost"] = fake_sound
    mgr.muted = False

    # Create a pygame event with our custom event
    event = pygame.event.Event(pygame.USEREVENT, {"event": BallLostEvent()})
    mgr.handle_events([event])

    fake_sound.play.assert_called_once()


def test_no_sound_if_muted(monkeypatch):
    mgr = make_manager()
    fake_sound = MagicMock()
    mgr.sounds["ball_lost"] = fake_sound
    mgr.muted = True

    # Create a pygame event with our custom event
    event = pygame.event.Event(pygame.USEREVENT, {"event": BallLostEvent()})
    mgr.handle_events([event])

    fake_sound.play.assert_not_called()


def test_set_volume_affects_sounds():
    mgr = make_manager()
    fake_sound = MagicMock()
    mgr.sounds["ball_lost"] = fake_sound
    mgr.set_volume(0.5)
    fake_sound.set_volume.assert_called_with(0.5)
    assert mgr.volume == 0.5


def test_mute_and_unmute():
    mgr = make_manager()
    fake_sound = MagicMock()
    mgr.sounds["ball_lost"] = fake_sound
    mgr.set_volume(0.7)
    mgr.mute()
    fake_sound.set_volume.assert_called_with(0)
    assert mgr.is_muted()
    mgr.unmute()
    fake_sound.set_volume.assert_called_with(0.7)
    assert not mgr.is_muted()


def test_load_sounds_from_map(monkeypatch):
    mgr = make_manager()
    called = {}

    def fake_load_sound(name, filename):
        called[name] = filename

    mgr.load_sound = fake_load_sound

    # Patch __subclasses__ to only return the test event classes
    monkeypatch.setattr(
        XBoingEvent, "__subclasses__", lambda: [BallLostEvent, BlockHitEvent]
    )

    mgr.load_sounds_from_events()
    assert called == {"ball_lost": "ball_lost.wav", "block_hit": "block_hit.wav"}


def test_unsubscribed_event_does_not_play(monkeypatch):
    mgr = make_manager()
    fake_sound = MagicMock()
    mgr.sounds["ball_lost"] = fake_sound

    # Create a pygame event with an unrelated custom event
    event = pygame.event.Event(pygame.USEREVENT, {"event": UnrelatedEvent()})
    mgr.handle_events([event])

    fake_sound.play.assert_not_called()


def test_ammo_fired_event_triggers_sound(monkeypatch):
    mgr = make_manager()
    fake_sound = MagicMock()
    mgr.sounds["shoot"] = fake_sound
    mgr.muted = False
    event = pygame.event.Event(pygame.USEREVENT, {"event": AmmoFiredEvent(3)})
    mgr.handle_events([event])
    fake_sound.play.assert_called_once()
