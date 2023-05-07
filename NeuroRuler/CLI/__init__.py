"""After installing NeuroRuler via pip, the functions here are importable like so

from NeuroRuler.CLI import {function}

where NeuroRuler.CLI is the name of the package this __init__.py file is in."""

import shutil
from pathlib import Path
import pkg_resources
import NeuroRuler.CLI.main as main
import NeuroRuler.utils.parser as parser
import NeuroRuler.utils.constants as constants


def cli() -> None:
    """Run CLI.

    Will create ``cli_config.json`` using package's ``cli_config.json`` if it doesn't already exist.
    """
    if not constants.JSON_CLI_CONFIG_PATH.exists():
        json_cli_from_package: Path = Path(
            pkg_resources.resource_filename(__name__, "../../cli_config.json")
        )
        shutil.copy(json_cli_from_package, constants.JSON_CLI_CONFIG_PATH)

    parser.parse_cli_config()
    parser.parse_cli()
    main.main()
