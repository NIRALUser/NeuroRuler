"""Global variables that change throughout program execution."""

import SimpleITK as sitk
from pathlib import Path
from typing import Any
from NeuroRuler.utils.constants import View

IMAGE_DICT: dict[Path, sitk.Image] = dict()
"""The group of images that have been loaded.

Since Python 3.7+, dicts maintain insertion order. Therefore, we can use CURR_IMAGE_INDEX for retrieval and deletion.

Use list(IMAGE_DICT.keys())[i] to return the i'th key in the dict, which can also index into the dict.
Not sure about this operation's speed, but it's used only
in the GUI for insertion and deletion operations, should be fine.

All images in the dictionary have matching properties, as defined by mri_image.get_properties."""

CURR_IMAGE_INDEX: int = 0
"""Image of the current image in the loaded batch of images, which is a dict[Path, sitk.Image].

You should probably use the helper functions in img_helpers instead of this (unless you're writing helper
functions)."""

READER: sitk.ImageFileReader = sitk.ImageFileReader()
"""Global ``sitk.ImageFileReader``."""

ORIENT_FILTER: sitk.DICOMOrientImageFilter = sitk.DICOMOrientImageFilter()
"""Global sitk.DICOMOrientImageFilter for orienting images.

See https://simpleitk.org/doxygen/latest/html/classitk_1_1simple_1_1DICOMOrientImageFilter.html#details
and the orientation strings in constants.py. Use ITK-SNAP for the orientations that we copy."""
VIEW: View = View.Z
"""Current view in the GUI."""
X_CENTER: int = 0
"""Used for changing views."""
Y_CENTER: int = 0
"""Used for changing views."""

EULER_3D_TRANSFORM: sitk.Euler3DTransform = sitk.Euler3DTransform()
"""Global sitk.Euler3DTransform for 3D rotations."""
THETA_X: int = 0
"""In degrees"""
THETA_Y: int = 0
"""In degrees"""
THETA_Z: int = 0
"""In degrees"""
SLICE: int = 0
"""0-indexed"""

SMOOTHING_FILTER: sitk.GradientAnisotropicDiffusionImageFilter = (
    sitk.GradientAnisotropicDiffusionImageFilter()
)
"""Global sitk.GradientAnisotropicDiffusionImageFilter for image smoothing.

See https://slicer.readthedocs.io/en/latest/user_guide/modules/gradientanisotropicdiffusion.html
for more information."""
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
In Slicer, the images are 3D and the default (.0625) time step will provide a stable solution."""

OTSU_THRESHOLD_FILTER: sitk.OtsuThresholdImageFilter = sitk.OtsuThresholdImageFilter()
"""Global Otsu threshold filter."""

BINARY_THRESHOLD_FILTER: sitk.BinaryThresholdImageFilter = (
    sitk.BinaryThresholdImageFilter()
)
"""Global binary threshold filter."""
LOWER_BINARY_THRESHOLD: float = 0.0
"""Threshold option for binary threshold."""
UPPER_BINARY_THRESHOLD: float = 200.0
"""Threshold option for binary threshold."""
