from unittest.mock import Mock, patch

import pygame

from src.controllers.game_controller import GameController
from engine.events import (
    BallShotEvent,
    MessageChangedEvent,
    PowerUpCollectedEvent,
    BombExplodedEvent,
    BallLostEvent,
    PaddleHitEvent,
    WallHitEvent
)


def make_key_event(key, mod=0):
    event = Mock()
    event.type = pygame.KEYDOWN
    event.key = key
    event.mod = mod
    return event


class PlayRect:
    def __init__(self):
        self.width = 100
        self.x = 0
        self.y = 0
        self.height = 100


class DummyPaddle:
    def __init__(self):
        self.width = 20

    def set_direction(self, d):
        pass

    def update(self, *a, **kw):
        pass


def test_ball_launch_logic():
    game_state = Mock()
    level_manager = Mock()
    balls = [Mock() for _ in range(2)]
    paddle = Mock()
    block_manager = Mock()
    renderer = Mock()
    audio_manager = Mock()
    event_sound_map = {"boing": "boing"}
    create_new_ball = Mock()
    quit_callback = Mock()
    input_manager = Mock()
    layout = Mock()
    controller = GameController(
        game_state,
        level_manager,
        balls,
        paddle,
        block_manager,
        input_manager=input_manager,
        layout=layout,
        renderer=renderer,
        audio_manager=audio_manager,
        event_sound_map=event_sound_map,
        quit_callback=quit_callback,
    )
    controller.waiting_for_launch = True
    # Patch pygame.event.post
    with patch('pygame.event.post') as mock_post:
        # Simulate mouse button down event
        event = Mock(type=1025)  # pygame.MOUSEBUTTONDOWN
        # Setup level_manager.get_level_info
        level_manager.get_level_info.return_value = {"title": "Test Level"}
        controller.handle_events([event])
        for ball in balls:
            ball.release_from_paddle.assert_called_once()
        assert controller.waiting_for_launch is False
        # Check BallShotEvent and MessageChangedEvent fired (by class name)
        assert any(
            call.args[0].type == pygame.USEREVENT and hasattr(call.args[0], 'event') and 
            isinstance(call.args[0].event, BallShotEvent)
            for call in mock_post.call_args_list
        )
        assert any(
            call.args[0].type == pygame.USEREVENT and hasattr(call.args[0], 'event') and 
            isinstance(call.args[0].event, MessageChangedEvent)
            for call in mock_post.call_args_list
        )


def test_update_balls_and_collisions_extra_ball():
    game_state = Mock()
    level_manager = Mock()
    # Start with one ball
    ball = Mock()
    ball.x = 10
    ball.y = 20
    ball.radius = 5
    ball.vx = 1  # Set to real number for math
    ball.vy = 2
    ball.update.return_value = (True, False, False)
    balls = [ball]
    paddle = Mock()
    block_manager = Mock()
    # Use a unique object for TYPE_EXTRABALL
    extra_effect = object()
    block_manager.TYPE_EXTRABALL = extra_effect
    block_manager.check_collisions.return_value = (0, 0, [extra_effect])
    renderer = Mock()
    audio_manager = Mock()
    event_sound_map = {"boing": "boing"}
    create_new_ball = Mock()
    quit_callback = Mock()
    input_manager = Mock()
    layout = Mock()
    play_rect = Mock(width=100, height=100, x=0, y=0)
    layout.get_play_rect.return_value = play_rect
    controller = GameController(
        game_state,
        level_manager,
        balls,
        paddle,
        block_manager,
        input_manager=input_manager,
        layout=layout,
        renderer=renderer,
        audio_manager=audio_manager,
        event_sound_map=event_sound_map,
        quit_callback=quit_callback,
    )
    # Patch Ball to avoid real instantiation
    import src.controllers.game_controller as gc_mod

    orig_ball = gc_mod.Ball
    new_ball_mock = Mock(x=10, y=20, radius=5, vx=-1, vy=2)
    # Make update return (True, False, False) once, then (False, False, False)
    new_ball_mock.update.side_effect = [(True, False, False), (False, False, False)]
    gc_mod.Ball = Mock(return_value=new_ball_mock)
    try:
        # Patch pygame.event.post
        with patch('pygame.event.post') as mock_post:
            controller.update_balls_and_collisions(0.016)
            # Should have added a new ball
            assert len(controller.balls) == 2
            # Should have fired PowerUpCollectedEvent
            assert any(
                call.args[0].type == pygame.USEREVENT and hasattr(call.args[0], 'event') and 
                isinstance(call.args[0].event, PowerUpCollectedEvent)
                for call in mock_post.call_args_list
            )
    finally:
        gc_mod.Ball = orig_ball


def test_update_balls_and_collisions_multiball():
    game_state = Mock()
    level_manager = Mock()
    # Start with one ball
    ball = Mock()
    ball.x = 10
    ball.y = 20
    ball.radius = 5
    ball.vx = 1
    ball.vy = 2
    ball.update.return_value = (True, False, False)
    balls = [ball]
    paddle = Mock()
    block_manager = Mock()
    # Use a unique object for TYPE_MULTIBALL
    multiball_effect = object()
    block_manager.TYPE_MULTIBALL = multiball_effect
    # Only return the effect on the first call
    block_manager.check_collisions.side_effect = [(0, 0, [multiball_effect])] + [
        (0, 0, [])
    ] * 10
    renderer = Mock()
    audio_manager = Mock()
    event_sound_map = {"boing": "boing"}
    create_new_ball = Mock()
    quit_callback = Mock()
    input_manager = Mock()
    layout = Mock()
    play_rect = Mock(width=100, height=100, x=0, y=0)
    layout.get_play_rect.return_value = play_rect
    controller = GameController(
        game_state,
        level_manager,
        balls,
        paddle,
        block_manager,
        input_manager=input_manager,
        layout=layout,
        renderer=renderer,
        audio_manager=audio_manager,
        event_sound_map=event_sound_map,
        quit_callback=quit_callback,
    )
    # Patch Ball to avoid real instantiation
    import src.controllers.game_controller as gc_mod

    orig_ball = gc_mod.Ball

    def make_new_ball(*args, **kwargs):
        m = Mock(x=10, y=20, radius=5, vx=0.8, vy=1.6)
        m.update.side_effect = [(True, False, False), (False, False, False)]
        return m

    gc_mod.Ball = Mock(side_effect=make_new_ball)
    try:
        # Patch pygame.event.post
        with patch('pygame.event.post') as mock_post:
            controller.update_balls_and_collisions(0.016)
            # Should have added two new balls (total 3)
            assert len(controller.balls) == 3
            # Should have fired PowerUpCollectedEvent
            assert any(
                call.args[0].type == pygame.USEREVENT and hasattr(call.args[0], 'event') and 
                isinstance(call.args[0].event, PowerUpCollectedEvent)
                for call in mock_post.call_args_list
            )
    finally:
        gc_mod.Ball = orig_ball


def test_update_balls_and_collisions_bomb():
    game_state = Mock()
    level_manager = Mock()
    # Start with one ball
    ball = Mock()
    ball.x = 10
    ball.y = 20
    ball.radius = 5
    ball.vx = 1
    ball.vy = 2
    ball.update.return_value = (True, False, False)
    balls = [ball]
    paddle = Mock()
    block_manager = Mock()
    # Use a unique object for TYPE_BOMB
    bomb_effect = object()
    block_manager.TYPE_BOMB = bomb_effect
    # Only return the effect on the first call
    block_manager.check_collisions.side_effect = [(0, 0, [bomb_effect])] + [
        (0, 0, [])
    ] * 10
    renderer = Mock()
    audio_manager = Mock()
    event_sound_map = {"boing": "boing"}
    create_new_ball = Mock()
    quit_callback = Mock()
    input_manager = Mock()
    layout = Mock()
    play_rect = Mock(width=100, height=100, x=0, y=0)
    layout.get_play_rect.return_value = play_rect
    controller = GameController(
        game_state,
        level_manager,
        balls,
        paddle,
        block_manager,
        input_manager=input_manager,
        layout=layout,
        renderer=renderer,
        audio_manager=audio_manager,
        event_sound_map=event_sound_map,
        quit_callback=quit_callback,
    )
    # Patch Ball to avoid real instantiation
    import src.controllers.game_controller as gc_mod

    orig_ball = gc_mod.Ball

    def make_new_ball(*args, **kwargs):
        m = Mock(x=10, y=20, radius=5, vx=0.8, vy=1.6)
        m.update.side_effect = [(True, False, False), (False, False, False)]
        return m

    gc_mod.Ball = Mock(side_effect=make_new_ball)
    try:
        # Patch pygame.event.post
        with patch('pygame.event.post') as mock_post:
            controller.update_balls_and_collisions(0.016)
            # Should have fired BombExplodedEvent
            assert any(
                call.args[0].type == pygame.USEREVENT and hasattr(call.args[0], 'event') and 
                isinstance(call.args[0].event, BombExplodedEvent)
                for call in mock_post.call_args_list
            )
    finally:
        gc_mod.Ball = orig_ball


def test_update_balls_and_collisions_paddle_expand():
    game_state = Mock()
    level_manager = Mock()
    # Start with one ball
    ball = Mock()
    ball.x = 10
    ball.y = 20
    ball.radius = 5
    ball.vx = 1
    ball.vy = 2
    ball.update.return_value = (True, False, False)
    balls = [ball]
    paddle = Mock()
    paddle.width = 10
    paddle.rect.width = 10
    block_manager = Mock()
    # Use a unique object for TYPE_PAD_EXPAND
    expand_effect = object()
    block_manager.TYPE_PAD_EXPAND = expand_effect
    # Only return the effect on the first call
    block_manager.check_collisions.side_effect = [(0, 0, [expand_effect])] + [
        (0, 0, [])
    ] * 10
    renderer = Mock()
    audio_manager = Mock()
    event_sound_map = {"boing": "boing"}
    create_new_ball = Mock()
    quit_callback = Mock()
    input_manager = Mock()
    layout = Mock()
    play_rect = Mock(width=100, height=100, x=0, y=0)
    layout.get_play_rect.return_value = play_rect
    controller = GameController(
        game_state,
        level_manager,
        balls,
        paddle,
        block_manager,
        input_manager=input_manager,
        layout=layout,
        renderer=renderer,
        audio_manager=audio_manager,
        event_sound_map=event_sound_map,
        quit_callback=quit_callback,
    )
    # Patch Ball to avoid real instantiation
    import src.controllers.game_controller as gc_mod

    orig_ball = gc_mod.Ball

    def make_new_ball(*args, **kwargs):
        m = Mock(x=10, y=20, radius=5, vx=0.8, vy=1.6)
        m.update.side_effect = [(True, False, False), (False, False, False)]
        return m

    gc_mod.Ball = Mock(side_effect=make_new_ball)
    try:
        # Patch pygame.event.post
        with patch('pygame.event.post') as mock_post:
            controller.update_balls_and_collisions(0.016)
            # Paddle width should have increased
            assert paddle.width > 10
            assert paddle.rect.width == paddle.width
            # Should have fired PowerUpCollectedEvent
            assert any(
                call.args[0].type == pygame.USEREVENT and hasattr(call.args[0], 'event') and 
                isinstance(call.args[0].event, PowerUpCollectedEvent)
                for call in mock_post.call_args_list
            )
    finally:
        gc_mod.Ball = orig_ball


def test_update_balls_and_collisions_paddle_shrink():
    game_state = Mock()
    level_manager = Mock()
    # Start with one ball
    ball = Mock()
    ball.x = 10
    ball.y = 20
    ball.radius = 5
    ball.vx = 1
    ball.vy = 2
    ball.update.return_value = (True, False, False)
    balls = [ball]
    paddle = Mock()
    paddle.width = 20
    paddle.rect.width = 20
    block_manager = Mock()
    # Use a unique object for TYPE_PAD_SHRINK
    shrink_effect = object()
    block_manager.TYPE_PAD_SHRINK = shrink_effect
    # Only return the effect on the first call
    block_manager.check_collisions.side_effect = [(0, 0, [shrink_effect])] + [
        (0, 0, [])
    ] * 10
    renderer = Mock()
    audio_manager = Mock()
    event_sound_map = {"boing": "boing"}
    create_new_ball = Mock()
    quit_callback = Mock()
    input_manager = Mock()
    layout = Mock()
    play_rect = Mock(width=100, height=100, x=0, y=0)
    layout.get_play_rect.return_value = play_rect
    controller = GameController(
        game_state,
        level_manager,
        balls,
        paddle,
        block_manager,
        input_manager=input_manager,
        layout=layout,
        renderer=renderer,
        audio_manager=audio_manager,
        event_sound_map=event_sound_map,
        quit_callback=quit_callback,
    )
    # Patch Ball to avoid real instantiation
    import src.controllers.game_controller as gc_mod

    orig_ball = gc_mod.Ball

    def make_new_ball(*args, **kwargs):
        m = Mock(x=10, y=20, radius=5, vx=0.8, vy=1.6)
        m.update.side_effect = [(True, False, False), (False, False, False)]
        return m

    gc_mod.Ball = Mock(side_effect=make_new_ball)
    try:
        # Patch pygame.event.post
        with patch('pygame.event.post') as mock_post:
            controller.update_balls_and_collisions(0.016)
            # Paddle width should have decreased
            assert paddle.width < 20
            assert paddle.rect.width == paddle.width
            # Should have fired PowerUpCollectedEvent
            assert any(
                call.args[0].type == pygame.USEREVENT and hasattr(call.args[0], 'event') and 
                isinstance(call.args[0].event, PowerUpCollectedEvent)
                for call in mock_post.call_args_list
            )
    finally:
        gc_mod.Ball = orig_ball


def test_update_balls_and_collisions_timer():
    game_state = Mock()
    level_manager = Mock()
    # Start with one ball
    ball = Mock()
    ball.x = 10
    ball.y = 20
    ball.radius = 5
    ball.vx = 1
    ball.vy = 2
    ball.update.return_value = (True, False, False)
    balls = [ball]
    paddle = Mock()
    block_manager = Mock()
    # Use a unique object for TYPE_TIMER
    timer_effect = object()
    block_manager.TYPE_TIMER = timer_effect
    # Only return the effect on the first call
    block_manager.check_collisions.side_effect = [(0, 0, [timer_effect])] + [
        (0, 0, [])
    ] * 10
    renderer = Mock()
    audio_manager = Mock()
    event_sound_map = {"boing": "boing"}
    create_new_ball = Mock()
    quit_callback = Mock()
    input_manager = Mock()
    layout = Mock()
    play_rect = Mock(width=100, height=100, x=0, y=0)
    layout.get_play_rect.return_value = play_rect
    controller = GameController(
        game_state,
        level_manager,
        balls,
        paddle,
        block_manager,
        input_manager=input_manager,
        layout=layout,
        renderer=renderer,
        audio_manager=audio_manager,
        event_sound_map=event_sound_map,
        quit_callback=quit_callback,
    )
    # Patch Ball to avoid real instantiation
    import src.controllers.game_controller as gc_mod

    orig_ball = gc_mod.Ball

    def make_new_ball(*args, **kwargs):
        m = Mock(x=10, y=20, radius=5, vx=0.8, vy=1.6)
        m.update.side_effect = [(True, False, False), (False, False, False)]
        return m

    gc_mod.Ball = Mock(side_effect=make_new_ball)
    try:
        # Patch pygame.event.post
        with patch('pygame.event.post') as mock_post:
            controller.update_balls_and_collisions(0.016)
            # Should have called add_time on level_manager
            level_manager.add_time.assert_called_with(20)
            # Should have fired PowerUpCollectedEvent
            assert any(
                call.args[0].type == pygame.USEREVENT and hasattr(call.args[0], 'event') and 
                isinstance(call.args[0].event, PowerUpCollectedEvent)
                for call in mock_post.call_args_list
            )
    finally:
        gc_mod.Ball = orig_ball


def test_update_balls_and_collisions_ball_lost():
    game_state = Mock()
    level_manager = Mock()
    # Start with one ball that will be lost
    ball = Mock()
    ball.x = 10
    ball.y = 20
    ball.radius = 5
    ball.vx = 1
    ball.vy = 2
    ball.update.return_value = (False, False, False)
    balls = [ball]
    paddle = Mock()
    block_manager = Mock()
    block_manager.check_collisions.return_value = (0, 0, [])
    renderer = Mock()
    audio_manager = Mock()
    event_sound_map = {"boing": "boing"}
    create_new_ball = Mock()
    quit_callback = Mock()
    input_manager = Mock()
    layout = Mock()
    play_rect = Mock(width=100, height=100, x=0, y=0)
    layout.get_play_rect.return_value = play_rect
    controller = GameController(
        game_state,
        level_manager,
        balls,
        paddle,
        block_manager,
        input_manager=input_manager,
        layout=layout,
        renderer=renderer,
        audio_manager=audio_manager,
        event_sound_map=event_sound_map,
        quit_callback=quit_callback,
    )
    # Patch pygame.event.post
    with patch('pygame.event.post') as mock_post:
        controller.update_balls_and_collisions(0.016)
        # Ball should be removed from balls list
        assert len(controller.balls) == 0
        # Should have fired BallLostEvent
        assert any(
            call.args[0].type == pygame.USEREVENT and hasattr(call.args[0], 'event') and 
            isinstance(call.args[0].event, BallLostEvent)
            for call in mock_post.call_args_list
        )


def test_update_balls_and_collisions_paddle_hit():
    game_state = Mock()
    level_manager = Mock()
    # Start with one ball that will hit the paddle
    ball = Mock()
    ball.x = 10
    ball.y = 20
    ball.radius = 5
    ball.vx = 1
    ball.vy = 2
    ball.update.return_value = (True, True, False)
    balls = [ball]
    paddle = Mock()
    block_manager = Mock()
    block_manager.check_collisions.return_value = (0, 0, [])
    renderer = Mock()
    audio_manager = Mock()
    event_sound_map = {"boing": "boing"}
    create_new_ball = Mock()
    quit_callback = Mock()
    input_manager = Mock()
    layout = Mock()
    play_rect = Mock(width=100, height=100, x=0, y=0)
    layout.get_play_rect.return_value = play_rect
    controller = GameController(
        game_state,
        level_manager,
        balls,
        paddle,
        block_manager,
        input_manager=input_manager,
        layout=layout,
        renderer=renderer,
        audio_manager=audio_manager,
        event_sound_map=event_sound_map,
        quit_callback=quit_callback,
    )
    # Patch pygame.event.post
    with patch('pygame.event.post') as mock_post:
        controller.update_balls_and_collisions(0.016)
        # Ball should remain in balls list
        assert len(controller.balls) == 1
        # Should have fired PaddleHitEvent
        assert any(
            call.args[0].type == pygame.USEREVENT and hasattr(call.args[0], 'event') and 
            isinstance(call.args[0].event, PaddleHitEvent)
            for call in mock_post.call_args_list
        )


def test_update_balls_and_collisions_wall_hit_without_sound():
    game_state = Mock()
    level_manager = Mock()
    # Start with one ball that will hit the wall
    ball = Mock()
    ball.x = 10
    ball.y = 20
    ball.radius = 5
    ball.vx = 1
    ball.vy = 2
    ball.update.return_value = (True, False, True)
    balls = [ball]
    paddle = Mock()
    block_manager = Mock()
    block_manager.check_collisions.return_value = (0, 0, [])
    renderer = Mock()
    audio_manager = Mock()
    event_sound_map = {"boing": "boing"}
    create_new_ball = Mock()
    quit_callback = Mock()
    input_manager = Mock()
    layout = Mock()
    play_rect = Mock(width=100, height=100, x=0, y=0)
    layout.get_play_rect.return_value = play_rect
    # Set event_sound_map but no audio_manager
    controller = GameController(
        game_state,
        level_manager,
        balls,
        paddle,
        block_manager,
        input_manager=input_manager,
        layout=layout,
        renderer=renderer,
        audio_manager=audio_manager,
        event_sound_map=event_sound_map,
        quit_callback=quit_callback,
    )
    # Patch pygame.event.post
    with patch('pygame.event.post') as mock_post:
        controller.update_balls_and_collisions(0.016)
        # Ball should remain in balls list
        assert len(controller.balls) == 1
        # Should have fired WallHitEvent
        assert any(
            call.args[0].type == pygame.USEREVENT and hasattr(call.args[0], 'event') and 
            isinstance(call.args[0].event, WallHitEvent)
            for call in mock_post.call_args_list
        )
