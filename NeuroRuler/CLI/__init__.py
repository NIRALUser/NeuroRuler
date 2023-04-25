"""After installing NeuroRuler via pip, the functions here are importable like so

from NeuroRuler.CLI import {function}

where NeuroRuler.CLI is the name of the package this __init__.py file is in."""

import NeuroRuler.CLI.main as main
import NeuroRuler.utils.parser as parser


def cli() -> None:
    """Run CLI."""
    parser.parse_cli_config()
    parser.parse_cli()
    main.main()
