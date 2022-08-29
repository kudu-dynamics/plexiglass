from contextlib import contextmanager
import datetime
import signal
from timeit import default_timer
from typing import Any, Iterator, List, Optional


def timestamp(start: datetime.datetime = None, offset: int = 0) -> datetime.datetime:
    """Get the UTC timestamp away from the provided time by {offset} seconds."""
    if not start:
        start = datetime.datetime.utcnow()
    delta = datetime.timedelta(seconds=offset)
    return start + delta


@contextmanager
def timer(*args: Any, **kwargs: Any) -> Iterator[List[float]]:
    """
    Yields a list that can be mutated during the execution of the timer
    context manager.

    The resulting list will have a single entry that represents the elapsed time.
    """
    result: List[float] = []
    try:
        start = default_timer()
        yield result
    finally:
        end = default_timer()
        result.append(end - start)


@contextmanager
def Timeout(seconds: Optional[int]):
    """
    Raise an exception after `seconds` number of seconds have passed.

    Seconds cannot be 0.

    If an alarm handler is already present, behave as a noop and allow the
    incumbent handler precedence.
    """
    if seconds is None:
        try:
            yield
        finally:
            return

    if seconds == 0:
        raise ValueError("Cannot create a Timeout for 0 seconds.")

    signal_set = False
    try:
        original_handler = signal.getsignal(signal.SIGALRM)
        if original_handler in (signal.SIG_DFL, signal.SIG_IGN):
            signal_set = True
            signal.signal(signal.SIGALRM, lambda signum, frame: exec("raise TimeoutError"))
            signal.alarm(seconds)
        yield
    finally:
        if signal_set:
            # Cancel any pending signals.
            signal.alarm(0)
            # Restore the original signal handler.
            signal.signal(signal.SIGALRM, original_handler)
