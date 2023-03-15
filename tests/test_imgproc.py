"""Test stuff in Playground.imgproc.

We use == for float comparison instead of |a-b|<epsilon when the numbers should be *exactly* the same."""

import SimpleITK as sitk
import numpy as np
import cv2
import pytest
import pathlib
import src.utils.imgproc as imgproc
from src.utils.imgproc import rotate_and_slice, contour, length_of_contour
import src.utils.exceptions as exceptions
from src.utils.globs import EXAMPLE_IMAGE_PATHS, EXAMPLE_DATA_DIR, NUM_CONTOURS_IN_INVALID_SLICE

EPSILON = 0.001
"""Used for `float` comparisons."""
READER = sitk.ImageFileReader()
EXAMPLE_IMAGES = []
"""DON'T MUTATE ANY OF THESE IMAGES."""

for img_path in EXAMPLE_IMAGE_PATHS:
    READER.SetFileName(str(img_path))
    EXAMPLE_IMAGES.append(READER.Execute())

# @pytest.mark.skip(reason="")
def test_all_images_min_value_0_max_value_less_than_1600():
    for img in EXAMPLE_IMAGES:
        img_np: np.ndarray = sitk.GetArrayFromImage(img)
        assert img_np.min() == 0 and img_np.max() < 1600


# @pytest.mark.skip(reason="Passed in commit 6ebf428. Doesn\'t need to run again.")
def test_dimensions_of_np_array_same_as_original_image_but_transposed():
    """Probably not needed but just in case.
    
    The dimensions of the numpy array are the same as the original image.
     
    Additionally, PNG files generated from numpy arrays (no metadata) look the same as slices of the original image (i.e., spacing correct).
    
    Pretty sure that means the arc length generated from the numpy array is the arc length of the original image, with the same units as the original image."""
    for img in EXAMPLE_IMAGES:
        for slice_z in range(img.GetSize()[2]):
            slice = img[:, :, slice_z]
            # Transposed
            np_slice = sitk.GetArrayFromImage(slice)

            assert slice.GetSize()[0] == np_slice.shape[1]
            assert slice.GetSize()[1] == np_slice.shape[0]


# @pytest.mark.skip(reason="Passed in commit 6ebf428. Doesn\'t need to run again.")
def test_numpy_2D_slice_array_is_transpose_of_sitk_2D_slice_array():
    """Confirm that the numpy matrix representation of a 2D slice is the transpose of the sitk matrix representation of a slice.

    Can ignore this test later."""
    for img in EXAMPLE_IMAGES:
        for z_slice in range(10):
            sitk_contour: sitk.Image = contour(rotate_and_slice(img, 0, 0, 0, z_slice))
            numpy_contour: np.ndarray = sitk.GetArrayFromImage(sitk_contour)

            for i in range(len(numpy_contour)):
                for j in range(len(numpy_contour[0])):
                    assert numpy_contour[i][j] == sitk_contour.GetPixel(j, i)


# @pytest.mark.skip(reason="")
def test_contour_returns_binary_slice():
    """Test that the contour function always returns a binary (0|1) slice."""
    for img in EXAMPLE_IMAGES:
        for slice_z in range(img.GetSize()[2]):
            contour_slice: sitk.Image = contour(rotate_and_slice(img, 0, 0, 0, slice_z))
            slice_np: np.ndarray = sitk.GetArrayFromImage(contour_slice)
            assert slice_np.min() <= 1 and slice_np.max() <= 1


# @pytest.mark.skip(reason="Passed in commit 6ebf428. Doesn\'t need to run again.")
def test_arc_length_works_same_on_binary_0_1_slice_and_binary_0_255_slice():
    """Test that cv2.arclength returns the same numbers for a file with 0's and 1's and a file with 0's and 255's.

    Our helpers.get_contour_length takes a binary image and does not replace the 1's with 255's. This test does so to make sure the numbers are the same.

    2^4=16 tests, which takes a while.

    Can ignore this test later."""
    for img in EXAMPLE_IMAGES:
        for theta_x in range(2):
            for theta_y in range(2):
                for theta_z in range(2):
                    for slice_z in range(2):
                        binary_contour = contour(rotate_and_slice(img, theta_x, theta_y, theta_z, slice_z))
                        circumference_1 = 0
                        try:
                            circumference_1 = imgproc.length_of_contour(binary_contour)
                        except exceptions.ComputeCircumferenceOfInvalidSlice:
                            # Don't compare against circumference_2
                            continue

                        contour_255 = contour(rotate_and_slice(img, theta_x, theta_y, theta_z, slice_z))
                        array_255: np.ndarray = sitk.GetArrayFromImage(contour_255)
                        for i in range(len(array_255)):
                            for j in range(len(array_255[0])):
                                if array_255[i][j] == 1:
                                    array_255[i][j] = 255
                        contours, hierarchy = cv2.findContours(
                            array_255, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                        parent_contour = contours[0]
                        circumference_2 = cv2.arcLength(parent_contour, True)

                        assert circumference_1 == circumference_2


# @pytest.mark.skip(reason="Passed in commit 6ebf428. Doesn\'t need to run again.")
def test_contours_0_is_always_parent_contour_if_no_islands():
    """Assuming there are no islands in the image, then contours[0] results in the parent contour.
    
    See documentation on our wiki page about hierarchy. tl;dr hierarchy[0][i] returns information about the i'th contour.
    hierarchy[0][i][3] is information about the parent contour of the i'th contour. So if hierarchy[0][0][3] = -1, then the 0'th contour is the parent."""
    for img in EXAMPLE_IMAGES:
        for slice_z in range(img.GetSize()[2]):
            # rotate_and_get_contour removes islands
            sitk_contour: sitk.Image = contour(rotate_and_slice(img, 0, 0, 0, slice_z))
            contours, hierarchy = cv2.findContours(sitk.GetArrayFromImage(sitk_contour), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            assert hierarchy[0][0][3] == -1


# @pytest.mark.skip(reason="")
def test_arc_length_of_copy_after_transpose_same_as_no_copy_after_transpose():
    """Test arc length of two re-transposed arrays is the same when calling .copy() on one but not the other."""
    for img in EXAMPLE_IMAGES:
        for theta_x in range(0, 30, 15):
            for theta_y in range(0, 30, 15):
                for theta_z in range(0, 30, 15):
                    for slice_z in range(0, img.GetSize()[2], img.GetSize()[2] // 10):
                        binary_contour = contour(rotate_and_slice(img,theta_x, theta_y, theta_z, slice_z))
                        img_np = np.ndarray.transpose(sitk.GetArrayFromImage(binary_contour))
                        img_np_copied = np.ndarray.transpose(sitk.GetArrayFromImage(binary_contour)).copy()

                        length1 = 0
                        length2 = 0

                        try:
                            length1 = length_of_contour(img_np)
                            length2 = length_of_contour(img_np_copied)
                            assert length1 == length2
                        except exceptions.ComputeCircumferenceOfInvalidSlice:
                            pass


# @pytest.mark.skip(reason="")
def test_arc_length_of_copy_after_transpose_same_as_no_copy_after_transpose_hardcoded():
    """Same as above but doesn't use our arc length helper function. Hardcodes to avoid ComputeCircumferenceOfInvalidSlice"""
    for img in EXAMPLE_IMAGES:
        for theta_x in range(0, 30, 15):
            for theta_y in range(0, 30, 15):
                for theta_z in range(0, 30, 15):
                    for slice_z in range(0, img.GetSize()[2], img.GetSize()[2] // 10):
                        binary_contour = contour(rotate_and_slice(img,theta_x, theta_y, theta_z, slice_z))
                        img_np = np.ndarray.transpose(sitk.GetArrayFromImage(binary_contour))
                        img_np_copied = np.ndarray.transpose(sitk.GetArrayFromImage(binary_contour)).copy()

                        length1 = 0
                        length2 = 0

                        contours1, hierarchy1 = cv2.findContours(img_np, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                        contours2, hierarchy2 = cv2.findContours(img_np_copied, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

                        parent_1 = contours1[0]
                        parent_2 = contours2[0]

                        # Assumes it's a closed curve, and it might not be
                        assert cv2.arcLength(parent_1, True) == cv2.arcLength(parent_2, True)


# @pytest.mark.skip(reason="Length_of_contour now re-transposes the result of sitk.GetArrayFromImage. This test would no longer compare a non-transposed matrix to a transposed matrix, both are transposed.")
def test_arc_length_of_transposed_matrix_is_same():
    """Per discussion here https://github.com/COMP523TeamD/HeadCircumferenceTool/commit/a230a6b57dc34ec433e311d760cc53841ddd6a49,

    Test that the arc length of a contour and its transpose is the same in a specific case. It probably generalizes to the general case.

    Specifically, for a matrix and its transpose, cv2.findContours will return [ [[x0 y0]] [[x1 y1]] [[x2 y2]] ... ] and [ [[y0 x0]], [[y1 x1]] [[y2 x2]] ... ]

    But cv2.arcLength will apply the distance formula to these contours and that will return the same result.

    However, if pixel spacing is off (non-square pixels), then the distance formula would need a scaling factor for one of the dimensions. Then we'd have to account for this.

    But the pixel spacing of the underlying `np.ndarray` passed into cv2.findContours *seems* to be fine. See discussion in the GH link.
    
    TODO: Unit test with pre-computed circumferences to really confirm this."""
    # Write settings of slices that cause ComputeCircumferenceOfInvalidSlice to a file to make sure they actually are just noise and not brain slices.
    f = open(pathlib.Path('tests') / 'noise_vals.txt', 'w')
    f.write(f'Write settings of slices that cause ComputeCircumferenceOfInvalidSlice (>= {NUM_CONTOURS_IN_INVALID_SLICE} contours detected)\nto this file to make sure they actually are invalid brain slices\n\n')
    f.write('From test_arc_length_of_transposed_matrix_is_same\n\n')

    for img_path in EXAMPLE_IMAGE_PATHS:
        f.write(f'{EXAMPLE_DATA_DIR.name}/{img_path.name}\n')
        READER.SetFileName(str(img_path))
        img = READER.Execute()
        for theta_x in range(0, 90, 45):
            for theta_y in range(0, 90, 45):
                for theta_z in range(0, 90, 45):
                    for slice_z in range(0, 150, 15):
                        sitk_contour = contour(rotate_and_slice(img, theta_x, theta_y, theta_z, slice_z))
                        np_contour_non_transposed = np.ndarray.transpose(sitk.GetArrayFromImage(sitk_contour))

                        try:
                            # get_contour_length will call sitk.GetArrayFromImage on the sitk.Image, returning a transposed np.ndarray()
                            length_of_transposed_contour = imgproc.length_of_contour(sitk_contour)
                            # But if passing in a np.ndarray, then it won't transpose it
                            length_of_non_transposed_contour = imgproc.length_of_contour(np_contour_non_transposed)

                            assert length_of_transposed_contour == length_of_non_transposed_contour

                        except exceptions.ComputeCircumferenceOfInvalidSlice:
                            f.write(f'{theta_x, theta_y, theta_z, slice_z}\n')
    f.close()


# @pytest.mark.skip(reason="Passed in commit 6ebf428. Doesn\'t need to run again.")
def test_arc_length_of_transposed_matrix_is_same_hardcoded():
    """Same as above test but doesn't use our helper function.

    Tests all slices but ignores the result when there are more than 9 contours (usually occurs for very large slice value), which indicates that slice is invalid."""
    # Write settings of slices with more than 10 contours to a file to make sure they actually are just noise and not brain slices.
    f = open(pathlib.Path('tests') / 'noise_vals.txt', 'a')
    f.write('From test_arc_length_of_transposed_matrix_is_same_hardcoded\n')

    for img_path in EXAMPLE_IMAGE_PATHS:
        f.write(f'{EXAMPLE_DATA_DIR.name}/{img_path.name}\n')
        READER.SetFileName(str(img_path))
        img = READER.Execute()
        for slice_z in range(0, img.GetSize()[2]):
            sitk_contour: sitk.Image = contour(rotate_and_slice(img, 0, 0, 0, slice_z))
            np_contour_transposed = sitk.GetArrayFromImage(sitk_contour)
            np_contour_not_transposed = np.ndarray.transpose(np_contour_transposed)

            contours_transposed, hierarchy = cv2.findContours(np_contour_transposed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            contours_not_transposed, hierarchy2 = cv2.findContours(np_contour_not_transposed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            # Number of contours should be the same if transposed or not transposed but check both just in case
            if len(contours_transposed) < NUM_CONTOURS_IN_INVALID_SLICE and len(contours_not_transposed) < NUM_CONTOURS_IN_INVALID_SLICE:
                transposed_length = cv2.arcLength(contours_transposed[0], True)
                not_transposed_length = cv2.arcLength(contours_not_transposed[0], True)
                # if transposed_length < 300 or not_transposed_length < 300:
                    # continue
                assert transposed_length == not_transposed_length
            else:
                f.write(f'(0, 0, 0, {slice_z})\n')
    f.close()
