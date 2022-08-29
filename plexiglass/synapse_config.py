import argparse
from functools import wraps
import os
from pathlib import Path
from typing import Any, Callable


def configure_parser(parser: argparse.ArgumentParser, **kwargs: Any) -> None:
    synapse_group = parser.add_argument_group("Synapse", "flags to control Synapse integration", suppress_group=True)

    add_all = kwargs.get("synapse", False)

    if add_all or kwargs.get("synapse_axon", False):
        synapse_group.add_argument("--axon-url", default="axon", help="URL/alias of an axon to interact with")
    if add_all or kwargs.get("synapse_cortex", False):
        synapse_group.add_argument("--cortex-url", default="cortex", help="URL/alias of a cortex to interact with")
    if add_all or kwargs.get("synapse_cryo", False):
        synapse_group.add_argument("--cryocell-url", default="cryo", help="URL/alias of a cryocell to interact with")
        synapse_group.add_argument(
            "--cryotank-name", default="virustotal:filefeed:2018:09", help="Name of the cryotank to process"
        )
    if add_all or kwargs.get("synapse_dir", False):
        synapse_group.add_argument(
            "--synapse-dir",
            default=f"{Path(os.getenv('HOME')) / '.syn'}",
            type=Path,
            help="Directory for Synapse-related data",
        )
    if add_all or kwargs.get("synapse_tags", False):
        synapse_group.add_argument(
            "--synapse-tags", default=[], help="Synapse tags to apply to any uploaded Synapse nodes", nargs="*"
        )


def syn_context(make_url: Callable[[argparse.Namespace], str], name: str) -> Callable:  # pragma: no cover
    def outer_wrapper(function: Callable) -> Callable:
        @wraps(function)
        def wrapper(cli_args: argparse.Namespace, *args: Any, **kwargs: Any) -> Any:
            import synapse.telepath as s_telepath

            with s_telepath.openurl(make_url(cli_args)) as context:
                kwargs[name] = context
                return function(cli_args, *args, **kwargs)

        return wrapper

    return outer_wrapper


with_axon = syn_context(lambda cli_args: str(cli_args.axon_url), "axon")
with_cortex = syn_context(lambda cli_args: str(cli_args.cortex_url), "cortex")
with_cryocell = syn_context(lambda cli_args: str(cli_args.cryocell_url), "cryocell")
with_cryotank = syn_context(lambda cli_args: "/".join((cli_args.cryocell_url, cli_args.cryotank_name)), "cryotank")
