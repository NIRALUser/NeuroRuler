"""Test stuff in Playground.imgproc.

We use == for float comparison instead of |a-b|<epsilon when the numbers should be *exactly* the same."""

import SimpleITK as sitk
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
                    binary_contour = imgproc_helpers.rotate_and_get_contour(
                        IMAGE_DONT_MUTATE, theta_x, theta_y, theta_z, slice_z)
                    circumference_1 = imgproc_helpers.get_contour_length(
                        binary_contour)

                    contour_255 = imgproc_helpers.rotate_and_get_contour(
                        IMAGE_DONT_MUTATE, theta_x, theta_y, theta_z, slice_z)
                    array_255: np.ndarray = sitk.GetArrayFromImage(contour_255)
                    for i in range(len(array_255)):
                        for j in range(len(array_255[0])):
                            if array_255[i][j] == 1:
                                array_255[i][j] = 255
                    contours, hierarchy = cv2.findContours(
                        array_255, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                    contour = contours[0]
                    circumference_2 = cv2.arcLength(contour, True)

                    assert circumference_1 == circumference_2


@pytest.mark.skip(reason="Don't need this function")
def test_our_arc_length_implementation_against_cv2_arc_length_implementation():
    """Test that our `arc_length` function works the same as cv2's."""
    for slice_z in range(0, 150, 15):
        contour_slice = imgproc_helpers.rotate_and_get_contour(
            IMAGE_DONT_MUTATE, 0, 0, 0, slice_z)
        # NOTE: np_contour_slice is the transpose of the sitk representation.
        # But don't need to worry about that for this test.
        np_contour_slice = sitk.GetArrayFromImage(contour_slice)
        contours, hierarchy = cv2.findContours(
            np_contour_slice, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contour = contours[0]

        cv2_arc_length = cv2.arcLength(contour, True)
        our_arc_length = imgproc_helpers.arc_length(contour)
        assert abs(cv2_arc_length - our_arc_length) < EPSILON


def test_numpy_2D_slice_array_is_transpose_of_sitk_2D_slice_array():
    """Confirm that the numpy matrix representation of a 2D slice is the transpose of the sitk matrix representation of a slice.

    Can ignore this test later."""
    for z_slice in range(10):
        sitk_contour: sitk.Image = imgproc_helpers.rotate_and_get_contour(
            IMAGE_DONT_MUTATE, 0, 0, 0, z_slice)
        numpy_contour: np.ndarray = sitk.GetArrayFromImage(sitk_contour)

        for i in range(len(numpy_contour)):
            for j in range(len(numpy_contour[0])):
                assert numpy_contour[i][j] == sitk_contour.GetPixel(j, i)


def test_arc_length_of_transposed_matrix_is_same():
    """Per discussion here https://github.com/COMP523TeamD/HeadCircumferenceTool/commit/a230a6b57dc34ec433e311d760cc53841ddd6a49,

    Test that the arc length of a contour and its transpose is the same in a specific case. It probably generalizes to the general case.

    Specifically, for a matrix and its transpose, cv2.findContours will return [ [[x0 y0]] [[x1 y1]] [[x2 y2]] ... ] and [ [[y0 x0]], [[y1 x1]] [[y2 x2]] ... ]

    But cv2.arcLength will apply the distance formula to these contours and that will return the same result.

    However, if pixel spacing is off (non-square pixels), then the distance formula would need a scaling factor for one of the dimensions. Then we'd have to account for this.

    But the pixel spacing of the underlying `np.ndarray` passed into cv2.findContours *seems* to be fine. See discussion in the GH link.
    
    TODO: Unit test with pre-computed circumferences to really confirm this."""

    for theta_x in range(0, 90, 45):
        for theta_y in range(0, 90, 45):
            for theta_z in range(0, 90, 45):
                for slice_z in range(0, 150, 15):
                    sitk_contour: sitk.Image = imgproc_helpers.rotate_and_get_contour(IMAGE_DONT_MUTATE, theta_x, theta_y, theta_z, slice_z)
                    np_contour_non_transposed = np.ndarray.transpose(sitk.GetArrayFromImage(sitk_contour))

                    assert (sitk_contour.GetSize()[0] == np_contour_non_transposed.shape[0]) and (sitk_contour.GetSize()[1] == np_contour_non_transposed.shape[1])

                    # get_contour_length will call sitk.GetArrayFromImage on the sitk.Image, returning a transposed np.ndarray()
                    length_of_transposed_contour = imgproc_helpers.get_contour_length(sitk_contour)
                    # But if passing in a np.ndarray, then it won't transpose it
                    length_of_non_transposed_contour = imgproc_helpers.get_contour_length(np_contour_non_transposed)

                    assert length_of_transposed_contour == length_of_non_transposed_contour


def test_arc_length_of_transposed_matrix_is_same_hardcoded():
    """Same as above test but no rotations. Checks that the matrices are actually transposed.
    
    Tests all slices but ignores the result when there are more than 4 contours (usually occurs for very large slice value), which indicates that slice isn't a brain slice and looks like NIFTI slice 162."""
    for slice_z in range(0, IMAGE_DONT_MUTATE.GetSize()[2]):
        sitk_contour: sitk.Image = imgproc_helpers.rotate_and_get_contour(IMAGE_DONT_MUTATE, 0, 0, 0, slice_z)
        np_contour_transposed = sitk.GetArrayFromImage(sitk_contour)
        np_contour_not_transposed = np.ndarray.transpose(np_contour_transposed)

        assert sitk_contour.GetSize()[0] == np_contour_not_transposed.shape[0] and sitk_contour.GetSize()[1] == np_contour_not_transposed.shape[1]
        assert sitk_contour.GetSize()[0] == np_contour_transposed.shape[1] and sitk_contour.GetSize()[1] == np_contour_transposed.shape[0]

        contours_transposed, hierarchy = cv2.findContours(np_contour_transposed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours_not_transposed, hierarchy2 = cv2.findContours(np_contour_not_transposed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Number of contours should be the same if transposed or not transposed but check both just in case
        if len(contours_transposed) < 5 and len(contours_not_transposed) < 5:
            transposed_length = cv2.arcLength(contours_transposed[0], True)
            not_transposed_length = cv2.arcLength(contours_not_transposed[0], True)
            assert transposed_length == not_transposed_length


def test_contours_0_is_always_parent_contour_if_no_islands():
    """Assuming there are no islands in the image, then contours[0] results in the parent contour.
    
    See documentation on our wiki page about hierarchy. tl;dr hierarchy[0][i] returns information about the i'th contour.
    hierarchy[0][i][3] is information about the parent contour of the i'th contour. So if hierarchy[0][0][3] = -1, then the 0'th contour is the parent."""
    for slice_z in range(IMAGE_DONT_MUTATE.GetSize()[2]):
        # rotate_and_get_contour removes islands
        sitk_contour: sitk.Image = imgproc_helpers.rotate_and_get_contour(IMAGE_DONT_MUTATE, 0, 0, 0, slice_z)
        contours, hierarchy = cv2.findContours(sitk.GetArrayFromImage(sitk_contour), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        assert hierarchy[0][0][3] == -1


@pytest.mark.skip(reason="This is trivial")
def test_distance_2d():
    """Really don't need to test this. Testing just in case."""
    x: np.ndarray = np.array([0, 0])
    y: np.ndarray = np.array([3, 4])
    assert abs(imgproc_helpers.distance_2d(x, y) - 5.0) < EPSILON
    y = np.ndarray([3, 4, 5])
    with pytest.raises(AssertionError):
        imgproc_helpers.distance_2d(x, y)
