"""Custom exceptions."""

from NeuroRuler.utils.constants import (
    deprecated,
    ROTATION_MAX,
    ROTATION_MIN,
    JSON_GUI_CONFIG_PATH,
)


class ComputeCircumferenceOfInvalidSlice(Exception):
    """User attempted to compute circumference of an invalid slice.

    We detect this by noticing that the number of contours in the slice >= global_vars.NUM_CONTOURS_IN_INVALID_SLICE
    AFTER processing (threshold, select largest component, etc.) in NeuroRuler.utils.imgproc.contour().

    Most valid brain slices have only 2 or 3 detectable contours.

    Change the number in global_vars.py, then run ``pytest`` and examine slices given by settings in
    tests/noise_vals.txt. Some valid slices have 6 or 7 contours.

    See NIFTI file (0, 0, 0, 151) for a valid slice with 9 contours. 9 seems like a good limit.
    """

    def __init__(self, num_contours):
        self.message = (
            f"You attempted to compute the circumference of something that isn't a valid brain slice. After processing, contours detected was {num_contours}\n"
            f"Likely just noise or otherwise not a valid brain slice."
        )
        super().__init__(self.message)


class ArraysDifferentShape(Exception):
    def __init__(self):
        self.message = f"Ran into two arrays of different shape when it was necessary that they be of the same shape."
        super().__init__(self.message)


class InvalidColor(Exception):
    def __init__(self, color: str):
        self.message = f"Invalid color {color} specified."
        super().__init__(self.message)


class RotationOutOfBounds(Exception):
    """Should never be encountered in the GUI because our sliders have min and max.
    This will be for CLI arguments."""

    def __init__(self, theta: int, axis: str):
        self.message = f"{axis} rotation value {theta} out of bounds. Min rotation value is {ROTATION_MIN} degrees, and max is {ROTATION_MAX}."
        super().__init__(self.message)


class InvalidJSONField(Exception):
    def __init__(self, field: str, expected: str):
        """``field`` is the name of the invalid field

        ``expected`` is some information about what the expected value should be"""
        self.message = f"The field {field} in {JSON_GUI_CONFIG_PATH} has an invalid type or value.\nExpected: {expected}"
        super().__init__(self.message)
