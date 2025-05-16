from unittest.mock import Mock

import pygame

from src.controllers.window_controller import WindowController


def make_key_event(key, mod=0):
    event = Mock()
    event.type = pygame.KEYDOWN
    event.key = key
    event.mod = mod
    return event


def test_base_controller_volume_up():
    audio_manager = Mock()
    audio_manager.get_volume.return_value = 0.5
    controller = WindowController(audio_manager=audio_manager)
    event = make_key_event(pygame.K_PLUS)
    controller.handle_events([event])
    audio_manager.set_volume.assert_called_once_with(0.6)


def test_base_controller_volume_down():
    audio_manager = Mock()
    audio_manager.get_volume.return_value = 0.5
    controller = WindowController(audio_manager=audio_manager)
    event = make_key_event(pygame.K_MINUS)
    controller.handle_events([event])
    audio_manager.set_volume.assert_called_once_with(0.4)


def test_base_controller_mute_unmute():
    audio_manager = Mock()
    audio_manager.is_muted.return_value = False
    controller = WindowController(audio_manager=audio_manager)
    event = make_key_event(pygame.K_m)
    controller.handle_events([event])
    audio_manager.mute.assert_called_once()
    audio_manager.is_muted.return_value = True
    controller.handle_events([event])
    audio_manager.unmute.assert_called_once()


def test_base_controller_quit():
    quit_callback = Mock()
    controller = WindowController(quit_callback=quit_callback)
    event = make_key_event(pygame.K_q, mod=pygame.KMOD_CTRL)
    controller.handle_events([event])
    quit_callback.assert_called_once()
