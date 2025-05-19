import pytest

from xboing.game.ball import Ball
from xboing.game.ball_manager import BallManager


class DummyBall(Ball):
    def __init__(self, x, y, active=True, stuck_to_paddle=False):
        super().__init__(x, y)
        self.active = active
        self.stuck_to_paddle = stuck_to_paddle


@pytest.fixture
def ball_manager():
    return BallManager()


def test_add_and_remove_ball(ball_manager):
    b1 = DummyBall(1, 1)
    b2 = DummyBall(2, 2)
    ball_manager.add_ball(b1)
    ball_manager.add_ball(b2)
    assert b1 in ball_manager.balls
    assert b2 in ball_manager.balls
    ball_manager.remove_ball(b1)
    assert b1 not in ball_manager.balls
    assert b2 in ball_manager.balls


def test_clear(ball_manager):
    ball_manager.add_ball(DummyBall(1, 1))
    ball_manager.add_ball(DummyBall(2, 2))
    ball_manager.clear()
    assert len(ball_manager) == 0


def test_reset_with_and_without_initial_ball(ball_manager):
    b = DummyBall(1, 1)
    ball_manager.add_ball(b)
    ball_manager.reset()
    assert len(ball_manager) == 0
    ball_manager.reset(initial_ball=b)
    assert len(ball_manager) == 1
    assert ball_manager.balls[0] is b


def test_has_ball_in_play(ball_manager):
    b1 = DummyBall(1, 1, active=True, stuck_to_paddle=False)
    b2 = DummyBall(2, 2, active=True, stuck_to_paddle=True)
    b3 = DummyBall(3, 3, active=False, stuck_to_paddle=False)
    ball_manager.add_ball(b1)
    ball_manager.add_ball(b2)
    ball_manager.add_ball(b3)
    assert ball_manager.has_ball_in_play() is True
    ball_manager.clear()
    ball_manager.add_ball(b2)
    ball_manager.add_ball(b3)
    assert ball_manager.has_ball_in_play() is False


def test_len_and_iter(ball_manager):
    b1 = DummyBall(1, 1)
    b2 = DummyBall(2, 2)
    ball_manager.add_ball(b1)
    ball_manager.add_ball(b2)
    assert len(ball_manager) == 2
    assert set(iter(ball_manager)) == {b1, b2}


def test_available_balls(ball_manager):
    b1 = DummyBall(1, 1)
    b2 = DummyBall(2, 2)
    ball_manager.add_ball(b1)
    ball_manager.add_ball(b2)
    assert ball_manager.available_balls() == 2


def test_active_ball_and_number_of_active_balls(ball_manager):
    b1 = DummyBall(1, 1, active=True)
    b2 = DummyBall(2, 2, active=False)
    ball_manager.add_ball(b1)
    ball_manager.add_ball(b2)
    assert ball_manager.active_ball() is True
    assert ball_manager.number_of_active_balls() == 1
    ball_manager.clear()
    ball_manager.add_ball(DummyBall(3, 3, active=False))
    assert ball_manager.active_ball() is False
    assert ball_manager.number_of_active_balls() == 0
