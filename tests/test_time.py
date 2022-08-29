import time

from plexiglass.time import timestamp, timer


def test_basic() -> None:
    start = timestamp()
    time.sleep(1)
    assert timestamp() > start

    with timer() as elapsed:
        time.sleep(1)
    assert len(elapsed) > 0
    assert isinstance(elapsed[0], float)
    assert elapsed[0] > 0.0
