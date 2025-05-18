from game.bullet import Bullet
from game.bullet_manager import BulletManager


class DummyBullet(Bullet):
    def __init__(self, x, y, active=True):
        super().__init__(x, y)
        self._active = active

    def is_active(self):
        return self._active

    def update(self, delta_ms):
        pass


def test_add_and_remove_bullet():
    bm = BulletManager()
    b1 = DummyBullet(1, 1)
    b2 = DummyBullet(2, 2)
    bm.add_bullet(b1)
    bm.add_bullet(b2)
    assert b1 in bm.bullets
    assert b2 in bm.bullets
    bm.remove_bullet(b1)
    assert b1 not in bm.bullets
    assert b2 in bm.bullets


def test_clear():
    bm = BulletManager()
    bm.add_bullet(DummyBullet(1, 1))
    bm.add_bullet(DummyBullet(2, 2))
    bm.clear()
    assert len(bm) == 0


def test_update_removes_inactive():
    bm = BulletManager()
    b1 = DummyBullet(1, 1, active=True)
    b2 = DummyBullet(2, 2, active=False)
    bm.add_bullet(b1)
    bm.add_bullet(b2)
    bm.update(16.67)
    assert b1 in bm.bullets
    assert b2 not in bm.bullets


def test_len_and_iter():
    bm = BulletManager()
    b1 = DummyBullet(1, 1)
    b2 = DummyBullet(2, 2)
    bm.add_bullet(b1)
    bm.add_bullet(b2)
    assert len(bm) == 2
    assert set(iter(bm)) == {b1, b2}
