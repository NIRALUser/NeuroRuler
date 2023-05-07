"""Constant values and functions. DO NOT MUTATE ANY VARIABLE IN THIS FILE FROM OUTSIDE OF THIS FILE!

This file should not import any module in this repo to avoid circular imports."""

import re
from pathlib import Path
import warnings
import functools
from screeninfo import get_monitors, ScreenInfoError
from numpy import pi
from typing import Union
from enum import Enum
import pkg_resources

OUTPUT_DIR: Path = Path("output")
"""Directory for storing output."""
if not OUTPUT_DIR.exists():
    OUTPUT_DIR.mkdir()

JSON_CLI_CONFIG_PATH: Path = Path("cli_config.json")
"""Settings that configure cli_settings.py.

In CLI.__init__.py cli(), will be created using package's ``cli_config.json`` if it doesn't already exist."""
JSON_GUI_CONFIG_PATH: Path = Path("gui_config.json")
"""Settings that configure gui_settings.py.

In GUI.__init__.py gui(), will be created using package's ``cli_config.json`` if it doesn't already exist."""

DATA_DIR: Path = Path("data")

SUPPORTED_IMAGE_EXTENSIONS: tuple = ("*.nii.gz", "*.nii", "*.nrrd")
"""Image file formats supported. Must be a subset of the file formats supported by SimpleITK."""
SUPPORTED_IMAGE_EXTENSIONS_REGEX: tuple[re.Pattern, ...] = tuple(
    map(
        re.compile,
        tuple(
            "^" + extension.replace(".", "\\.").replace("*", ".*") + "$"
            for extension in SUPPORTED_IMAGE_EXTENSIONS
        ),
    )
)
"""Tuple of ``re.Pattern`` for supported image extensions."""

THEME_DIR: Path = Path("NeuroRuler") / "GUI" / "themes"
"""themes/ directory where .qss stylesheets and resources.py files are stored."""
if not THEME_DIR.exists():
    try:
        THEME_DIR = Path(pkg_resources.resource_filename("NeuroRuler.GUI", "themes"))
    # This will occur on circular import, which will occur when running
    # from NeuroRuler.CLI import CLI
    # but CLI doesn't care about THEME_DIR
    # This is a janky way to avoid circular import
    except ImportError:
        pass

THEMES: list[str] = []
"""List of themes, i.e. the names of the directories in THEME_DIR."""

# Without this, autodocumentation might crash
# THEME_DIR obviously exists at this point, except maybe in autodocumentation code
if THEME_DIR.exists():
    for path in THEME_DIR.iterdir():
        if path.is_dir():
            THEMES.append(path.name)
    THEMES = sorted(THEMES)
else:
    pass


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
    """Self-explanatory"""

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
"""Maps the value of ``xyzt_units`` of the metadata of a NIfTI file to physical meaning.

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
ORIENTATION_STRINGS: tuple[str, str, str] = (
    X_ORIENTATION_STR,
    Y_ORIENTATION_STR,
    Z_ORIENTATION_STR,
)
"""(X_ORIENTATION_STR, Y_ORIENTATION_STR, Z_ORIENTATION_STR)

Intended to be indexed using View.X.value, View.Y.value, and View.Z.value."""

PRIMARY_MONITOR_DIMENSIONS: tuple[int, int] = (500, 500)
"""Set to user's primary monitor's dimensions. 500, 500 are dummy values"""

try:
    for monitor in get_monitors():
        if monitor.is_primary:
            PRIMARY_MONITOR_DIMENSIONS = (monitor.width, monitor.height)
            break
except ScreenInfoError:
    # This will occur in GH automated tests.
    pass


MESSAGE_TO_SHOW_IF_UNITS_NOT_FOUND: str = "millimeters (mm)"
"""We assume units are millimeters if we can't find units in metadata"""


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


def get_path_stem(path: Path) -> str:
    """Get true stem of ``path``.

    E.g., stem of ``a.nii`` is ``a``, and stem of ``a.nii.gz`` is also ``a``.

    Note that ``Path('a.nii.gz').stem`` is ``'a.nii'``, not expected in this project.

    :param path:
    :type path: Path
    :return: True stem of path
    :rtype: str"""
    return path.stem.split(".")[0]
