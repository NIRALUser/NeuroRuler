"""Global variables and functions that change throughout program execution, unlike constants.py,
that the user should not be able to modify directly, unlike user_settings.py.

Can run this file as module (python -m src.utils.globs) to test stuff."""

import warnings
import functools
from sortedcontainers import SortedDict
import SimpleITK as sitk

IMAGE_DICT: SortedDict = SortedDict()
"""Global mapping of unique and sorted Path to sitk.Image"""

INDEX: int = 0
"""Image of the current image in global IMAGE_DICT"""

READER: sitk.ImageFileReader = sitk.ImageFileReader()
"""Global `sitk.ImageFileReader`."""

MODEL_IMAGE: sitk.Image = sitk.Image()

EULER_3D_TRANSFORM: sitk.Euler3DTransform = sitk.Euler3DTransform()

THETA_X: int = 0
"""In degrees"""
THETA_Y: int = 0
"""In degrees"""
THETA_Z: int = 0
"""In degrees"""
SLICE: int = 0
"""0-indexed"""


# Autodocumentation throws an error when this isn't here... which file still imports deprecated from globs???
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


def main():
    """For testing."""
    pass


if __name__ == "__main__":
    main()
