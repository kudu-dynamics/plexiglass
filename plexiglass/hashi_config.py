"""
Configuration settings to support tool integration with HashiCorp tools.

https://www.hashicorp.com/
"""
import argparse
import os
from typing import Any, Optional


def configure_parser(parser: argparse.ArgumentParser, **kwargs: Any) -> None:
    if kwargs.get("consul", False):
        consul_group = parser.add_argument_group(
            "Consul", "flags to control Consul integration", suppress_group=kwargs.get("suppress_group", True)
        )
        consul_group.add_argument("--consul-host", help="Address of a Consul agent")
        consul_group.add_argument("--consul-port", default=8600, help="Port of a Consul agent")
    if kwargs.get("nomad", False):
        nomad_group = parser.add_argument_group(
            "Nomad", "flags to control Nomad integration", suppress_group=kwargs.get("suppress_group", True)
        )
        nomad_group.add_argument("--nomad-host", help="Address of a Nomad agent")
        nomad_group.add_argument("--nomad-port", default=4646, help="Port of a Nomad agent")
        nomad_group.add_argument("--nomad-secure", default=False, help="Whether or not to use HTTPS")


def configure_hashi(cli_args: Optional[argparse.Namespace] = None, **kwargs: Any) -> None:
    if not cli_args:
        return
    if not getattr(cli_args, "nomad_host", None):
        return
    protocol = "https" if cli_args.nomad_secure else "http"
    os.environ["NOMAD_ADDR"] = f"{protocol}://{cli_args.nomad_host}:{cli_args.nomad_port}"
