"""Helper functions for image processing. Essentially, the main algorithm."""

import SimpleITK as sitk
import cv2
import numpy as np

import src.utils.exceptions as exceptions
from src.utils.constants import NUM_CONTOURS_IN_INVALID_SLICE
import src.utils.user_settings as settings
from src.utils.img_helpers import get_curr_spacing


# The RV is a np array, not sitk.Image
# because we can't actually use a sitk.Image contour in the rest of the process
# To compute arc length, we need a np array
# To overlay the contour on top of the base image in the GUI, we need a np array
def contour(mri_slice: sitk.Image, retranspose: bool = False) -> np.ndarray:
    """Generate the contour of a 2D slice by applying smoothing, Otsu threshold,
    hole filling, and island removal (remove largest component). Return a binary (0|1) numpy
    array with only the points on the contour=1.

    Calls sitk.GetArrayFromImage() at the end, which will return the transpose of the sitk.Image.
    retranspose defaults to False to match images viewed in ITK-SNAP (radiological conventions).

    If user_settings.SMOOTH_BEFORE_RENDERING is True, this function will not re-smooth `mri_slice`
    since it was smoothed in :code:`img_helpers.curr_rotated_slice()`.

    :param mri_slice: 2D MRI slice
    :type mri_slice: sitk.Image
    :param retranspose: Whether to return a re-transposed ndarray. Defaults to False.
    :type retranspose: bool
    :return: binary (0|1) numpy array with only the points on the contour = 1
    :rtype: np.ndarray"""
    if settings.DEBUG and not settings.SMOOTH_BEFORE_RENDERING:
        print(
            "imgproc.contour() smoothed the slice provided to it AFTER rendering (i.e., user does not see smoothed slice)."
        )
    # The cast is necessary, otherwise get sitk::ERROR: Pixel type: 16-bit signed integer is not supported in 2D
    # However, this does throw some weird errors
    # GradientAnisotropicDiffusionImageFilter (0x107fa6a00): Anisotropic diffusion unstable time step: 0.125
    # Stable time step for this image must be smaller than 0.0997431
    smooth_slice: sitk.Image = (
        mri_slice
        if settings.SMOOTH_BEFORE_RENDERING
        else sitk.GradientAnisotropicDiffusionImageFilter().Execute(
            sitk.Cast(mri_slice, sitk.sitkFloat64)
        )
    )

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
    """Remove islands from a binary (0|1) 2D slice. Return a binary slice
    containing only the largest connected component.

    :param binary_slice: Binary (0|1) 2D slice
    :type binary_slice: sitk.Image
    :return: Binary (0|1) slice with only the largest connected component
    :rtype: sitk.Image"""
    component_image: sitk.Image = sitk.ConnectedComponent(binary_slice)
    sorted_component_image: sitk.Image = sitk.RelabelComponent(
        component_image, sortByObjectSize=True
    )
    largest_component_binary_image: sitk.Image = sorted_component_image == 1
    return largest_component_binary_image


# Based on commit a230a6b discussion, may not need to worry about non-square pixels
def length_of_contour(
    binary_contour_slice: np.ndarray, raise_exception: bool = True
) -> float:
    """Given a 2D binary slice, return the arc length of the parent contour.

    cv2 will find all contours if there is more than one. Most valid brain slices have 2 or 3.

    The binary slice passed into this function should be processed by `contour()` to contain
    just one contour (except in edge cases that we don't need to worry about) to guarantee an accurate result.

    This function assumes the contour is a closed curve.

    :param binary_contour_slice: 2D binary (0|1) slice that should be pre-processed by contour() to contain just a single contour.
    :type binary_contour_slice: np.ndarray
    :param raise_exception: Whether or not to raise ComputeCircumferenceOfInvalidSlice.  Defaults to True and should be False only for unit testing purposes.
    :type raise_exception: bool
    :raise exceptions.ComputeCircumferenceOfInvalidSlice: If >= constants.NUM_CONTOURS_IN_INVALID_SLICE contours are detected.
    :return: Arc length of parent contour
    :rtype: float"""

    # contours is an array of contours
    # A single contour, contours[0], looks like [[[122  76]] [[121  77]] [[107  77]] ... [[106  78]]],
    # representing boundary points of the contour
    # contours[1] would be another contour, and so on
    # hierarchy is a list of the same length as contours that provides information about each contour
    # See the documentation for more detail
    contours, hierarchy = cv2.findContours(
        binary_contour_slice, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )
    num_contours: int = len(contours)

    if settings.DEBUG:
        print(
            f"Number of contours detected after processing: {num_contours} (in imgproc.length_of_contour())"
        )

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


# TODO: Not sure if x and y are in the right order here.
# sitk.GetArrayFromImage returns transpose...
def length_of_contour_with_spacing(
    binary_contour_slice: np.ndarray, x_spacing: float, y_spacing: float
) -> float:
    """Given a 2D binary slice (i.e., RV of contour()), return arc length of parent contour,
    accounting for x_spacing and y_spacing values.

    The binary slice passed into this function should be processed by `contour()`
    to guarantee an accurate result.

    Slices for which circumference is calculated are always parallel to z,
    so the z spacing value is always ignored.

    This function assumes the contour is a closed curve.

    TODO: Not sure if x and y are in the right order here.

    :param binary_contour_slice:
    :type binary_contour_slice: np.ndarray
    :param x_spacing:
    :type x_spacing: float
    :param y_spacing:
    :type y_spacing: float
    :raise: exceptions.ComputeCircumferenceOfInvalidSlice if contours detected >= constants.NUM_CONTOURS_IN_INVALID_SLICE
    :return: arc length of parent contour
    :rtype: float
    """
    contours, hierarchy = cv2.findContours(
        binary_contour_slice, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )

    num_contours: int = len(contours)
    if settings.DEBUG:
        print(
            f"Number of contours detected after processing: {num_contours} (in imgproc.length_of_contour())"
        )

    if num_contours >= NUM_CONTOURS_IN_INVALID_SLICE:
        raise exceptions.ComputeCircumferenceOfInvalidSlice(num_contours)

    parent_contour: np.ndarray = contours[0]

    arc_length: float = 0
    for i in range(len(parent_contour) - 1):
        # contours[0] would return [[x y]], so need to do an additional [0] index to just get [x y]
        arc_length += distance_2d_with_spacing(
            parent_contour[i][0], parent_contour[i + 1][0], x_spacing, y_spacing
        )
    # Get distance between first and last points
    arc_length += distance_2d_with_spacing(
        parent_contour[-1][0], parent_contour[0][0], x_spacing, y_spacing
    )
    return arc_length


def distance_2d_with_spacing(x, y, x_spacing: float, y_spacing: float) -> float:
    """Return the distance between two 2D iterables (list or tuple) given x and y spacing values.

    :param x: 2D point
    :type x: iterable
    :param y: 2D point
    :type y: iterable
    :param x_spacing:
    :type x_spacing: float
    :param y_spacing:
    :type y_spacing: float"""
    assert len(x) == 2 and len(y) == 2
    return np.sqrt((x_spacing * (x[0] - x[1])) ** 2 + (y_spacing * (y[0] - y[1])) ** 2)
