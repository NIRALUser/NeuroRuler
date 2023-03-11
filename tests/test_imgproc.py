"""Test stuff in Playground.imgproc."""

import SimpleITK as sitk
import math
import numpy as np
import cv2
import pytest
import Playground.imgproc.imgproc_helpers as imgproc_helpers

OUTPUT_DIR = 'out'
NRRD1_PATH = 'ExampleData/BCP_Dataset_2month_T1w.nrrd'
NRRD2_PATH = 'ExampleData/IBIS_Dataset_12month_T1w.nrrd'
NRRD3_PATH = 'ExampleData/IBIS_Dataset_NotAligned_6month_T1w.nrrd'
NIFTI_PATH = 'ExampleData/MicroBiome_1month_T1w.nii.gz'
EPSILON = 0.001
"""Used for `float` comparisons."""

reader = sitk.ImageFileReader()
reader.SetFileName(NIFTI_PATH)
IMAGE_DONT_MUTATE = reader.Execute()
"""Reuse this image for tests; DO NOT MUTATE."""

def test_arc_length_works_same_on_binary_0_1_slice_and_binary_0_255_slice():
    """Test that cv2.arclength returns the same numbers for a file with 0's and 1's and a file with 0's and 255's.
    
    Our helpers.get_contour_length takes a binary image and does not replace the 1's with 255's. This test does so to make sure the numbers are the same.
    
    2^4=16 tests, which takes a while.
    
    Can ignore this test later."""
    for theta_x in range(2):
        for theta_y in range(2):
            for theta_z in range(2):
                for slice_z in range(2):
                    binary_contour = imgproc_helpers.rotate_and_get_contour(IMAGE_DONT_MUTATE, theta_x, theta_y, theta_z, slice_z)
                    circumference_1 = imgproc_helpers.get_contour_length(binary_contour)

                    contour_255 = imgproc_helpers.rotate_and_get_contour(IMAGE_DONT_MUTATE, theta_x, theta_y, theta_z, slice_z)
                    array_255: np.ndarray = sitk.GetArrayFromImage(contour_255)
                    for i in range(len(array_255)):
                        for j in range(len(array_255[0])):
                            if array_255[i][j] == 1:
                                array_255[i][j] = 255
                    contours, hierarchy = cv2.findContours(array_255, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                    contour = contours[0]
                    circumference_2 = cv2.arcLength(contour, True)
                    # == for float comparison is sus but these two numbers should be exactly the same so it's fine
                    assert circumference_1 == circumference_2


def test_our_arc_length_implementation_against_cv2_arc_length_implementation():
    """Test that our `arc_length` function works the same as cv2's."""
    for slice_z in range(0, 150, 15):
        contour_slice = imgproc_helpers.rotate_and_get_contour(IMAGE_DONT_MUTATE, 0, 0, 0, slice_z)
        # NOTE: np_contour_slice is the transpose of the sitk representation.
        # But don't need to worry about that for this test.
        np_contour_slice = sitk.GetArrayFromImage(contour_slice)
        contours, hierarchy = cv2.findContours(np_contour_slice, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contour = contours[0]

        cv2_arc_length = cv2.arcLength(contour, True)
        our_arc_length = imgproc_helpers.arc_length(contour)
        assert abs(cv2_arc_length - our_arc_length) < EPSILON


def test_numpy_2D_slice_array_is_transpose_of_sitk_2D_slice_array():
    """Confirm that the numpy matrix representation of a 2D slice is the transpose of the sitk matrix representation of a slice.
    
    Can ignore this test later."""
    for z_slice in range(10):
        sitk_contour: sitk.Image = imgproc_helpers.rotate_and_get_contour(IMAGE_DONT_MUTATE, 0, 0, 0, z_slice)
        numpy_contour: np.ndarray = sitk.GetArrayFromImage(sitk_contour)

        for i in range(len(numpy_contour)):
            for j in range(len(numpy_contour[0])):
                assert numpy_contour[i][j] == sitk_contour.GetPixel(j, i)


def test_distance_2d():
    """Somehow I'm paranoid I messed up something here lmao."""
    x: np.ndarray = np.array([0, 0])
    y: np.ndarray = np.array([3, 4])
    assert abs(imgproc_helpers.distance_2d(x, y) - 5.0) < EPSILON
    y = np.ndarray([3, 4, 5])
    with pytest.raises(AssertionError):
        imgproc_helpers.distance_2d(x, y)
