"""Some helper functions for image processing."""

import SimpleITK as sitk
import numpy as np
import cv2
from typing import Union

try:
    # This is for pytest and normal use
    import src.utils.exceptions as exceptions
except ModuleNotFoundError:
    # This is for processing.ipynb
    import exceptions
from src.utils.globs import deprecated, NUM_CONTOURS_IN_INVALID_SLICE
import src.utils.settings as settings


# The RV is a np array, not sitk.Image, because we can't actually use a sitk.Image contour in the program, besides for testing purposes
# To compute arc length, we need a np array
# To overlay the contour on top of the base image in the GUI, we need a np array
def contour(mri_slice: sitk.Image, retranspose: bool = True) -> np.ndarray:
    """Given a rotated slice, apply smoothing, Otsu threshold, hole filling, and island removal. Return a binary (0|1) numpy
    array with only the points on the contour=1.

    Parameter
    --------
    mri_slice: sitk.Image
        2D MRI slice.

        If settings.SMOOTH_BEFORE_RENDERING is True, then this function will not apply smoothing to mri_slice.

        Else, it'll operate on a smoothed copy of the slice.

    retranspose: bool
        sitk.GetArrayFromImage returns a numpy array that's the transpose of the sitk representation.

        If True (default), this function will return a re-transposed result to match the sitk representation.

    Return value
    ------------
    binary (0|1) numpy array with only the points on the contour = 1"""
    # The cast is necessary, otherwise get sitk::ERROR: Pixel type: 16-bit signed integer is not supported in 2D
    # However, this does throw some weird errors
    # GradientAnisotropicDiffusionImageFilter (0x107fa6a00): Anisotropic diffusion unstable time step: 0.125
    # Stable time step for this image must be smaller than 0.0997431
    if not settings.SMOOTH_BEFORE_RENDERING:
        print('contour() smoothed the slice provided to it')
    smooth_slice: sitk.Image = mri_slice if settings.SMOOTH_BEFORE_RENDERING else sitk.GradientAnisotropicDiffusionImageFilter().Execute(
        sitk.Cast(mri_slice, sitk.sitkFloat64))

    otsu: sitk.Image = sitk.OtsuThresholdImageFilter().Execute(smooth_slice)

    hole_filling: sitk.Image = sitk.BinaryGrindPeakImageFilter().Execute(otsu)

    # BinaryGrindPeakImageFilter has inverted foreground/background 0 and 1, need to invert
    inverted: sitk.Image = sitk.NotImageFilter().Execute(hole_filling)

    largest_component: sitk.Image = select_largest_component(inverted)

    contour: sitk.Image = sitk.BinaryContourImageFilter().Execute(largest_component)

    contour_np: np.ndarray = sitk.GetArrayFromImage(contour)

    if retranspose:
        return np.transpose(contour_np)
    return contour_np


# Credit: https://discourse.itk.org/t/simpleitk-extract-largest-connected-component-from-binary-image/4958
def select_largest_component(binary_slice: sitk.Image) -> sitk.Image:
    """Remove islands.

    Given a binary (0|1) binary slice, return a binary slice containing only the largest connected component."""
    component_image: sitk.Image = sitk.ConnectedComponent(binary_slice)
    sorted_component_image: sitk.Image = sitk.RelabelComponent(
        component_image, sortByObjectSize=True)
    largest_component_binary_image: sitk.Image = sorted_component_image == 1
    return largest_component_binary_image


# Based on commit a230a6b discussion, may not need to worry about non-square pixels
def length_of_contour(binary_contour_slice: np.ndarray, raise_exception: bool = True) -> float:
    """Given a 2D binary (0|1 or 0|255) slice containing a single contour, return the arc length of the parent contour.

    This function assumes the contour is a closed curve.

    Parameters
    ---------
    contour_slice: np.ndarray
        This needs to be a 2D binary (0|1 or 0|255, doesn't make a difference) slice containing a contour.
    
    raise_exception: bool
        If True (default), will raise ComputeCircumferenceOfInvalidSlice when too many contours are detected, indicating the slice is invalid
        
        Should be set to False only for unit tests"""
    contours, hierarchy = cv2.findContours(binary_contour_slice, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if raise_exception and len(contours) >= NUM_CONTOURS_IN_INVALID_SLICE:
        raise exceptions.ComputeCircumferenceOfInvalidSlice(len(contours))

    # NOTE: select_largest_component removes all "islands" from the image.
    # But there can still be contours within the largest contour.
    # Most valid brain slices have 2 contours, rarely 3.
    # Assuming there are no islands, contours[0] is always the parent contour.
    # See unit test in test_imgproc.py: test_contours_0_is_always_parent_contour_if_no_islands
    parent_contour: np.ndarray = contours[0]
    arc_length = cv2.arcLength(parent_contour, True)
    return arc_length


def degrees_to_radians(num: Union[int, float]) -> float:
    return num * np.pi / 180
