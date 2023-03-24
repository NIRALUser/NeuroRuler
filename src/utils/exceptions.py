"""Custom exceptions, most of which aren't actually in use rn."""

from pathlib import Path
from src.utils.constants import deprecated, ROTATION_MAX, ROTATION_MIN


# TODO: Make __init__ accept theta_x, theta_y, theta_z, slice_num as parameters to display those to the user?
# Probably not necessary because those will be displayed in the GUI.
class ComputeCircumferenceOfInvalidSlice(Exception):
    """User attempted to compute circumference of an invalid slice.

    We detect this by noticing that the number of contours in the slice >= globs.NUM_CONTOURS_IN_INVALID_SLICE
    AFTER processing (threshold, select largest component, etc.) in src.utils.imgproc.contour().

    Most valid brain slices have only 2 or 3 detectable contours.

    Change the number in global_vars.py, then run `pytest` and examine slices given by settings in
    tests/noise_vals.txt. Some valid slices have 6 or 7 contours.

    See NIFTI file (0, 0, 0, 151) for a valid slice with 9 contours. 9 seems like a good limit.
    """

    def __init__(self, num_contours):
        self.message = (
            f"You attempted to compute the circumference of an invalid brain slice. After processing, contours detected: {num_contours}\n"
            f"Likely noise or otherwise not a valid brain slice."
        )
        super().__init__(self.message)


@deprecated
class RemoveFromEmptyList(Exception):
    """Self-explanatory."""

    def __init__(self):
        self.message = f"You attempted to remove an image from an empty list of images."
        super().__init__(self.message)


@deprecated
class RemoveFromListOfLengthOne(Exception):
    """If the list becomes empty, there's no image to render, which might cause an `IndexError`."""

    def __init__(self):
        self.message = f"You attempted to remove an image from a list of size 1 (i.e., the list would become empty after the delete)."
        super().__init__(self.message)


@deprecated
class RemoveAtInvalidIndex(Exception):
    """The error message accounts for the user seeing a 1-indexed list."""

    def __init__(self, index: int):
        self.message = f"You attempted to remove an image at index {index + 1}, which doesn't exist in the list of images."
        super().__init__(self.message)


@deprecated
class UnexpectedNegativeNum(Exception):
    def __init__(self):
        self.message = f""
        super().__init__(self.message)


class ArraysDifferentShape(Exception):
    def __init__(self):
        self.message = f"Ran into two arrays of different shape when it was necessary that they be of the same shape."
        super().__init__(self.message)


class InvalidColor(Exception):
    def __init__(self, color: str):
        self.message = f"Invalid color {color} specified."
        super().__init__(self.message)


class DuplicateFilepathsInMRIImageList(Exception):
    def __init__(self, paths: set[Path]):
        self.message = f"Duplicate file path(s) {set(map(str, paths))} were added to the MRIImageList."
        super().__init__(self.message)


# sitk can handle any rotation, but we should enforce -90 and 90 bounds.
class RotationOutOfBounds(Exception):
    def __init__(self, theta: int, axis: str):
        self.message = f"{axis} rotation value {theta} out of bounds. Min rotation value is {ROTATION_MIN} degrees, and max is {ROTATION_MAX}."
        super().__init__(self.message)


class DoesNotMatchModelImage(Exception):
    def __init__(self, path: Path):
        self.message = f"Newly added image with path {path} has properties (e.g., dimensions, pixel spacing, etc.) that do not match the first image in the list."
        super().__init__
