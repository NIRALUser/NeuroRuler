"""Some helper functions for image processing."""

import SimpleITK as sitk
import cv2
import numpy as np

# import PyQt6 is fine here but is useless, can't access things from it?
# from PyQt6.QtGui import QImage, QColor breaks GH automated tox tests

try:
    # This is for pytest and normal use
    import src.utils.exceptions as exceptions
except ModuleNotFoundError:
    # This is for processing.ipynb
    import exceptions
from src.utils.constants import NUM_CONTOURS_IN_INVALID_SLICE
import src.utils.settings as settings


# The RV is a np array, not sitk.Image
# because we can't actually use a sitk.Image contour in the program
# To compute arc length, we need a np array
# To overlay the contour on top of the base image in the GUI, we need a np array
def contour(mri_slice: sitk.Image, retranspose: bool = True) -> np.ndarray:
    """Generate the contour of a rotated slice by applying smoothing, Otsu threshold,
    hole filling, and island removal. Return a binary (0|1) numpy
    array with only the points on the contour=1.

    If settings.SMOOTH_BEFORE_RENDERING is True, this function will not re-smooth `mri_slice`
    since it was smoothed in :code:`MRIImage.resample()`.

    :param mri_slice: 2D MRI slice
    :type mri_slice: sitk.Image

    :param retranspose: Whether or not to return a re-transposed numpy array that matches the sitk representation. Defaults to True.
    :type retranspose: bool
    :return: binary (0|1) numpy array with only the points on the contour = 1
    :rtype: np.ndarray"""
    # The cast is necessary, otherwise get sitk::ERROR: Pixel type: 16-bit signed integer is not supported in 2D
    # However, this does throw some weird errors
    # GradientAnisotropicDiffusionImageFilter (0x107fa6a00): Anisotropic diffusion unstable time step: 0.125
    # Stable time step for this image must be smaller than 0.0997431
    if settings.DEBUG and not settings.SMOOTH_BEFORE_RENDERING:
        print('imgproc.contour() smoothed the slice provided to it.')
    smooth_slice: sitk.Image = mri_slice if settings.SMOOTH_BEFORE_RENDERING else sitk.GradientAnisotropicDiffusionImageFilter().Execute(
        sitk.Cast(mri_slice, sitk.sitkFloat64))

    otsu: sitk.Image = sitk.OtsuThresholdImageFilter().Execute(smooth_slice)

    hole_filling: sitk.Image = sitk.BinaryGrindPeakImageFilter().Execute(otsu)

    # BinaryGrindPeakImageFilter has inverted foreground/background 0 and 1, need to invert
    inverted: sitk.Image = sitk.NotImageFilter().Execute(hole_filling)

    largest_component: sitk.Image = select_largest_component(inverted)

    contour: sitk.Image = sitk.BinaryContourImageFilter().Execute(largest_component)

    # GetArrayFromImage returns the transpose of the sitk representation
    contour_np: np.ndarray = sitk.GetArrayFromImage(contour)

    if retranspose:
        return np.transpose(contour_np)
    return contour_np


# Credit: https://discourse.itk.org/t/simpleitk-extract-largest-connected-component-from-binary-image/4958
def select_largest_component(binary_slice: sitk.Image) -> sitk.Image:
    """Remove islands from a binary (0|1) 2D slice. That is, return a binary slice
    containing only the largest connected component.

    :param binary_slice: Binary (0|1) 2D slice
    :type binary_slice: sitk.Image
    :return: Binary (0|1) slice with only the largest connected component
    :rtype: sitk.Image"""
    component_image: sitk.Image = sitk.ConnectedComponent(binary_slice)
    sorted_component_image: sitk.Image = sitk.RelabelComponent(
        component_image, sortByObjectSize=True)
    largest_component_binary_image: sitk.Image = sorted_component_image == 1
    return largest_component_binary_image


# Based on commit a230a6b discussion, may not need to worry about non-square pixels
def length_of_contour(binary_contour_slice: np.ndarray, raise_exception: bool = True) -> float:
    """Given a 2D binary slice, return the arc length of the parent contour.

    cv2 will find all contours if there is more than one. Most valid brain slices have 2 or 3.

    The binary slice passed into this function should be processed by `contour()` to contain
    just one contour (except in edge cases) to guarantee an accurate result.

    This function assumes the contour is a closed curve.

    :param binary_contour_slice: 2D binary (0|1) slice that should be pre-processed by contour() to contain just a single contour.
    :type binary_contour_slice: np.ndarray
    :param raise_exception: Whether or not to raise ComputeCircumferenceOfInvalidSlice.  Defaults to True and should be False only for unit testing purposes.
    :type raise_exception: bool
    :raise exceptions.ComputeCircumferenceOfInvalidSlice: If >= globs.NUM_CONTOURS_IN_INVALID_SLICE contours are detected.
    :return: Arc length of parent contour
    :rtype: float"""

    # contours is an array of contours
    # A single contour, contours[0], looks like [[[122  76]] [[121  77]] [[107  77]] ... [[106  78]]],
    # representing boundary points of the contour
    # contours[1] would be another contour, and so on
    # hierarchy is a list of the same length as contours that provides information about each contour
    # See the documentation for more detail
    contours, hierarchy = cv2.findContours(binary_contour_slice, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    num_contours: int = len(contours)

    if settings.DEBUG:
        print(f'Number of contours detected after processing: {num_contours}')

    if raise_exception and num_contours >= NUM_CONTOURS_IN_INVALID_SLICE:
        raise exceptions.ComputeCircumferenceOfInvalidSlice(len(contours))

    # NOTE: select_largest_component removes all "islands" from the image.
    # But there can still be contours within the largest contour.
    # Most valid brain slices have 2 contours, rarely 3.
    # Assuming there are no islands, contours[0] is always the parent contour.
    # See unit test in test_imgproc.py: test_contours_0_is_always_parent_contour_if_no_islands
    parent_contour: np.ndarray = contours[0]
    # True means we assume the contour is a closed curve.
    arc_length = cv2.arcLength(parent_contour, True)
    return arc_length
