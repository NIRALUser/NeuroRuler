"""Some helper functions for image processing.

Deprecated functions that aren't currently in use are at the bottom. They should be removed when we're sure we won't
have any further use for them.
"""

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


# Not actually used except in unit tests. GUI rotations occur in mri_image.py.
def rotate_and_slice(mri_image: sitk.Image, theta_x: int, theta_y: int, theta_z: int, slice_z: int) -> sitk.Image:
    """Given a 3D MRI image, 3D rotate it, and return a 2D slice.
    
    Parameters
    ----------
    mri_image: sitk.Image
        3D MRI image
        
    theta_x, theta_y, theta_y
        All ints and in degrees
        
    slice_z
        Slice num"""
    euler_3d_transform: sitk.Euler3DTransform = sitk.Euler3DTransform()
    euler_3d_transform.SetCenter(mri_image.TransformContinuousIndexToPhysicalPoint([((dimension - 1) / 2.0) for dimension in mri_image.GetSize()]))
    euler_3d_transform.SetRotation(degrees_to_radians(theta_x), degrees_to_radians(theta_y), degrees_to_radians(theta_z))
    return sitk.Resample(mri_image, euler_3d_transform)[:, :, slice_z]


def contour(mri_slice: sitk.Image) -> sitk.Image:
    """Given a rotated slice, apply smoothing, Otsu threshold, hole filling, island removal, and get contours."""
    # The cast is necessary, otherwise get sitk::ERROR: Pixel type: 16-bit signed integer is not supported in 2D
    # However, this does throw some weird errors
    # GradientAnisotropicDiffusionImageFilter (0x107fa6a00): Anisotropic diffusion unstable time step: 0.125
    # Stable time step for this image must be smaller than 0.0997431
    smooth_slice = sitk.GradientAnisotropicDiffusionImageFilter().Execute(
        sitk.Cast(mri_slice, sitk.sitkFloat64))

    otsu = sitk.OtsuThresholdImageFilter().Execute(smooth_slice)

    hole_filling = sitk.BinaryGrindPeakImageFilter().Execute(otsu)

    # BinaryGrindPeakImageFilter has inverted foreground/background 0 and 1, need to invert
    inverted = sitk.NotImageFilter().Execute(hole_filling)

    largest_component = select_largest_component(inverted)

    contour = sitk.BinaryContourImageFilter().Execute(largest_component)

    return contour


# Credit: https://discourse.itk.org/t/simpleitk-extract-largest-connected-component-from-binary-image/4958
def select_largest_component(binary_slice: sitk.Image) -> sitk.Image:
    """Remove islands.

    Given a binary (0|1) binary slice, return a binary slice containing only the largest connected component."""
    component_image = sitk.ConnectedComponent(binary_slice)
    sorted_component_image = sitk.RelabelComponent(
        component_image, sortByObjectSize=True)
    largest_component_binary_image = sorted_component_image == 1
    return largest_component_binary_image


def length_of_contour(contour_slice: Union[sitk.Image, np.ndarray]) -> float:
    """Given a 2D binary (0|1 or 0|255) slice containing a single contour, return the arc length of the parent contour.

    Based on commit a230a6b discussion, may not need to worry about non-square pixels.

    Parameter
    ---------
    contour_slice: Union[sitk.Image, np.ndarray]
        This needs to be a 2D binary (0|1 or 0|255, doesn't make a difference) slice containing a contour.

        Note that if contour_slice is a `sitk.Image`, then `sitk.GetArrayFromImage` will return a `np.ndarray` that is the transpose of the `sitk` representation.

        Therefore, if passing in a `sitk.Image`, this function will re-transpose the numpy array resulting from `sitk.GetArrayFromImage`.
        
        Numpy's transpose will change the stride of the array, not the internal memory representation (i.e., no copy). But further np operations might be slowed.

        See https://blog.paperspace.com/numpy-optimization-internals-strides-reshape-transpose/. Should avoid the transpose if possible.

        But test_arc_length_of_transposed_matrix_is_same_hardcoded() showed that arc length might be different on transposed vs. non-transposed contours (might be an edge case though).
        
        test_arc_length_of_copy_after_transpose_same_as_no_copy_after_transpose() checks that the result with transpose then copy is the same as transpose without copy.
        
        So this function does not do .copy() after transpose."""
    slice_array: np.ndarray = np.ndarray.transpose(sitk.GetArrayFromImage(contour_slice)) if isinstance(contour_slice, sitk.Image) else contour_slice
    contours, hierarchy = cv2.findContours(slice_array, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) >= NUM_CONTOURS_IN_INVALID_SLICE:
        raise exceptions.ComputeCircumferenceOfInvalidSlice(len(contours))

    # NOTE: select_largest_component removes all "islands" from the image.
    # But there can still be contours within the largest contour.
    # Most valid brain slices have 2 contours, rarely 3.
    # Assuming there are no islands, contours[0] is always the parent contour.
    # See unit test in test_imgproc.py: test_contours_0_is_always_parent_contour_if_no_islands
    contour = contours[0]
    length = cv2.arcLength(contour, True)
    return length


def degrees_to_radians(num: Union[int, float]) -> float:
    return num * np.pi / 180
