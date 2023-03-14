"""Some helper functions for image processing."""

import SimpleITK as sitk
import numpy as np
import cv2
import matplotlib.pyplot as plt
import warnings
import functools
import pathlib
from PIL import Image
from typing import Union
try:
    # This is for pytest and normal use
    import src.utils.exceptions as exceptions
except ModuleNotFoundError:
    # This is for processing.ipynb
    import exceptions
import src.utils.globs as globs


# Source: https://stackoverflow.com/questions/2536307/decorators-in-the-python-standard-lib-deprecated-specifically
def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used."""
    @functools.wraps(func)
    def new_func(*args, **kwargs):
        warnings.simplefilter('always', DeprecationWarning)  # turn off filter
        warnings.warn("Call to deprecated function {}.".format(func.__name__),
                      category=DeprecationWarning,
                      stacklevel=2)
        warnings.simplefilter('default', DeprecationWarning)  # reset filter
        return func(*args, **kwargs)
    return new_func


# TODO: Make this call process_slice_and_get_contour?
def rotate_and_get_contour(img: sitk.Image, theta_x: int, theta_y: int, theta_z: int, slice_z: int) -> sitk.Image:
    """
    Do 3D rotation, then get 2D slice. Then, apply smoothing, Otsu threshold, hole filling, remove islands, and get contours.

    Return 2D `sitk.Image` containing only the largest connected contour (but may have child contours).

    RV is a binary (0|1) `sitk.Image` with UInt8 pixels.

    Parameters
    ----------
    img: `sitk.Image`
        3D image
    theta_x, theta_y, theta_z
        In degrees
    slice_z
        The number of the slice

    RV
    --
    sitk.Image
        Binary (0|1) image with points on the contour = 1"""

    euler_3d_transform = sitk.Euler3DTransform()
    # NOTE: This center is possibly incorrect.
    euler_3d_transform.SetCenter(img.TransformContinuousIndexToPhysicalPoint(
        [((dimension - 1) / 2.0) for dimension in img.GetSize()]))
    euler_3d_transform.SetRotation(degrees_to_radians(
        theta_x), degrees_to_radians(theta_y), degrees_to_radians(theta_z))
    rotated_image = sitk.Resample(img, euler_3d_transform)
    rotated_image_slice = rotated_image[:, :, slice_z]

    # The cast is necessary, otherwise get sitk::ERROR: Pixel type: 16-bit signed integer is not supported in 2D
    # However, this does throw some weird errors
    # GradientAnisotropicDiffusionImageFilter (0x107fa6a00): Anisotropic diffusion unstable time step: 0.125
    # Stable time step for this image must be smaller than 0.0997431
    smooth_slice = sitk.GradientAnisotropicDiffusionImageFilter().Execute(
        sitk.Cast(rotated_image_slice, sitk.sitkFloat64))

    otsu = sitk.OtsuThresholdImageFilter().Execute(smooth_slice)

    hole_filling = sitk.BinaryGrindPeakImageFilter().Execute(otsu)

    # BinaryGrindPeakImageFilter has inverted foreground/background 0 and 1, need to invert
    inverted = sitk.NotImageFilter().Execute(hole_filling)

    largest_component = select_largest_component(inverted)

    contour = sitk.BinaryContourImageFilter().Execute(largest_component)

    return contour


def process_slice_and_get_contour(slice: sitk.Image) -> sitk.Image:
    """Given a rotated slice, apply smoothing, Otsu threshold, hole filling, island removal, and get contours."""
    # The cast is necessary, otherwise get sitk::ERROR: Pixel type: 16-bit signed integer is not supported in 2D
    # However, this does throw some weird errors
    # GradientAnisotropicDiffusionImageFilter (0x107fa6a00): Anisotropic diffusion unstable time step: 0.125
    # Stable time step for this image must be smaller than 0.0997431
    smooth_slice = sitk.GradientAnisotropicDiffusionImageFilter().Execute(
        sitk.Cast(slice, sitk.sitkFloat64))

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


def get_contour_length(contour_2D_slice: Union[sitk.Image, np.ndarray]) -> float:
    """Given a 2D binary (0|1) or (0|255) slice containing only the contour, return the arc length.

    Based on commit a230a6b discussion, may not need to worry about non-square pixels.

    Parameter
    ---------
    contour_2D_slice: Union[sitk.Image, np.ndarray]
        Either `sitk.Image` or `np.ndarray`, for testing purposes.

        Note that if passing in a `sitk.Image`, then `sitk.GetArrayFromImage` will return a transposed `np.ndarray`.

        However, based on tests in `test_imgproc.py`, this will not affect the arc length result except in irrelevant edge cases where the slice is invalid."""
    slice_array: np.ndarray = sitk.GetArrayFromImage(contour_2D_slice) if isinstance(
        contour_2D_slice, sitk.Image) else contour_2D_slice
    contours, hierarchy = cv2.findContours(
        slice_array, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) >= 10:
        raise exceptions.ComputeCircumferenceOfInvalidSlice()

    # NOTE: select_largest_component removes all "islands" from the image.
    # But there can still be contours within the largest contour.
    # Most valid brain slices have 2 contours, rarely 3.
    # Assuming there are no islands, contours[0] is always the parent contour. See unit test in test_imgproc.py.
    contour = contours[0]
    length = cv2.arcLength(contour, True)
    return length


def save_sitk_slice_to_file(slice: sitk.Image, filepath: pathlib.Path) -> None:
    """Should be called after `MRIImage.resample` and `process_slice_and_get_contour`.

    Parameters
    ----------
    img
        2D slice
    filepath
        Should usually be in the `./img` directory. Any extension supported by `PIL.Image` is supported here. Should usually be jpg or png."""
    # This is transposed
    np_array: np.ndarray = sitk.GetArrayFromImage(slice)
    # Untranspose it to display the actual representation (i.e., what you'd see in Fiji)
    np_array = np.ndarray.transpose(np_array)
    # See https://stackoverflow.com/questions/16720682/pil-cannot-write-mode-f-to-jpeg
    img = Image.fromarray(np_array).convert("L")
    img.save(str(filepath))


def save_all_slices_to_img_dir():
    """Only called after `Open` is pressed. Saves all `rotated_slice`s in `globs.IMAGE_LIST` to `./img/` to ensure that all can be rendered.
    
    Each `MRIImage` gets a `rotated_slice` field during initialization with rotation and slice values all 0, which allows this to work."""
    for (i, mri_image) in enumerate(globs.IMAGE_LIST):
        save_sitk_slice_to_file(mri_image.get_rotated_slice(), globs.IMG_DIR / f'{i}.{globs.IMAGE_EXTENSION}')


def save_curr_slice_to_img_dir():
    """Save the current slice to `IMG_DIR`."""
    index: int = globs.IMAGE_LIST.get_index()
    # This is not a syntax error at runtime. MRIImageList.__gt__'s return value can't be Union[MRIImage, MRIImageList], so Python is confused before runtime.
    save_sitk_slice_to_file(globs.IMAGE_LIST[index].get_rotated_slice(), globs.IMG_DIR / f'{index}.{globs.IMAGE_EXTENSION}')


def binary_array_to_255_array(arr: np.ndarray) -> np.ndarray:
    """Given a binary (0|1) numpy array, returns a binary (0|255) array to display black and white in png/jpg images.

    Parameters
    ----------
    arr
        Rectangular (m x n) binary (0|1) array. This function does not check that all rows are of the same length. A deep copy is created and returned."""
    arr_copy = np.ndarray.copy(arr)
    for i in range(len(arr)):
        for j in range(len(arr[0])):
            if arr[i][j] == 1:
                arr_copy[i][j] = 255
    return arr_copy


def degrees_to_radians(num: Union[int, float]) -> float:
    """Convert degrees to radians."""
    return num * np.pi / 180


@deprecated
def show_fiji(image: sitk.Image) -> None:
    sitk.Show(sitk.Cast(image, sitk.sitkFloat32) + 255)


@deprecated
def show_current_slice(current_slice: sitk.Image) -> None:
    """Show current slice using `matplotlib.pyplot`."""
    plt.imshow(sitk.GetArrayViewFromImage(current_slice))
    plt.axis('off')
    plt.show()


@deprecated
def arc_length(contour_boundary_points: np.ndarray) -> float:
    """Given a numpy array representing boundary points of a contour, such as the result of `cv2.findContours`, return arc length.

    Parameters
    ----------
    contour_boundary_points
        Looks like [[[122  76]] [[121  77]] [[107  77]] ... [[106  78]]]. The return value of `cv2.findContours`."""
    assert len(contour_boundary_points) > 1
    arc_length: float = 0
    for i in range(len(contour_boundary_points) - 1):
        # contours[0] would return [[x y]], so need to do an additional [0] index to just get [x y]
        arc_length += distance_2d(
            contour_boundary_points[i][0], contour_boundary_points[i + 1][0])
    # Get distance between first and last points
    arc_length += distance_2d(
        contour_boundary_points[-1][0], contour_boundary_points[0][0])
    return arc_length


@deprecated
def distance_2d(x, y) -> float:
    """Return the distance between two 2D iterables."""
    assert (len(x) == 2) and (len(y) == 2)
    return np.sqrt((x[0] - y[0]) ** 2 + (x[1] - y[1]) ** 2)


@deprecated
def write_sitk_slice(slice: sitk.Image, filename: str):
    """Write a 2D slice to the file `filename`, for testing purposes."""
    with open(filename, 'w') as f:
        for x in range(slice.GetSize()[0]):
            for y in range(slice.GetSize()[1]):
                f.write(f'{slice.GetPixel(x, y)}')
            f.write('\n')


@deprecated
def write_numpy_array_slice_transpose(matrix: np.ndarray, filename: str):
    """Write numpy matrix representation of `sitk.Image` resulting from `sitk.GetArrayFromImage` to a text file.

    numpy has transposed x and y. Must use reversed indexing `matrix[j][i]` to get the same result as `write_sitk_slice`."""
    with open(filename, 'w') as f:
        for i in range(len(matrix[0])):
            for j in range(len(matrix)):
                f.write(str(matrix[j][i]))
            f.write('\n')
