"""
Configuration settings to support tool integrations with Redis.
"""
import argparse
from typing import Any


def configure_parser(parser: argparse.ArgumentParser, **kwargs: Any) -> None:
    group = parser.add_argument_group(
        "Redis", "flags to control Redis integration", suppress_group=kwargs.get("suppress_group", True)
    )
    group.add_argument("--redis-host", default="127.0.0.1", help="Address of a Redis server")
    group.add_argument("--redis-port", default="6379", help="Port of a Redis server")
    group.add_argument("--redis-db", default="0", help="Redis db")
