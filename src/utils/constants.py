"""Constant values and functions. DO NOT MUTATE ANY VARIABLE IN THIS FILE!

This file holds values that will never change after program setup, unlike global_vars.py.
No values here should be modifiable by the user, unlike user_settings.py.
But things like THEMES, a mutable set that will never change after initial setup, can go here.

This file should not import any module in this repo to avoid circular imports."""


from pathlib import Path
import warnings
import functools
from numpy import pi
from typing import Union
from enum import Enum

JSON_CONFIG_PATH: Path = Path("config.json")
"""Settings that configure user_settings.py"""
EXPECTED_NUM_FIELDS_IN_JSON: int = 10
"""Number of expected fields in JSON config file. If the number of fields discovered does not match this, an exception
will be raised."""

SUPPORTED_EXTENSIONS: tuple = ("*.nii.gz", "*.nii", "*.nrrd")
"""File formats supported. Must be a subset of the file formats supported by SimpleITK.

TODO: Support .txt for loading image paths from text file (which we can quite easily export using global_vars.IMAGE_GROUPS)."""
EXAMPLE_DATA_DIR: Path = Path("ExampleData")
"""Directory for storing example data."""

UI_FILE_PATH: Path = Path("src") / "GUI" / "mainwindow.ui"
COMPILED_UI_FILE_PATH: Path = Path("src") / "GUI" / "ui_mainwindow.py"

THEME_DIR: Path = Path("src") / "GUI" / "themes"
"""themes/ directory where .qss stylesheets and resources.py files are stored."""
THEMES: list[str] = []
"""List of themes, i.e. the names of the directories in THEME_DIR."""
if len(list(THEME_DIR.glob("*"))) != 0:
    for path in THEME_DIR.iterdir():
        if path.is_dir():
            THEMES.append(path.name)
    THEMES = sorted(THEMES)
else:
    # Without this, autodocumentation crashes
    pass

HCT_MAIN_COLOR: str = "b55162"
"""HCT's copyrighted color :P

The pink-ish color used in the midterm presentation. Imperceptibly different from the website logo color."""

DARK_THEME_COLOR: str = "3daee9"
"""Blue that's the main color in dark theme"""
LIGHT_THEME_COLOR: str = "3daef3"
"""Blue that's the main color in light theme"""


class View(Enum):
    """X, Y, or Z view.

    The letters are assigned indices 0-2 to be used for indexing operations."""

    X = 0
    Y = 1
    Z = 2


class ThresholdFilter(Enum):
    """Determines the threshold filter (Otsu or binary) used in imgproc.contour()."""

    Otsu = 0
    Binary = 1


class BinaryColor(Enum):
    Black = 0
    White = 1


ROTATION_MIN: int = -90
"""In degrees"""
ROTATION_MAX: int = 90
"""In degrees"""


NUM_CONTOURS_IN_INVALID_SLICE: int = 10
"""If this number of contours or more is detected in a slice after processing by contour()
(Otsu, largest component, etc.), then the slice is considered invalid."""

NIFTI_METADATA_UNITS_VALUE_TO_PHYSICAL_UNITS: dict[str, str] = {
    "0": "unknown",
    "1": "meters (m)",
    "2": "millimeters (mm)",
    "3": "microns (μm)",
    "8": "seconds (s)",
    "16": "milliseconds (ms)",
    "24": "microseconds (μs)",
    "32": "Hertz (Hz)",
    "40": "parts-per-million (ppm)",
    "48": "radians per second (rad/s)",
}
"""Maps the value of `xyzt_units` of the metadata of a NIfTI file to physical meaning.

Based on https://brainder.org/2012/09/23/the-nifti-file-format/.

See img_helpers.py MRIImage for code to get metadata using sitk."""

NIFTI_METADATA_UNITS_KEY: str = "xyzt_units"
"""In the NIfTI metadata dictionary, the numerical str value attached to this key represents units of the file."""

NUM_DIGITS_TO_ROUND_TO: int = 3
"""For floats, number of digits to round to, i.e. round(float, n)."""


# Got these values by looking at ITK-SNAP and
# https://simpleitk.org/doxygen/latest/html/classitk_1_1simple_1_1DICOMOrientImageFilter.html#details
# Two characters in each string orients the image properly (i.e., same as ITK-SNAP)
# The remaining character affects direction of rotations (CCW vs CW)

# TODO: X rotation goes the wrong way :(, but it's also wrong for LPI
# Last 2 are the important ones
X_ORIENTATION_STR: str = "RPI"
"""Orientation string to pass into sitk.DICOMOrientImageFilter to orient X view correctly."""
# First and third are the important ones
Y_ORIENTATION_STR: str = "LPI"
"""Orientation string to pass into sitk.DICOMOrientImageFilter to orient Y view correctly."""
# First 2 are the important ones
Z_ORIENTATION_STR: str = "LPS"
"""Orientation string to pass into sitk.DICOMOrientImageFilter to orient Z view correctly."""

VIEW_TO_ORIENTATION_STR: dict = {
    View.X: X_ORIENTATION_STR,
    View.Y: Y_ORIENTATION_STR,
    View.Z: Z_ORIENTATION_STR,
}
"""Map View enum to its orientation string."""


# Source: https://stackoverflow.com/questions/2536307/decorators-in-the-python-standard-lib-deprecated-specifically
def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used."""

    @functools.wraps(func)
    def new_func(*args, **kwargs):
        warnings.simplefilter("always", DeprecationWarning)  # turn off filter
        warnings.warn(
            "Call to deprecated function {}.".format(func.__name__),
            category=DeprecationWarning,
            stacklevel=2,
        )
        warnings.simplefilter("default", DeprecationWarning)  # reset filter
        return func(*args, **kwargs)

    return new_func


def degrees_to_radians(angle: Union[int, float]) -> float:
    """It's quite simple.

    :param num: A degree measure
    :type num: int or float
    :return: Equivalent radian measure
    :rtype: float"""
    return angle * pi / 180
