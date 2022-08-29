"""
Configuration settings to support opentracing tooling.

https://github.com/jaegertracing/jaeger-client-python
https://github.com/opentracing/opentracing-python
"""
import argparse
from typing import Any


def configure_parser(parser: argparse.ArgumentParser, **kwargs: Any) -> None:
    group = parser.add_argument_group(
        "Tracing", "flags to control opentracing integration", suppress_group=kwargs.get("suppress_group", True)
    )
    group.add_argument("--tracing-host", default="127.0.0.1", help="Address of a Dgraph Alpha server")
    group.add_argument("--tracing-port", default="9080", help="Port of a Dgraph Alpha server (9080: grpc, 8080: http)")
