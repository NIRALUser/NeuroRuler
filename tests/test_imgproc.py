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

OUTPUT_DIR = pathlib.Path('out')
NRRD1_PATH = pathlib.Path('ExampleData') / 'BCP_Dataset_2month_T1w.nrrd'
NRRD2_PATH = pathlib.Path('ExampleData') / 'IBIS_Dataset_12month_T1w.nrrd'
NRRD3_PATH = pathlib.Path('ExampleData') / 'IBIS_Dataset_NotAligned_6month_T1w.nrrd'
NIFTI_PATH = pathlib.Path('ExampleData') / 'MicroBiome_1month_T1w.nii.gz'
IMAGE_PATHS = [NRRD1_PATH, NRRD2_PATH, NRRD3_PATH, NIFTI_PATH]
"""For iterating over all images."""
EPSILON = 0.001
"""Used for `float` comparisons."""

reader = sitk.ImageFileReader()
# Choose a single MRI image to run tests on.
reader.SetFileName(str(NIFTI_PATH))
IMAGE_DONT_MUTATE = reader.Execute()
"""Reuse this image for tests; DO NOT MUTATE."""

def test_all_images_min_value_0_max_value_less_than_1600():
    types = ('*.nii.gz', '*.nii', '*.nrrd')
    base_path = pathlib.Path('ExampleData')
    reader = sitk.ImageFileReader()

    for type in types:
        path_list = pathlib.Path(base_path).glob(type)
        for img_path in path_list:
            reader.SetFileName(str(img_path))
            img: sitk.Image = reader.Execute()
            img_np: np.ndarray = sitk.GetArrayFromImage(img)
            assert img_np.min() == 0 and img_np.max() < 1600


# @pytest.mark.skip(reason="Passed in commit 6ebf428. Doesn't need to run again.")
def test_dimensions_of_np_array_same_as_original_image_but_transposed():
    """Probably not needed but just in case.
    
    The dimensions of the numpy array are the same as the original image.
     
    Additionally, PNG files generated from numpy arrays (no metadata) look the same as slices of the original image (i.e., spacing correct).
    
    Pretty sure that means the arc length generated from the numpy array is the arc length of the original image, with the same units as the original image."""
    for image_path in IMAGE_PATHS:
        reader = sitk.ImageFileReader()
        reader.SetFileName(str(image_path))
        image = reader.Execute()
        for slice_z in range(image.GetSize()[2]):
            slice = image[:, :, slice_z]
            # Transposed
            np_slice = sitk.GetArrayFromImage(slice)

            assert slice.GetSize()[0] == np_slice.shape[1]
            assert slice.GetSize()[1] == np_slice.shape[0]


# @pytest.mark.skip(reason="Passed in commit 6ebf428. Doesn't need to run again.")
def test_numpy_2D_slice_array_is_transpose_of_sitk_2D_slice_array():
    """Confirm that the numpy matrix representation of a 2D slice is the transpose of the sitk matrix representation of a slice.

    Can ignore this test later."""
    for z_slice in range(10):
        sitk_contour: sitk.Image = contour(rotate_and_slice(IMAGE_DONT_MUTATE, 0, 0, 0, z_slice))
        numpy_contour: np.ndarray = sitk.GetArrayFromImage(sitk_contour)

        for i in range(len(numpy_contour)):
            for j in range(len(numpy_contour[0])):
                assert numpy_contour[i][j] == sitk_contour.GetPixel(j, i)


# @pytest.mark.skip(reason="Passed in commit 6ebf428. Doesn't need to run again.")
def test_arc_length_works_same_on_binary_0_1_slice_and_binary_0_255_slice():
    """Test that cv2.arclength returns the same numbers for a file with 0's and 1's and a file with 0's and 255's.

    Our helpers.get_contour_length takes a binary image and does not replace the 1's with 255's. This test does so to make sure the numbers are the same.

    2^4=16 tests, which takes a while.

    Can ignore this test later."""
    for theta_x in range(2):
        for theta_y in range(2):
            for theta_z in range(2):
                for slice_z in range(2):
                    binary_contour = contour(rotate_and_slice(IMAGE_DONT_MUTATE, theta_x, theta_y, theta_z, slice_z))
                    circumference_1 = imgproc.length_of_contour(
                        binary_contour)

                    contour_255 = contour(rotate_and_slice(IMAGE_DONT_MUTATE, theta_x, theta_y, theta_z, slice_z))
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


# @pytest.mark.skip(reason="Passed in commit 6ebf428. Doesn't need to run again.")
def test_arc_length_of_transposed_matrix_is_same():
    """Per discussion here https://github.com/COMP523TeamD/HeadCircumferenceTool/commit/a230a6b57dc34ec433e311d760cc53841ddd6a49,

    Test that the arc length of a contour and its transpose is the same in a specific case. It probably generalizes to the general case.

    Specifically, for a matrix and its transpose, cv2.findContours will return [ [[x0 y0]] [[x1 y1]] [[x2 y2]] ... ] and [ [[y0 x0]], [[y1 x1]] [[y2 x2]] ... ]

    But cv2.arcLength will apply the distance formula to these contours and that will return the same result.

    However, if pixel spacing is off (non-square pixels), then the distance formula would need a scaling factor for one of the dimensions. Then we'd have to account for this.

    But the pixel spacing of the underlying `np.ndarray` passed into cv2.findContours *seems* to be fine. See discussion in the GH link.
    
    TODO: Unit test with pre-computed circumferences to really confirm this."""
    # Write settings of slices with more than 5 contours to a file to make sure they actually are just noise and not brain slices.
    f = open(pathlib.Path('tests') / 'noise_vals.txt', 'w')
    f.write('From test_arc_length_of_transposed_matrix_is_same\n')

    for theta_x in range(0, 90, 45):
        for theta_y in range(0, 90, 45):
            for theta_z in range(0, 90, 45):
                for slice_z in range(0, 150, 15):
                    sitk_contour = contour(rotate_and_slice(IMAGE_DONT_MUTATE, theta_x, theta_y, theta_z, slice_z))
                    np_contour_non_transposed = np.ndarray.transpose(sitk.GetArrayFromImage(sitk_contour))

                    assert (sitk_contour.GetSize()[0] == np_contour_non_transposed.shape[0]) and (sitk_contour.GetSize()[1] == np_contour_non_transposed.shape[1])

                    try:
                        # get_contour_length will call sitk.GetArrayFromImage on the sitk.Image, returning a transposed np.ndarray()
                        length_of_transposed_contour = imgproc.length_of_contour(sitk_contour)
                        # But if passing in a np.ndarray, then it won't transpose it
                        length_of_non_transposed_contour = imgproc.length_of_contour(np_contour_non_transposed)

                        assert length_of_transposed_contour == length_of_non_transposed_contour

                    except exceptions.ComputeCircumferenceOfInvalidSlice:
                        f.write(f'{theta_x, theta_y, theta_z, slice_z}\n')
    f.close()


# @pytest.mark.skip(reason="Passed in commit 6ebf428. Doesn't need to run again.")
def test_arc_length_of_transposed_matrix_is_same_hardcoded():
    """Same as above test but no rotations. Checks that the matrices are actually transposed.
    
    Tests all slices but ignores the result when there are more than 4 contours (usually occurs for very large slice value), which indicates that slice isn't a brain slice and looks like NIFTI slice 162."""
    # Write settings of slices with more than 5 contours to a file to make sure they actually are just noise and not brain slices.
    f = open(pathlib.Path('tests') / 'noise_vals.txt', 'a')
    f.write('From test_arc_length_of_transposed_matrix_is_same_hardcoded\n')

    for slice_z in range(0, IMAGE_DONT_MUTATE.GetSize()[2]):
        sitk_contour: sitk.Image = contour(rotate_and_slice(IMAGE_DONT_MUTATE, 0, 0, 0, slice_z))
        np_contour_transposed = sitk.GetArrayFromImage(sitk_contour)
        np_contour_not_transposed = np.ndarray.transpose(np_contour_transposed)

        assert sitk_contour.GetSize()[0] == np_contour_not_transposed.shape[0] and sitk_contour.GetSize()[1] == np_contour_not_transposed.shape[1]
        assert sitk_contour.GetSize()[0] == np_contour_transposed.shape[1] and sitk_contour.GetSize()[1] == np_contour_transposed.shape[0]

        contours_transposed, hierarchy = cv2.findContours(np_contour_transposed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours_not_transposed, hierarchy2 = cv2.findContours(np_contour_not_transposed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Number of contours should be the same if transposed or not transposed but check both just in case
        if len(contours_transposed) <= 9 and len(contours_not_transposed) <= 9:
            transposed_length = cv2.arcLength(contours_transposed[0], True)
            not_transposed_length = cv2.arcLength(contours_not_transposed[0], True)
            assert transposed_length == not_transposed_length
        else:
            f.write(f'(0, 0, 0, {slice_z})\n')
    f.close()


# @pytest.mark.skip(reason="Passed in commit 6ebf428. Doesn't need to run again.")
def test_contours_0_is_always_parent_contour_if_no_islands():
    """Assuming there are no islands in the image, then contours[0] results in the parent contour.
    
    See documentation on our wiki page about hierarchy. tl;dr hierarchy[0][i] returns information about the i'th contour.
    hierarchy[0][i][3] is information about the parent contour of the i'th contour. So if hierarchy[0][0][3] = -1, then the 0'th contour is the parent."""
    for slice_z in range(IMAGE_DONT_MUTATE.GetSize()[2]):
        # rotate_and_get_contour removes islands
        sitk_contour: sitk.Image = contour(rotate_and_slice(IMAGE_DONT_MUTATE, 0, 0, 0, slice_z))
        contours, hierarchy = cv2.findContours(sitk.GetArrayFromImage(sitk_contour), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        assert hierarchy[0][0][3] == -1
