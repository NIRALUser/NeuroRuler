"""After installing NeuroRuler via pip, the functions here are importable like so

from NeuroRuler.CLI import {function}

where NeuroRuler.CLI is the name of the package this __init__.py file is in."""


def cli() -> None:
    """Run CLI."""
    parser.parse_gui_config()
    parser.parse_cli()
    climain.main()
