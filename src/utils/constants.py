"""Constant values and functions. DO NOT MUTATE ANY VARIABLE IN THIS FILE!

This file should never import any module in this repo to avoid any circular import problems.

It holds values that will never change after program setup (i.e., during execution), unlike global_vars.py.
But things like THEMES can go here. Specifically, THEMES is a mutable set, but it will never
change after initial setup.

No values here should be modifiable by the user, unlike user_settings.py."""

from pathlib import Path
import warnings
import functools
from numpy import pi
from typing import Union

ROTATION_MIN: int = -90
"""In degrees"""
ROTATION_MAX: int = 90
"""In degrees"""

SUPPORTED_EXTENSIONS: tuple = ("*.nii.gz", "*.nii", "*.nrrd")
"""File formats supported. Must be a subset of the file formats supported by SimpleITK."""
EXAMPLE_DATA_DIR: Path = Path("ExampleData")
"""Directory for storing example data."""

THEME_DIR: Path = Path("src") / "GUI" / "themes"
"""themes/ directory where .qss stylesheets and resources.py files are stored."""
THEMES: set[str] = set()
"""List of themes, i.e. the names of the directories in THEME_DIR."""
if len(list(THEME_DIR.glob("*"))) != 0:
    for path in THEME_DIR.iterdir():
        if path.is_dir():
            THEMES.add(path.name)
else:
    # TODO: Without this, autodocumentation will crash. Is there a better way around this?
    print(
        f"No themes discovered in {str(THEME_DIR)}. Make sure to run from .../HeadCircumferenceTool ."
    )

HCT_MAIN_COLOR: str = "b55162"
"""HCT's copyrighted color :P

The pink-ish color used in the midterm presentation. Imperceptibly different from the website logo color.

Shouldn't use this much if we still use BreezeStyleSheet themes, in which each theme has a unique
theme color.

This is more here for reference than actual use in the program."""

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
"""For floats, number of digits n to round to, i.e. round(float, n)."""


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
