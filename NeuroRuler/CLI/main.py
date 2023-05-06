"""Defines ``main()``, the entrypoint of the CLI.

See ``tests/test_cli.py`` for examples of how to use this script.

Run with the ``-h`` option to see all CLI options."""

import NeuroRuler.utils.constants as constants
import NeuroRuler.utils.global_vars as global_vars
import NeuroRuler.utils.imgproc as imgproc
import NeuroRuler.utils.cli_settings as cli_settings
import SimpleITK as sitk
import numpy as np
from pathlib import Path
from typing import Union

from NeuroRuler.utils.img_helpers import (
    initialize_globals,
    get_curr_image,
    get_curr_rotated_slice,
    get_curr_physical_units,
)


def main() -> None:
    """Main entrypoint of CLI."""
    file_path = Path(cli_settings.FILE)

    initialize_globals([file_path])

    # slice options
    global_vars.THETA_X = cli_settings.THETA_X
    global_vars.THETA_Y = cli_settings.THETA_Y
    global_vars.THETA_Z = cli_settings.THETA_Z
    if (
        cli_settings.SLICE != -1
    ):  # initialize_globals will init it to middle slice if -1
        global_vars.SLICE = cli_settings.SLICE

    # smoothing options
    global_vars.SMOOTHING_FILTER.SetConductanceParameter(
        cli_settings.CONDUCTANCE_PARAMETER
    )
    global_vars.SMOOTHING_FILTER.SetNumberOfIterations(
        cli_settings.SMOOTHING_ITERATIONS
    )
    global_vars.SMOOTHING_FILTER.SetTimeStep(cli_settings.TIME_STEP)

    rotated_slice: sitk.Image = get_curr_rotated_slice()

    # Binary threshold setting application
    # Won't be used if cli_settings.THRESHOLD_FILTER is Otsu, but applied anyway
    global_vars.BINARY_THRESHOLD_FILTER.SetLowerThreshold(
        cli_settings.LOWER_BINARY_THRESHOLD
    )
    global_vars.BINARY_THRESHOLD_FILTER.SetUpperThreshold(
        cli_settings.UPPER_BINARY_THRESHOLD
    )

    binary_contour_slice: np.ndarray = imgproc.contour(
        rotated_slice, cli_settings.THRESHOLD_FILTER
    )

    spacing: tuple = get_curr_image().GetSpacing()
    units: Union[str, None] = get_curr_physical_units()
    circumference: float = imgproc.length_of_contour_with_spacing(
        binary_contour_slice, spacing[0], spacing[1]
    )

    if cli_settings.RAW:
        print(circumference)
    else:
        print(
            f"Calculated Circumference: {round(circumference, constants.NUM_DIGITS_TO_ROUND_TO)} {units if units is not None else constants.MESSAGE_TO_SHOW_IF_UNITS_NOT_FOUND}"
        )


if __name__ == "__main__":
    import NeuroRuler.utils.parser as parser

    parser.parse_cli_config()
    parser.parse_cli()
    main()
