"""Global variables and functions that change throughout program execution, unlike constants.py,
that the user should not be able to modify directly, unlike user_settings.py."""

import SimpleITK as sitk
from pathlib import Path
from src.utils.constants import View

IMAGE_GROUPS: dict[tuple, dict[Path, sitk.Image]] = dict()
"""Mapping from properties tuple to a group of images, where a group of images is a dict[Path, sitk.Image].

Each dictionary of images has the same properties, as defined by img_helpers.get_properties()

{
    properties tuple: dict[Path, sitk.Image]
    properties tuple: dict[Path, sitk.Image]
    ...
}

The IMAGE_DICT group is by default the 0'th group in this list. If we want to be able to change batches,
we can change CURR_BATCH_INDEX.

IMAGE_GROUPS[list(IMAGE_GROUPS.keys())[0]] gets the first group of images (dict maintains insertion order
in Python 3.7+, https://mail.python.org/pipermail/python-dev/2017-December/151283.html)."""

IMAGE_DICT: dict[Path, sitk.Image] = dict()
"""The current (i.e., loaded in GUI) group of images in IMAGE_GROUPS.

Since Python 3.7+, dicts maintain insertion order. Therefore, we can use CURR_IMAGE_INDEX for retrieval and deletion.

Use list(IMAGE_DICT.keys())[i] to return the i'th key in the dict, which can also index into the dict.
Not sure about this operation's speed, but it's used only
in the GUI for insertion and deletion operations, should be fine.

All images in the dictionary have matching properties, as defined by mri_image.get_properties.
This is due to the setup of IMAGE_GROUPS."""

CURR_IMAGE_INDEX: int = 0
"""Image of the current image in the loaded batch of images, which is a dict[Path, sitk.Image].

You should probably use the helper functions in img_helpers instead of this (unless you're writing helper
functions)."""

CURR_BATCH_INDEX: int = 0
"""TODO: Not implemented (idk if useful yet). For now, this is just 0 throughout the program.

It's meant to be the index of the current group/batch in IMAGE_GROUPS.
Indexing into IMAGE_GROUPS using this number
(IMAGE_GROUPS[list(IMAGE_GROUPS.keys())[CURR_BATCH_INDEX]])
will result in a dict of images.

Remember to update the center of EULER_3D_TRANSFORM if updating batch index!"""

READER: sitk.ImageFileReader = sitk.ImageFileReader()
"""Global `sitk.ImageFileReader`."""

EULER_3D_TRANSFORM: sitk.Euler3DTransform = sitk.Euler3DTransform()
"""Global sitk.Euler3DTransform for 3D rotations.

It is assumed that all currently loaded images have the same center of rotation. The center won't change
for the currently loaded batch of images.

Switching the batch will change the center. Make sure to set it. Or encapsulate an Euler3DTransform for each batch?

Rotation values are the global rotation values in global_vars.py."""

THETA_X: int = 0
"""In degrees"""
THETA_Y: int = 0
"""In degrees"""
THETA_Z: int = 0
"""In degrees"""
SLICE: int = 0
"""0-indexed"""

OTSU_THRESHOLD_FILTER: sitk.OtsuThresholdImageFilter = sitk.OtsuThresholdImageFilter()
"""Global OTSU filter"""
BINARY_THRESHOLD_FILTER: sitk.BinaryThresholdImageFilter = (
    sitk.BinaryThresholdImageFilter()
)
"""Global Binary filter"""
LOWER_THRESHOLD: int = 100
"""Threshold option for binary threshold"""
UPPER_THRESHOLD: int = 200
"""Threshold option for binary threshold"""
INSIDE_VALUE: int = 0
"""Threshold option for inside color"""
OUTSIDE_VALUE: int = 1
"""Threshold option for outside color"""

OTSU_THRESHOLD_FILTER: sitk.OtsuThresholdImageFilter = sitk.OtsuThresholdImageFilter()
"""Global OTSU filter"""
BINARY_THRESHOLD_FILTER: sitk.BinaryThresholdImageFilter = (
    sitk.BinaryThresholdImageFilter()
)
"""Global Binary filter"""
LOWER_THRESHOLD: int = 100
"""Threshold option for binary threshold"""
UPPER_THRESHOLD: int = 200
"""Threshold option for binary threshold"""
INSIDE_VALUE: int = 0
"""Threshold option for inside color"""
OUTSIDE_VALUE: int = 1
"""Threshold option for outside color"""

X_CENTER: int = 0
"""Used for changing views."""

Y_CENTER: int = 0
"""Used for changing views."""

VIEW: View = View.Z
"""Current view."""

SMOOTHING_FILTER: sitk.GradientAnisotropicDiffusionImageFilter = (
    sitk.GradientAnisotropicDiffusionImageFilter()
)
"""Global sitk.GradientAnisotropicDiffusionImageFilter for image smoothing.

See https://slicer.readthedocs.io/en/latest/user_guide/modules/gradientanisotropicdiffusion.html for more information."""

CONDUCTANCE_PARAMETER: float = 3.0
"""Smoothing option.

Conductance controls the sensitivity of the conductance term.
As a general rule, the lower the value, the more strongly the filter preserves edges.
A high value will cause diffusion (smoothing) across edges.
Note that the number of iterations controls how much smoothing is done within regions bounded by edges."""

SMOOTHING_ITERATIONS: int = 5
"""Smoothing option.

The more iterations, the more smoothing. Each iteration takes the same amount of time.
If it takes 10 seconds for one iteration, then it will take 100 seconds for 10 iterations.
Note that the conductance controls how much each iteration smooths across edges."""

TIME_STEP: float = 0.0625
"""Smoothing option.

The time step depends on the dimensionality of the image.
In Slicer the images are 3D and the default (.0625) time step will provide a stable solution."""

ORIENT_FILTER: sitk.DICOMOrientImageFilter = sitk.DICOMOrientImageFilter()
"""Global sitk.DICOMOrientImageFilter for orienting images.

See https://simpleitk.org/doxygen/latest/html/classitk_1_1simple_1_1DICOMOrientImageFilter.html#details
and the orientation strings in constants.py. Use ITK-SNAP for the orientations that we copy."""


SETTINGS_VIEW_ENABLED: bool = True
"""Whether the user is able to adjust settings (settings screen) or not
(circumference and contoured image screen).

Used in src/GUI/main.py"""


def main():
    """For testing."""
    pass


if __name__ == "__main__":
    main()
