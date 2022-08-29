import json
from typing import Any

import structlog as logging

from plexiglass import argparse_config, logging_config


def test_verbosity() -> None:
    parser = argparse_config.make_parser()
    logging_config.configure_parser(parser)

    cli_args = parser.parse_args(["-v"])
    logging_config.configure_logging(cli_args)

    assert logging_config._LOG_CONFIG["root"]["level"] == "INFO"


def test_jsonl(capsys: Any) -> None:
    parser = argparse_config.make_parser()
    logging_config.configure_parser(parser)

    cli_args = parser.parse_args(["--log-level", "DEBUG", "--jsonl"])
    logging_config.configure_logging(cli_args)

    assert logging_config._LOG_CONFIG["root"]["level"] == "DEBUG"
    assert logging_config._LOG_CONFIG["root"]["handlers"] == ["machine"]

    logging.getLogger(__name__).info("Hello!")

    # A log message when the jsonl flag is enabled should be a single json parsable line.
    captured = capsys.readouterr()
    line = json.loads(captured.err)
    assert line
    assert "event" in line
    assert line["event"] == "Hello!"
