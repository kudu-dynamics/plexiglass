"""
Monkey Patch the argparse ActionContainer classes to support automatically using
an inferred environment variable to supply default values.

Here there be dragons...
"""
import argparse
from contextlib import suppress
import os
import sys
from typing import Any, Optional, Union


_MODIFIED = False


def new_init(self: Union[argparse.ArgumentParser, argparse._ArgumentGroup], *args: Any, **kwargs: Any) -> None:
    """
    Set an appropriate prefix for environment variable defaults.
    """
    # Pop out a prefix to prepend to any environment variable override.
    if "prefix" in kwargs:
        self.prefix = kwargs.pop("prefix").rstrip("_").upper()
    else:
        self.prefix = ""
    if self.prefix:
        self.prefix += "_"

    # Allow certain argument groups be muted unless a full `--help` is invoked.
    if "suppress_group" in kwargs:
        self.suppress_group = kwargs.pop("suppress_group")
    else:
        self.suppress_group = False

    # Route back to the original __init__ function.
    self._init(*args, **kwargs)


def new_infer_name(self: argparse._ActionsContainer, name: str, use_prefix: bool = True) -> str:
    """
    Given an argument long option name, generate the corresponding environment
    variable name.
    """
    return "".join([self.prefix if use_prefix else "", name.lstrip("-").upper().replace("-", "_")])


def override(name: str, **kwargs: Any) -> Any:
    """
    Take an environment variable and argument parameters to determine a default value.
    """
    arg_action = kwargs.get("action", None)
    # Override the default value with that of the corresponding environment
    # variable if not explicitly disabled.
    arg_default = kwargs.get("default", None)
    arg_type = kwargs.get("type", str)

    # Actions provide a lot of sensible defaults.
    if arg_action == "count":
        arg_default = arg_default or 0
        arg_type = int
    elif arg_action == "store_true":
        arg_default = False
        arg_type = bool
    elif arg_action == "store_false":
        arg_default = True
        arg_type = bool
    # Support basic types, custom types can be handled by the user.
    elif kwargs.get("nargs", "") in ("+", "*") or isinstance(arg_default, list):
        arg_default = arg_default or []
        arg_type = list

    # Coerce the type before returning.
    if not kwargs.get("disable_envvar_override", False):
        arg_default = os.environ.get(name, arg_default)
    if arg_default is not None:
        if not isinstance(arg_default, list):
            arg_default = arg_type(arg_default)
    return arg_default


def new_add_argument(self: argparse._ActionsContainer, *args: Any, **kwargs: Any) -> None:
    """
    Hook add_argument to change the default value to support an
    environment variable default.
    """
    # Allow for certain arguments to not have the prefix added.
    use_prefix = True
    with suppress(KeyError):
        use_prefix = kwargs.pop("use_prefix")

    # Iterate through args for safety.
    for arg in args:
        if arg.startswith("--") and not arg.endswith("help") and not arg.endswith("version"):
            name = self._infer_name(arg, use_prefix)
            # Don't override/provide a default value for a required or a const flag.
            if "const" in kwargs or "required" in kwargs:
                break
            kwargs["default"] = override(name, **kwargs)
            break

    # Route back to the original add_argument.
    self._add_argument(*args, **kwargs)


def new_format_help(self: argparse.ArgumentParser) -> str:
    # Save the original action groups before modifying their help output.
    action_groups = self._action_groups[:]

    # Print the help for a group that is suppressed only if the full --help
    # is passed in.
    self._action_groups = [
        ag for ag in self._action_groups if "--help" in sys.argv or not getattr(ag, "suppress_group", False)
    ]
    help_str = self._format_help()
    # Restore the original action groups.
    self._action_groups = action_groups
    return help_str


if not _MODIFIED:
    _MODIFIED = True

    # Target classes that implement add_argument and allow them to be configured
    # with a prefix that will be prepended to their environment variable defaults.
    # Monkey patch their __init__ functions as needed to allow this attribute
    # setting behavior.
    original_ap_init = argparse.ArgumentParser.__init__
    argparse.ArgumentParser._init = original_ap_init
    argparse.ArgumentParser.__init__ = new_init

    original_ap_format_help = argparse.ArgumentParser.format_help
    argparse.ArgumentParser._format_help = original_ap_format_help
    argparse.ArgumentParser.format_help = new_format_help

    original_ag_init = argparse._ArgumentGroup.__init__
    argparse._ArgumentGroup._init = original_ag_init
    argparse._ArgumentGroup.__init__ = new_init

    # Then modify only the add_argument on the _ActionsContainer that
    # ArgumentParser, _ArgumentGroup, etc inherit from.
    original_add = argparse._ActionsContainer.add_argument
    argparse._ActionsContainer._add_argument = original_add
    argparse._ActionsContainer.add_argument = new_add_argument

    # Add the new _infer_name function we need to the _ActionsContainer object.
    argparse._ActionsContainer._infer_name = new_infer_name


class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    pass


# Public API for argparse.ArgumentParser instances to use.
def make_parser(name: str = "", description: Optional[str] = None, version: Optional[str] = None):
    """
    Pass in __file__ and all of the arguments will be settable with
    a prefix.

    E.g: make_parser("PURIFIER")

    PURIFIER_CONSUL_HOST=10.0.0.1 purifier

    is equivalent to

    purifier --consul-host 10.0.0.1
    """
    parser = argparse.ArgumentParser(
        description=description, formatter_class=CustomFormatter, prefix=os.path.splitext(name)[0].upper()
    )
    if version:
        parser.add_argument("--version", action="version", version=version)
    return parser
