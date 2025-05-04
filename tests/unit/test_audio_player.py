import os
import threading
import pytest
from unittest import mock
from utils.audio_player import DirectAudioPlayer

@pytest.fixture(autouse=True)
def patch_pygame_mixer(monkeypatch):
    # Patch pygame.mixer.init to do nothing
    monkeypatch.setattr("pygame.mixer.init", lambda *args, **kwargs: None)
    # Patch pygame.mixer.Sound to a mock
    mock_sound = mock.MagicMock()
    monkeypatch.setattr("pygame.mixer.Sound", lambda path: mock_sound)
    return mock_sound

def test_get_sound_caches_and_returns(monkeypatch, tmp_path):
    # Create a fake wav file
    sound_name = "test_sound"
    sound_path = tmp_path / f"{sound_name}.wav"
    sound_path.write_bytes(b"RIFF....WAVEfmt ")  # Minimal fake header
    player = DirectAudioPlayer(sounds_dir=str(tmp_path))
    # Should load and cache
    sound1 = player.get_sound(sound_name)
    sound2 = player.get_sound(sound_name)
    assert sound1 is sound2  # Cached

def test_get_sound_missing_file(tmp_path):
    player = DirectAudioPlayer(sounds_dir=str(tmp_path))
    with pytest.raises(FileNotFoundError):
        player.get_sound("does_not_exist")

def test_get_sound_load_error(monkeypatch, tmp_path):
    # Patch pygame.mixer.Sound to raise
    monkeypatch.setattr("pygame.mixer.Sound", lambda path: (_ for _ in ()).throw(Exception("fail")))
    sound_name = "fail_sound"
    sound_path = tmp_path / f"{sound_name}.wav"
    sound_path.write_bytes(b"RIFF....WAVEfmt ")
    player = DirectAudioPlayer(sounds_dir=str(tmp_path))
    with pytest.raises(Exception):
        player.get_sound(sound_name)

def test_play_sound_success(monkeypatch, tmp_path):
    # Patch Sound.play to return a mock channel
    mock_channel = mock.MagicMock()
    mock_sound = mock.MagicMock()
    mock_sound.play.return_value = mock_channel
    monkeypatch.setattr("pygame.mixer.Sound", lambda path: mock_sound)
    sound_name = "playme"
    sound_path = tmp_path / f"{sound_name}.wav"
    sound_path.write_bytes(b"RIFF....WAVEfmt ")
    player = DirectAudioPlayer(sounds_dir=str(tmp_path))
    channel = player.play_sound(sound_name)
    assert channel is mock_channel
    mock_sound.play.assert_called_once()

def test_play_sound_failure(monkeypatch, tmp_path):
    # Patch get_sound to raise
    player = DirectAudioPlayer(sounds_dir=str(tmp_path))
    player.get_sound = mock.MagicMock(side_effect=Exception("fail"))
    channel = player.play_sound("fail")
    assert channel is None

def test_clear_cache(tmp_path):
    sound_name = "clearme"
    sound_path = tmp_path / f"{sound_name}.wav"
    sound_path.write_bytes(b"RIFF....WAVEfmt ")
    player = DirectAudioPlayer(sounds_dir=str(tmp_path))
    # Patch Sound
    with mock.patch("pygame.mixer.Sound") as mock_sound:
        player.get_sound(sound_name)
        assert player.sounds  # Cache is not empty
        player.clear_cache()
        assert not player.sounds

def test_thread_safety(tmp_path):
    sound_name = "threaded"
    sound_path = tmp_path / f"{sound_name}.wav"
    sound_path.write_bytes(b"RIFF....WAVEfmt ")
    player = DirectAudioPlayer(sounds_dir=str(tmp_path))
    with mock.patch("pygame.mixer.Sound") as mock_sound:
        results = []
        def load():
            results.append(player.get_sound(sound_name))
        threads = [threading.Thread(target=load) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        # All should return the same (cached) object
        assert all(r is results[0] for r in results) 