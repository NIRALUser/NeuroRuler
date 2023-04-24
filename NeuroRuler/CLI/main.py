"""
Defines main(), the entrypoint of the CLI (if you want to call it that).
"""
from NeuroRuler.utils.constants import ThresholdFilter
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
    get_curr_image_size,
    get_curr_rotated_slice,
    get_curr_smooth_slice,
    get_curr_metadata,
    get_curr_binary_thresholded_slice,
    get_curr_otsu_slice,
    get_curr_physical_units,
    get_curr_path,
    get_curr_properties_tuple,
    get_middle_dimension,
)


def main() -> None:
    """Main entrypoint of CLI."""
    file_path = Path(cli_settings.FILE)

    initialize_globals([file_path])

    global_vars.THETA_X = cli_settings.THETA_X
    global_vars.THETA_Y = cli_settings.THETA_Y
    global_vars.THETA_Z = cli_settings.THETA_Z
    if cli_settings.SLICE != -1:  # initialize_globals will init it fine otherwise
        global_vars.SLICE = cli_settings.SLICE

    global_vars.CONDUCTANCE_PARAMETER = cli_settings.CONDUCTANCE_PARAMETER
    global_vars.SMOOTHING_ITERATIONS = cli_settings.SMOOTHING_ITERATIONS
    global_vars.TIME_STEP = cli_settings.TIME_STEP

    rotated_slice: sitk.Image = get_curr_rotated_slice()

    binary_contour_slice: np.ndarray = np.zeros(0)
    if cli_settings.USE_OTSU:
        binary_contour_slice: np.ndarray = imgproc.contour(
            rotated_slice, ThresholdFilter.Otsu
        )
    else:  # != otsu => use binary
        global_vars.BINARY_THRESHOLD_FILTER.SetLowerThreshold(
            cli_settings.LOWER_THRESHOLD
        )

        global_vars.BINARY_THRESHOLD_FILTER.SetUpperThreshold(
            cli_settings.UPPER_THRESHOLD
        )

        binary_contour_slice: np.ndarray = imgproc.contour(
            rotated_slice, ThresholdFilter.Binary
        )

    units: Union[str, None] = get_curr_physical_units()
    circumference: float = imgproc.length_of_contour(binary_contour_slice)

    print(circumference)
    print(units)


if __name__ == "__main__":
    import NeuroRuler.utils.parser as parser

    parser.parse_cli_config()
    parser.parse_cli()
    main()
