from unittest.mock import MagicMock

from engine.audio_manager import AudioManager
from utils.event_bus import EventBus


class BallLostEvent:
    pass
class BlockHitEvent:
    pass

class UnrelatedEvent: 
    pass


def make_manager_and_bus():
    bus = EventBus()
    event_sound_map = {BallLostEvent: "ball_lost", BlockHitEvent: "block_hit"}
    mgr = AudioManager(bus, sound_dir="/fake/dir", event_sound_map=event_sound_map)
    return mgr, bus

def test_event_triggers_sound(monkeypatch):
    mgr, bus = make_manager_and_bus()
    fake_sound = MagicMock()
    mgr.sounds["ball_lost"] = fake_sound
    mgr.muted = False
    bus.fire(BallLostEvent())
    fake_sound.play.assert_called_once()

def test_no_sound_if_muted(monkeypatch):
    mgr, bus = make_manager_and_bus()
    fake_sound = MagicMock()
    mgr.sounds["ball_lost"] = fake_sound
    mgr.muted = True
    bus.fire(BallLostEvent())
    fake_sound.play.assert_not_called()

def test_set_volume_affects_sounds():
    mgr, _ = make_manager_and_bus()
    fake_sound = MagicMock()
    mgr.sounds["ball_lost"] = fake_sound
    mgr.set_volume(0.5)
    fake_sound.set_volume.assert_called_with(0.5)
    assert mgr.volume == 0.5

def test_mute_and_unmute():
    mgr, _ = make_manager_and_bus()
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
    mgr, _ = make_manager_and_bus()
    called = {}
    def fake_load_sound(name, filename):
        called[name] = filename
    mgr.load_sound = fake_load_sound
    mgr.load_sounds_from_map()
    assert called == {"ball_lost": "ball_lost.wav", "block_hit": "block_hit.wav"}

def test_unsubscribed_event_does_not_play(monkeypatch):
    mgr, bus = make_manager_and_bus()
    fake_sound = MagicMock()
    mgr.sounds["ball_lost"] = fake_sound
    bus.fire(UnrelatedEvent())
    fake_sound.play.assert_not_called() 