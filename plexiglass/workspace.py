"""
Create a workspace for the tools to store and process artifacts.

A workspace is created such that four subdirectories are created.
/path/to/workspace/[debug, download, upload]
"""
import argparse
from contextlib import contextmanager, suppress
from pathlib import Path
import shutil
import tempfile
import time
from typing import IO, Iterator, Optional


class WorkspaceError(Exception):
    pass


@contextmanager
def createfile(cli_args: argparse.Namespace, workspace, fname: str) -> Iterator[IO]:
    """Create a file in the desired workspace with the designated fname.

    Creates a temporary file and atomically moves it (Linux POSIX guarantees) so
    that downstream consumers see the fully constructed file.
    """
    if workspace not in cli_args.workspace_dirs:
        raise ValueError(f"invalid workspace '{workspace}'")
    target = cli_args.workspace_dirs[workspace] / fname

    # Atomically overwrite the destination with the data.
    temp_path: Optional[Path] = None
    try:
        with tempfile.NamedTemporaryFile(delete=False) as tfile:
            temp_path = Path(tfile.name)
            # Allow the user to directly write to the temporary file.
            yield tfile.file
        shutil.move(temp_path, target)
        while not target.exists():
            time.sleep(0.1)
    except:  # pragma: no cover
        raise
    finally:
        # Delete the temporary file whether or not it was successfully moved.
        with suppress(AttributeError, FileNotFoundError):
            temp_path.unlink()


def existsfile(cli_args: argparse.Namespace, workspace, fname: str) -> bool:
    """Check if a particular file exists in the specified workspace."""
    if workspace not in cli_args.workspace_dirs:
        raise ValueError(f"invalid workspace '{workspace}'")
    target = cli_args.workspace_dirs[workspace] / fname
    return target.exists()


def check_error_flag(cli_args: argparse.Namespace) -> bool:
    """
    Check if the workspace error flag exists.
    """
    return (cli_args.workspace_dirs.debug / "error").exists()


def set_error_flag(cli_args: argparse.Namespace) -> None:  # pragma: no cover
    """
    If an error occurs, create a file signifying that the workspace needs
    manual intervention.
    """
    with (cli_args.workspace_dirs.debug / "error").open("w"):
        pass
