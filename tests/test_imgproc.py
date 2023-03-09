"""Test stuff in Playground.imgproc."""

import SimpleITK as sitk
import math
import numpy as np
import cv2
import Playground.imgproc.imgproc_helpers as helpers

OUTPUT_DIR = 'out'
NRRD1_PATH = 'ExampleData/BCP_Dataset_2month_T1w.nrrd'
NRRD2_PATH = 'ExampleData/IBIS_Dataset_12month_T1w.nrrd'
NRRD3_PATH = 'ExampleData/IBIS_Dataset_NotAligned_6month_T1w.nrrd'
NIFTI_PATH = 'ExampleData/MicroBiome_1month_T1w.nii.gz'
EPSILON = 0.01

def test_arc_length_works_same_on_binary_0_1_slice_and_binary_0_255_slice():
    """Test that cv2.arclength returns the same numbers for a file with 0's and 1's and a file with 0's and 255's.
    
    Our helpers.get_contour_length takes a binary image and does not replace the 1's with 255's. This test does so to make sure the numbers are the same.
    
    2^4=16 tests, which takes a while. Can ignore this test later."""
    reader = sitk.ImageFileReader()
    reader.SetFileName(NIFTI_PATH)
    image = reader.Execute()
    for theta_x in range(2):
        for theta_y in range(2):
            for theta_z in range(2):
                for slice_z in range(2):
                    binary_contour = helpers.rotate_and_get_contour(image, theta_x, theta_y, theta_z, slice_z)
                    circumference_1 = helpers.get_contour_length(binary_contour)


                    contour_255 = helpers.rotate_and_get_contour(image, theta_x, theta_y, theta_z, slice_z)
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

    
