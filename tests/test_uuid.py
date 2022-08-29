from pathlib import Path
from tempfile import NamedTemporaryFile

from plexiglass.uuid import get_uuid


def test_basic_uuid() -> None:
    assert len(get_uuid()) == 32


def test_basic_uuid_no_dup() -> None:
    assert get_uuid() != get_uuid()


def test_uuid_from_nonexistent_path() -> None:
    with NamedTemporaryFile(mode="r+") as fd:
        path = Path(fd.name)

    assert not path.exists()
    value = get_uuid(path)
    assert path.exists()
    assert len(Path(fd.name).read_text()) == 32

    # Test loading the uuid back in.
    assert value == path.read_text()

    path.unlink()


def test_uuid_from_empty_file() -> None:
    with NamedTemporaryFile(mode="r+") as fd:
        path = Path(fd.name)
        assert path.exists()
        assert not path.read_text()
        # Read nothing and write the UUID.
        value = get_uuid(path)
        # Read the previously written UUID.
        value = get_uuid(path)
        assert len(path.read_text()) == 32
        assert value == path.read_text()
