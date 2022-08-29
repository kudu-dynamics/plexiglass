"""
Configuration settings to support tool integration with NATS.

https://nats-io.github.io/docs/
"""
import argparse
from typing import Any, Optional


def configure_parser(parser: argparse.ArgumentParser, **kwargs: Any) -> None:
    nats_group = parser.add_argument_group(
        "NATS", "flags to control NATS integration", suppress_group=kwargs.get("suppress_group", True)
    )
    nats_group.add_argument("--nats-host", help="Address of a NATS server")
    nats_group.add_argument("--nats-port", help="Port of a NATS server", default=4222)
    nats_group.add_argument("--nats-channel", help="NATS channel to interact with")


def configure_nats(cli_args: Optional[argparse.Namespace] = None, **kwargs: Any) -> None:
    if not cli_args:
        return
    setattr(cli_args, "nats_server", f"nats://{cli_args.nats_host}:{cli_args.nats_port}")
