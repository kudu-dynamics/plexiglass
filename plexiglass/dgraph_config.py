"""
Configuration settings to support tool integrations with Dgraph.

https://dgraph.io/
"""
import argparse
from typing import Any


def configure_parser(parser: argparse.ArgumentParser, **kwargs: Any) -> None:
    dgraph_group = parser.add_argument_group(
        "Dgraph", "flags to control Dgraph integration", suppress_group=kwargs.get("suppress_group", True)
    )
    dgraph_group.add_argument("--dgraph-host", default="127.0.0.1", help="Address of a Dgraph Alpha server")
    dgraph_group.add_argument(
        "--dgraph-port", default="9080", help="Port of a Dgraph Alpha server (9080: grpc, 8080: http)"
    )
