"""
Configures logging behavior with both the stdlib logging library as well as
the 3rd-party structlog library.

Logging configuration taken from https://www.fun4jimmy.com/2015/09/15/configuring-pythons-logging-module-with-argparse.html  # noqa

.. code-block:: python

    from plexiglass import argparse_config, logging_config

    parser = argparse_config.make_parser()
    logging_config.configure_parser(parser)

    cli_args = parser.parse_args(argv)
    logging_config.configure_logging(cli_args)

A tool created from the above code could be configured from the console.

.. code-block:: bash

    $ python3 plexiglass-example.py --log-level {CRITICAL,ERROR,WARNING,INFO,DEBUG}

    $ python3 plexiglass-example.py -vv  # Equivalent to log-level DEBUG

    $ python3 plexiglass-example.py --jsonl  # Emits log lines in jsonl format

The logging configuration code can be run without an argument parser as well.

.. code-block:: python

   from plexiglass import logging_config

   logging_config.configure_logging()
"""
import argparse
from contextlib import suppress
import logging
import logging.config
from typing import Any, Dict, Optional

import structlog
from structlog.stdlib import LoggerFactory


_LOG_LEVEL_STRINGS = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]
_LOG_CONFIG: Dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "[%(levelname)s] %(name)s: %(message)s"},
        "verbose": {"format": "%(asctime)s : [%(levelname)s] %(name)s: %(message)s"},
        "machine": {"format": "%(message)s"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "simple"},
        "machine": {"class": "logging.StreamHandler", "formatter": "machine"},
    },
    "loggers": {"asyncio": {"level": "WARNING"}, "urllib3.connectionpool": {"level": "WARNING"}},
    "root": {"handlers": ["machine"], "level": "WARNING"},
}


def configure_parser(parser: argparse.ArgumentParser) -> None:
    log_group = parser.add_argument_group("Logging", "flags to control logging")
    log_group.add_argument("--jsonl", action="store_true", help="Emit JSON logs parsable by tools like logstash")
    log_group.add_argument(
        "--log-level",
        choices=_LOG_LEVEL_STRINGS,
        default=_LOG_CONFIG["root"]["level"],
        help="Set the logging output level",
    )
    log_group.add_argument("-v", "--verbose", action="count", help="Enable verbose logging")


def _configure_stdlib_logging(**kwargs: Any) -> None:
    default_level = _LOG_CONFIG["root"]["level"]
    log_level = kwargs.get("log_level", default_level)

    if log_level == default_level:
        level_index = _LOG_LEVEL_STRINGS.index(log_level)
        highest_level_index = len(_LOG_LEVEL_STRINGS) - 1
        # Each verbosity flag increases the log level.
        with suppress(TypeError, ValueError):
            level_index = min(highest_level_index, level_index + kwargs.get("verbose", 0))
        _LOG_CONFIG["root"]["level"] = _LOG_LEVEL_STRINGS[level_index]
    else:
        _LOG_CONFIG["root"]["level"] = log_level

    logging.config.dictConfig(_LOG_CONFIG)


def _configure_structlog_logging(**kwargs: Any) -> None:
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper("iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    if kwargs.get("jsonl", False):
        processors.append(structlog.processors.JSONRenderer())
    else:
        colors = False
        with suppress(ImportError):
            import colorama  # noqa

            colors = True
        processors.append(structlog.dev.ConsoleRenderer(colors=colors))

    structlog.configure(
        logger_factory=LoggerFactory(), processors=processors, wrapper_class=structlog.stdlib.BoundLogger
    )


def configure_logging(cli_args: Optional[argparse.Namespace] = None, **kwargs: Any) -> None:
    """Set the log level.

    The argument flags allow directly setting the log level, but also use the
    verbosity flags from the parsed `args` to determine the output log level.
    """
    # Options provided at the command line through argparse supersede those
    # explicitly set in code.
    if cli_args:
        kwargs.update(vars(cli_args))

    if kwargs.get("jsonl", False):
        _LOG_CONFIG["root"]["handlers"] = ["machine"]
    _configure_stdlib_logging(**kwargs)
    _configure_structlog_logging(**kwargs)
