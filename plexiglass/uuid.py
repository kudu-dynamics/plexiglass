from contextlib import suppress
from pathlib import Path
from typing import Optional
import uuid


def get_uuid(path: Optional[Path] = None) -> str:
    """
    Generate a uuid value.

    If a path is provided, use it as a lookup and cache destination.
    """
    result = uuid.uuid4().hex
    if path is not None:
        with suppress(FileNotFoundError):
            read_result = path.read_text().strip()
            if read_result:
                result = read_result
        path.write_text(result)
    return result
