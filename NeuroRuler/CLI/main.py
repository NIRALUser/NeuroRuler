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
    update_images,
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

    #reader = sitk.ImageFileReader()
    #reader.SetFileName(str(file_path))
    #new_img: sitk.Image = reader.Execute()
    #new_img: sitk.Image = sitk.DICOMOrientImageFilter().Execute(new_img)
    ##new_img = sitk.DICOMOrientImageFilter().Execute(new_img)

    #euler = sitk.Euler3DTransform()
    #euler.SetRotation(0, 0, 0)
    #rotated_image: sitk.Image = sitk.Resample(new_img, euler)
    #rotated_slice = rotated_image[:, :, 79] # last is the slice

    #binary_contour_slice: np.ndarray = imgproc.contour(
    #    rotated_slice, ThresholdFilter.Binary
    #)

    #circumference: float = imgproc.length_of_contour(binary_contour_slice)
    #print(circumference)
    global_vars.SLICE = 79

    rotated_slice: sitk.Image = get_curr_rotated_slice()
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
