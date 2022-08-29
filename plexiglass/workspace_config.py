import argparse
from pathlib import Path
from typing import List

from plexiglass.jot import Jot
from plexiglass.uuid import get_uuid


DEFAULT_WORKSPACES = ["debug", "download", "upload"]


def configure_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--workspace-dir", help="Directory to house workspaces", required=True, type=Path)


def configure_workspace(cli_args: argparse.Namespace, extra_workspaces: List[str] = []) -> None:
    """
    Expose an argparse args attribute for each workspace directory.
    """
    setattr(cli_args, "workspace_dirs", Jot())
    for workspace in DEFAULT_WORKSPACES + extra_workspaces:
        workspace_dir = cli_args.workspace_dir / workspace
        workspace_dir.mkdir(parents=True, exist_ok=True)
        cli_args.workspace_dirs[workspace] = workspace_dir
    # Create a file to track the unique id of the client.
    cli_args.owner_id = get_uuid(cli_args.workspace_dir / "uuid")
