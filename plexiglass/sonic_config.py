"""
Configuration settings to support tool integrations with Sonic.
"""
import argparse
from typing import Any


def configure_parser(parser: argparse.ArgumentParser, **kwargs: Any) -> None:
    group = parser.add_argument_group(
        "Sonic", "flags to control Sonic integration", suppress_group=kwargs.get("suppress_group", True)
    )
    group.add_argument("--sonic-host", default="127.0.0.1", help="Address of a Sonic server")
    group.add_argument("--sonic-port", default="1491", help="Port of a Sonic server")
