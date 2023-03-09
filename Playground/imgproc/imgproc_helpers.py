"""Some helper functions for image processing."""

import SimpleITK as sitk
import numpy as np
import cv2
import matplotlib.pyplot as plt


def rotate_and_get_contour(img: sitk.Image, theta_x: int, theta_y: int, theta_z: int, slice_z: int) -> sitk.Image:
    """
    Do 3D rotation, get 2D slice, apply Otsu threshold, hole filling, and get contours.

    Return 2D slice containing only the contour. RV is a sitk.Image with UInt8 pixels, only 0 or 1.
    
    Parameters
    ----------
    img
        `sitk.Image` 3D image
    theta_x, theta_y, theta_z
        In degrees
    slice_z
        The number of the slice"""

    euler_3d_transform = sitk.Euler3DTransform()
    # NOTE: This center is possibly incorrect.
    euler_3d_transform.SetCenter(img.TransformContinuousIndexToPhysicalPoint([((dimension - 1) / 2.0) for dimension in img.GetSize()]))
    euler_3d_transform.SetRotation(degrees_to_radians(theta_x), degrees_to_radians(theta_y), degrees_to_radians(theta_z))
    rotated_image = sitk.Resample(img, euler_3d_transform)
    rotated_image_slice = rotated_image[:,:,slice_z]

    # The cast is necessary, otherwise get sitk::ERROR: Pixel type: 16-bit signed integer is not supported in 2D
    smooth_slice = sitk.GradientAnisotropicDiffusionImageFilter().Execute(sitk.Cast(rotated_image_slice, sitk.sitkFloat64))

    otsu = sitk.OtsuThresholdImageFilter().Execute(smooth_slice)

    hole_filling = sitk.BinaryGrindPeakImageFilter().Execute(otsu)

    # BinaryGrindPeakImageFilter has inverted foreground/background 0 and 1
    inverted = sitk.NotImageFilter().Execute(hole_filling)

    largest_component = select_largest_component(inverted)

    contour = sitk.BinaryContourImageFilter().Execute(largest_component)

    return contour


def get_contour_length(contour_2D_slice: sitk.Image) -> float:
    """Given a 2D slice containing only the contour, return the arc length.
    
    NOT A FINISHED IMPLEMENTATION. DOES NOT ACCOUNT FOR NON-SQUARE PIXELS."""
    # NOTE: np.ndarray is the transpose of sitk.Image image representation.
    # Compare write_sitk_image() and write_numpy_array(), which write the same result but have reversed indexing.
    temp: np.ndarray = sitk.GetArrayFromImage(contour_2D_slice)
    contours, hierarchy = cv2.findContours(temp, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # TODO: This might not return the right contour. contours is a list of the contours that cv2 finds.
    # We need to make sure contours[0] is always the outer contour.
    contour = contours[0]
    circumference = cv2.arcLength(contour, True)
    return circumference


def degrees_to_radians(num: float) -> float:
    return num * np.pi / 180


# Credit: https://discourse.itk.org/t/simpleitk-extract-largest-connected-component-from-binary-image/4958
def select_largest_component(binary_slice: sitk.Image):
    component_image = sitk.ConnectedComponent(binary_slice)
    sorted_component_image = sitk.RelabelComponent(component_image, sortByObjectSize=True)
    largest_component_binary_image = sorted_component_image == 1
    return largest_component_binary_image


def write_sitk_image(slice: sitk.Image, filename: str):
    """Write a 2D slice to the file `filename`, for testing purposes."""
    with open(filename, 'w') as f:
        for x in range(slice.GetSize()[0]):
            for y in range(slice.GetSize()[1]):
                f.write(f'{slice.GetPixel(x, y)}')
            f.write('\n')
        

def write_numpy_array_image(matrix: np.ndarray, filename: str):
    """Write numpy matrix representation of sitk.Image resulting from sitk.GetArrayFromImage to a text file.
    
    numpy has flipped (transposed) x and y. Must write matrix[j][i] to get the same result as `write_slice`.
    
    Warning, sitk.GetArrayFromImage returns a transposed representation of the sitk.Image."""
    with open(filename, 'w') as f:
        for i in range(len(matrix[0])):
            for j in range(len(matrix)):
                f.write(str(matrix[j][i]))
            f.write('\n')


def show_fiji(image: sitk.Image) -> None:
    sitk.Show(sitk.Cast(image,sitk.sitkFloat32) + 255)


def show_current_slice(current_slice: sitk.Image) -> None:
    plt.imshow(sitk.GetArrayViewFromImage(current_slice))
    plt.axis('off')
    plt.show()
