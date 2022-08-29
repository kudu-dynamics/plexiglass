from pathlib import Path

import tempfile

import pytest

from plexiglass import argparse_config, workspace, workspace_config


def test_basic() -> None:
    parser = argparse_config.make_parser()
    workspace_config.configure_parser(parser)

    with tempfile.TemporaryDirectory() as tmpdir_path:
        cli_args = parser.parse_args(["--workspace-dir", tmpdir_path])
        workspace_config.configure_workspace(cli_args)

        assert (Path(tmpdir_path) / "uuid").exists()
        assert not workspace.check_error_flag(cli_args)
        workspace.set_error_flag(cli_args)
        assert workspace.check_error_flag(cli_args)

        assert not workspace.existsfile(cli_args, "download", "help")
        with workspace.createfile(cli_args, "download", "help") as tmp:
            tmp.write(b"hello world")
        assert workspace.existsfile(cli_args, "download", "help")

        target = cli_args.workspace_dirs.download / "help"
        assert target.read_text() == "hello world"


def test_bad_workspace() -> None:
    parser = argparse_config.make_parser()
    workspace_config.configure_parser(parser)

    with tempfile.TemporaryDirectory() as tmpdir_path:
        cli_args = parser.parse_args(["--workspace-dir", tmpdir_path])
        workspace_config.configure_workspace(cli_args)

        with pytest.raises(ValueError):
            workspace.existsfile(cli_args, "non-existent", "nope")

        with pytest.raises(ValueError):
            with workspace.createfile(cli_args, "non-existent", "nope") as tmp:
                raise ValueError(tmp)
