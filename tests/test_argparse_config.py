import argparse
from contextlib import suppress
import os
import sys
import tempfile
from typing import Any
from unittest.mock import patch

from plexiglass import argparse_config, dgraph_config, hashi_config, logging_config, synapse_config, workspace_config


def test_type() -> None:
    """
    Through monkey patching, the argparse module has been changed.
    """
    parser = argparse.ArgumentParser()
    assert isinstance(parser, argparse.ArgumentParser)
    # These functions have been renamed to preserve the originals.
    assert getattr(parser, "_init", None)
    assert getattr(parser, "_format_help", None)


def test_prefix_envvar() -> None:
    """
    The make_parser API allows setting flags via environment variables
    automatically. Providing a use_prefix boolean will determine whether or
    not the environment variable needs to be prefixed with the parser namespace.
    """
    with patch.dict(os.environ, {"TEST_FIRST_FLAG": "10", "SECOND_FLAG": "1", "TEST_THIRD_FLAG": "2"}):
        parser = argparse_config.make_parser("TEST", version="0.0.1")
        parser.add_argument("--first-flag", type=int)
        parser.add_argument("--second-flag", type=int, use_prefix=False)
        parser.add_argument("--third-flag", type=int)
        parser.add_argument("--fourth-flag", type=int)
        cli_args = parser.parse_args(None)
        assert cli_args.first_flag == 10
        assert cli_args.second_flag == 1
        assert cli_args.third_flag == 2
        assert cli_args.fourth_flag is None


def test_arg_type_conversion() -> None:
    parser = argparse.ArgumentParser()
    # "count" actions implicitly type their flag to int.
    parser.add_argument("--verbose", action="count", default=0)
    # "store_true" and "store_false" actions are implicitly typed to bool.
    parser.add_argument("--yes-or-no", action="store_false")
    parser.add_argument("--no-or-yes", action="store_true")
    # nargs force a list.
    parser.add_argument("--num", nargs="*")

    cli_args = parser.parse_args(["--num", "1", "2"])
    assert cli_args.verbose == 0
    assert cli_args.yes_or_no is True
    assert cli_args.no_or_yes is False
    assert cli_args.num == ["1", "2"]


def test_required_no_override() -> None:
    """
    Arguments that are required or have a const value assigned should not be overridden.
    """
    with patch.dict(os.environ, {"SET_THIS": "999", "NEED": "WHAT"}):
        parser = argparse.ArgumentParser()
        parser.add_argument("--set-this", const=10, nargs="?")
        parser.add_argument("--need", required=True)

        cli_args = parser.parse_args(["--set-this", "--need", "help"])
        assert cli_args.set_this == 10
        assert cli_args.need == "help"


def test_suppress_group(capsys: Any) -> None:
    parser = argparse.ArgumentParser()
    s_group = parser.add_argument_group("Hidden!", suppress_group=True)
    s_group.add_argument("--test", action="store_true")

    # Suppressed groups are hidden when the tool is invoked with '-h'.
    with suppress(SystemExit):
        parser.parse_args(["-h"])
    capture = capsys.readouterr()
    assert "Hidden!" not in capture.out

    with suppress(SystemExit):
        parser.parse_args(["--help"])
    capture = capsys.readouterr()
    assert "Hidden!" not in capture.out

    # Suppressed groups are displayed when the tool is invoked with '--help'
    # from the command line.
    with patch.object(sys, "argv", [__name__, "--help"]):
        with suppress(SystemExit):
            parser.parse_args(["--help"])
    capture = capsys.readouterr()
    assert "Hidden!" in capture.out


def test_all_configs() -> None:
    """
    Cover all config options.
    """
    parser = argparse.ArgumentParser()
    dgraph_config.configure_parser(parser)
    hashi_config.configure_parser(parser, consul=True, nomad=True)
    logging_config.configure_parser(parser)
    synapse_config.configure_parser(
        parser, synapse_axon=True, synapse_cortex=True, synapse_cryo=True, synapse_tags=True
    )
    workspace_config.configure_parser(parser)

    with tempfile.TemporaryDirectory() as tmpdir:
        cli_args = parser.parse_args(["--workspace-dir", tmpdir])
        logging_config.configure_logging(cli_args)
        workspace_config.configure_workspace(cli_args)
