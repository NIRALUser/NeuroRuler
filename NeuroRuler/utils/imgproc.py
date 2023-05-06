"""Helper functions for image processing. Main algorithm."""

import SimpleITK as sitk
import cv2
import numpy as np

import NeuroRuler.utils.exceptions as exceptions
from NeuroRuler.utils.constants import (
    NUM_CONTOURS_IN_INVALID_SLICE,
    ThresholdFilter,
    BinaryColor,
)
import NeuroRuler.utils.gui_settings as settings
from NeuroRuler.utils.global_vars import (
    SMOOTHING_FILTER,
    OTSU_THRESHOLD_FILTER,
    BINARY_THRESHOLD_FILTER,
)

NUM_PIXELS_TO_CHECK_ON_EACH_EDGE_FOR_BACKGROUND_COLOR_DETECTION: int = 25
"""Roughly this many pixels are checked along the top, bottom, left, and right edges of the image."""
MAX_NUM_MISMATCHED_PIXELS_FOR_BACKGROUND_COLOR_DETECTION: int = 3
"""At most this many edge pixels can be different from the pixel at (0, 0)."""


# The RV is a np array, not sitk.Image
# because we can't actually use a sitk.Image contour in the rest of the process
# To compute arc length, we need a np array
# To overlay the contour on top of the base image in the GUI, we need a np array
def contour(
    img_2d: sitk.Image, threshold_filter: ThresholdFilter = ThresholdFilter.Otsu
) -> np.ndarray:
    r"""Generate the contour of a 2D slice by applying smoothing, Otsu threshold or binary threshold,
    hole filling, and island removal (select largest component). Return a binary (0|1) numpy
    array with only the points within the contour=1.

    Calls sitk.GetArrayFromImage() at the end, which will return the transpose of the sitk.Image.
    Consider whether to re-transpose the result or not.

    :param img_2d:
    :type img_2d: sitk.Image
    :param threshold_filter: ThresholdFilter.Otsu or ThresholdFilter.Binary. Defaults to ThresholdFilter.Otsu
    :type threshold_filter: ThresholdFilter
    :return: binary (0|1) numpy array with only the points on the contour = 1
    :rtype: np.ndarray"""
    smooth_slice: sitk.Image = SMOOTHING_FILTER.Execute(
        sitk.Cast(img_2d, sitk.sitkFloat64)
    )

    if threshold_filter == ThresholdFilter.Otsu:
        # This always results in fg = 0 (black), bg = 1 (white)
        thresholded: sitk.Image = OTSU_THRESHOLD_FILTER.Execute(smooth_slice)
    else:
        # This sometimes results in fg = 0 (black), bg = 1 (white)
        # other times fg = 1 (white), bg = 0 (black)
        # Depends on the lower and upper threshold settings
        thresholded: sitk.Image = BINARY_THRESHOLD_FILTER.Execute(smooth_slice)
        if (
            background_color_of_binary_thresholded_slice(thresholded)
            == BinaryColor.Black
        ):
            thresholded = sitk.NotImageFilter().Execute(thresholded)

    # Image needs to be inverted here (i.e., brain 0 black and background 1 white)
    # for BinaryGrindPeakImageFilter to work
    hole_filling: sitk.Image = sitk.BinaryGrindPeakImageFilter().Execute(thresholded)

    # BinaryGrindPeakImageFilter results in inverted foreground/background 0 and 1, need to invert
    inverted: sitk.Image = sitk.NotImageFilter().Execute(hole_filling)

    largest_component: sitk.Image = select_largest_component(inverted)

    contour: sitk.Image = sitk.BinaryContourImageFilter().Execute(largest_component)

    # GetArrayFromImage returns the transpose of the sitk representation
    return sitk.GetArrayFromImage(contour)


# Credit: https://discourse.itk.org/t/simpleitk-extract-largest-connected-component-from-binary-image/4958
def select_largest_component(binary_slice: sitk.Image) -> sitk.Image:
    r"""Remove islands from a binary (0|1) 2D slice. Return a binary slice
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


def length_of_contour(
    binary_contour_slice: np.ndarray, raise_exception: bool = True
) -> float:
    r"""Given a 2D binary slice, return the arc length of the parent contour.

    ``cv2.findContours`` will find all contours if there is more than one. Most valid brain slices have 2 or 3.

    The binary slice passed into this function should be processed by ``contour()``
    (i.e., hole-filling, island removal, threshold, etc.)
    to contain just one contour (except in edge cases that we don't need to worry about)
    to guarantee an accurate result.

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


def length_of_contour_with_spacing(
    binary_contour_slice: np.ndarray, x_spacing: float, y_spacing: float
) -> float:
    r"""Given a 2D binary slice (i.e., RV of contour()), return arc length of parent contour,
    accounting for x_spacing and y_spacing values.
    MAKE SURE x_spacing and y_spacing values are passed in the correct order!
    The binary slice passed into this function should be processed by ``contour()``
    to guarantee an accurate result.
    Slices for which circumference is calculated are always parallel to z,
    so the z spacing value is always ignored.
    This function assumes the contour is a closed curve.

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
        # TC89_L1 works better than SIMPLE
        # That is, when (a, a, a) pixel spacing image is converted to (a, b, c) pixel spacing via Slicer,
        # The arc length is closer to the (a, a, a) arc length if using TC89_L1 than when using SIMPLE
        binary_contour_slice,
        cv2.RETR_TREE,
        cv2.CHAIN_APPROX_TC89_L1,
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


def distance_2d_with_spacing(p1, p2, x_spacing: float, y_spacing: float) -> float:
    r"""Return the distance between two 2D iterables (list or tuple) given x and y spacing values.
    :param p1: 2D point
    :type p1: iterable
    :param p2: 2D point
    :type p2: iterable
    :param x_spacing:
    :type x_spacing: float
    :param y_spacing:
    :type y_spacing: float"""
    assert len(p1) == 2 and len(p2) == 2
    return np.sqrt(
        (x_spacing * (p1[0] - p2[0])) ** 2 + (y_spacing * (p1[1] - p2[1])) ** 2
    )


# TODO: Super naive, but realistically will work fine
def background_color_of_binary_thresholded_slice(img_2d: sitk.Image) -> BinaryColor:
    r"""Checks the background color of the slice returning from binary threshold filter
    since some settings result in fg 0, bg 1, and other settings result in fg 1, bg 0.

    Internally, compares the pixel value at (0, 0) to pixel values at the top, bottom, left, and right edges.
    Very naive approach that assumes there won't be noise or islands at the edges.

    :param img_2d:
    :type img_2d: sitk.Image
    :return: BinaryColor.Black or BinaryColor.White
    :rtype: BinaryColor"""
    width: int = img_2d.GetWidth()
    height: int = img_2d.GetHeight()
    background_color: int = img_2d.GetPixel(0, 0)
    mismatched_pixels: int = 0
    for i in range(
        1,
        width,
        width // NUM_PIXELS_TO_CHECK_ON_EACH_EDGE_FOR_BACKGROUND_COLOR_DETECTION,
    ):
        mismatched_pixels += img_2d.GetPixel(i, 0) != background_color
        mismatched_pixels += img_2d.GetPixel(i, height - 1) != background_color
    for j in range(
        1,
        height,
        height // NUM_PIXELS_TO_CHECK_ON_EACH_EDGE_FOR_BACKGROUND_COLOR_DETECTION,
    ):
        mismatched_pixels += img_2d.GetPixel(0, j) != background_color
        mismatched_pixels += img_2d.GetPixel(width - 1, j) != background_color
    if mismatched_pixels > MAX_NUM_MISMATCHED_PIXELS_FOR_BACKGROUND_COLOR_DETECTION:
        raise Exception(
            f"Could not successfully detect background color after executing binary threshold.\nMore than {MAX_NUM_MISMATCHED_PIXELS_FOR_BACKGROUND_COLOR_DETECTION} pixels on the top, bottom, left, or right edge don't match the pixel at the top left corner."
        )

    return BinaryColor(background_color)
