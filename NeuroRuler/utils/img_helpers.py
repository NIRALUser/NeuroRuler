"""Image helper functions that aren't quite part of the main algorithm, unlike ``imgproc.py``.

Mostly holds helper functions for working with ``IMAGE_DICT`` in ``global_vars.py``."""

from typing import Union
import SimpleITK as sitk
from pathlib import Path
import NeuroRuler.utils.global_vars as global_vars
from NeuroRuler.utils.constants import degrees_to_radians, View
import NeuroRuler.utils.constants as constants


def update_images(path_list: list[Path]) -> list[Path]:
    """Initialize IMAGE_DICT. See the docstring for IMAGE_DICT in global_vars.py for more info.

    All images are oriented for the axial view when loaded. When calling this, make sure global_vars.VIEW = Z.

    If the images at path(s) in path_list don't match the properties of previously saved images,
    then this method returns the paths of the images that don't match, and
    IMAGE_DICT is updated only with the non-differing images.

    :param path_list:
    :type path_list: list[Path]
    :raise: Exception if path_list is empty (disallow this in GUI)
    :return: List of paths of images with properties that differ from those of the images currently in IMAGE_DICT
    :rtype: list[Path]"""
    if not path_list:
        raise Exception("update_images assumes path_list isn't empty.")

    # On load, orient the image for Z view by default
    # If we don't do this, then the misaligned image's GetSize()[2] won't actually be the inferior-superior axis
    # Then the max slice value would not be correct because it would use some other axis
    global_vars.ORIENT_FILTER.SetDesiredCoordinateOrientation(
        constants.Z_ORIENTATION_STR
    )

    comparison_properties_tuple: tuple
    if global_vars.IMAGE_DICT:
        comparison_properties_tuple = get_curr_properties_tuple()
    else:
        first_path: Path = path_list[0]
        comparison_properties_tuple = get_properties_from_path(first_path)
        global_vars.READER.SetFileName(str(first_path))
        first_img: sitk.Image = global_vars.READER.Execute()
        first_img_axial: sitk.Image = global_vars.ORIENT_FILTER.Execute(first_img)
        global_vars.IMAGE_DICT[first_path] = first_img_axial
        # Don't need to look at first image again
        path_list = path_list[1:]

    differing_image_paths: list[Path] = []

    for path in path_list:
        global_vars.READER.SetFileName(str(path))
        new_img: sitk.Image = global_vars.READER.Execute()
        new_img = global_vars.ORIENT_FILTER.Execute(new_img)
        new_img_properties: tuple = get_properties_from_sitk_image(new_img)
        if comparison_properties_tuple != new_img_properties:
            differing_image_paths.append(path)
        else:
            new_img_axial: sitk.Image = global_vars.ORIENT_FILTER.Execute(new_img)
            global_vars.IMAGE_DICT[path] = new_img_axial
    return differing_image_paths


def initialize_globals(path_list: list[Path]) -> list[Path]:
    """After pressing File > Open, the global variables need to be cleared and (re)initialized.

    If loading images with different properties, then this method returns
    False, and IMAGE_DICT isn't updated with the differing images.

    Mutated global variables: IMAGE_DICT, CURR_IMAGE_INDEX,
    READER, THETA_X, THETA_Y, THETA_Z, SLICE, EULER_3D_TRANSFORM.

    Specifically, clears IMAGE_DICT and then populates it.

    :param path_list:
    :type path_list: list[Path]
    :return: List of paths of images with properties that differ from those of the images currently in IMAGE_DICT
    :rtype: list[Path]"""
    global_vars.CURR_IMAGE_INDEX = 0
    global_vars.IMAGE_DICT.clear()
    differing_image_paths: list[Path] = update_images(path_list)
    global_vars.THETA_X = 0
    global_vars.THETA_Y = 0
    global_vars.THETA_Z = 0
    # curr_img has the same properties as the whole group in IMAGE_DICT.
    # Use it to set slice and center of rotation for the group
    curr_img: sitk.Image = get_curr_image()
    # TODO: Set maximum for the slice slider in the GUI!
    global_vars.SLICE = get_middle_dimension(curr_img, View.Z)
    global_vars.EULER_3D_TRANSFORM.SetCenter(get_center_of_rotation(curr_img))
    global_vars.EULER_3D_TRANSFORM.SetRotation(0, 0, 0)
    global_vars.SMOOTHING_FILTER.SetConductanceParameter(3.0)
    global_vars.SMOOTHING_FILTER.SetNumberOfIterations(5)
    global_vars.SMOOTHING_FILTER.SetTimeStep(0.0625)
    global_vars.VIEW = constants.View.Z
    global_vars.X_CENTER = get_middle_dimension(curr_img, View.X)
    global_vars.Y_CENTER = get_middle_dimension(curr_img, View.Y)
    global_vars.BINARY_THRESHOLD_FILTER.SetLowerThreshold(100)
    global_vars.BINARY_THRESHOLD_FILTER.SetUpperThreshold(200)
    return differing_image_paths


def clear_globals() -> None:
    """Clear global variables for unit testing in test_img_helpers.

    Don't need to reset Euler3DTransform since that's not used in the tests there.

    :return: None
    :rtype: None"""
    global_vars.IMAGE_DICT.clear()
    global_vars.CURR_IMAGE_INDEX = 0
    global_vars.THETA_X = 0
    global_vars.THETA_Y = 0
    global_vars.THETA_Z = 0
    global_vars.SLICE = 0


def image_dict_is_empty() -> bool:
    """
    :return: True if IMAGE_DICT is empty, else False
    :rtype: bool"""
    return bool(global_vars.IMAGE_DICT)


def get_curr_path() -> Path:
    """Return the current Path in IMAGE_DICT. That is, the key at index CURR_IMAGE_INDEX.

    :return: Path of current image
    :rtype: Path"""
    return list(global_vars.IMAGE_DICT.keys())[global_vars.CURR_IMAGE_INDEX]


def get_all_paths() -> list[Path]:
    """Return all Paths in IMAGE_DICT.

    :return: All paths in IMAGE_DICT
    :rtype: list[Path]"""
    return list(global_vars.IMAGE_DICT.keys())


def get_curr_image() -> sitk.Image:
    """Return the sitk.Image at the current index in global_vars.IMAGE_DICT.

    :return: current image
    :rtype: sitk.Image"""
    return global_vars.IMAGE_DICT[get_curr_path()]


# TODO: Add more properties?
# TODO: Implement tolerance for spacing
def get_properties_from_sitk_image(img: sitk.Image) -> tuple:
    """Tuple of properties of a sitk.Image.

    TODO: Add more properties

    If modifying this, NeuroRuler/GUI/main.py print_properties also has to be modified slightly.

    :param img:
    :type img: sitk.Image
    :return: (center of rotation used in EULER_3D_TRANSFORM, dimensions, spacing)
    :rtype: tuple"""
    return (
        get_center_of_rotation(img),
        img.GetSize(),
        img.GetSpacing(),
    )


def get_properties_from_path(path: Path) -> tuple:
    """Tuple of properties of the sitk.Image we get from path. Uses global_vars.READER.

    :param path: Path from which we can get a sitk.Image
    :type path: Path
    :return: (dimensions, center of rotation used in EULER_3D_TRANSFORM, spacing)
    :rtype: tuple"""
    global_vars.READER.SetFileName(str(path))
    img: sitk.Image = global_vars.READER.Execute()
    return get_properties_from_sitk_image(img)


def get_middle_dimension(img: sitk.Image, axis: View) -> int:
    """int((img.GetSize()[axis.value] - 1) / 2)

    :param img:
    :param axis: int (0-2)
    :type img: sitk.Image
    :return: int((img.GetSize()[axis.value] - 1) / 2)
    :rtype: int"""
    return int((img.GetSize()[axis.value] - 1) / 2)


def get_curr_image_size() -> tuple:
    """Return dimensions of current image.

    :return: dimensions
    :rtype: tuple"""
    return get_curr_image().GetSize()


def get_center_of_rotation(img: sitk.Image) -> tuple:
    """img.TransformContinuousIndexToPhysicalPoint([
    (dimension - 1) / 2.0 for dimension in img.GetSize()])

    :param: img
    :type img: sitk.Image
    :return: img.TransformContinuousIndexToPhysicalPoint([
    (dimension - 1) / 2.0 for dimension in img.GetSize()]"""
    return img.TransformContinuousIndexToPhysicalPoint(
        [(dimension - 1) / 2.0 for dimension in img.GetSize()]
    )


def set_curr_image(image: sitk.Image) -> None:
    """Set the sitk.Image at the current index in global_vars.IMAGE_DICT.

    :param image:
    :type image: sitk.Image
    :return: None
    :rtype: None"""
    global_vars.IMAGE_DICT[get_curr_path()] = image


def orient_curr_image(view: View) -> None:
    """Given a view enum, set the current image to the oriented version for that view.

    :param view:
    :type view: View.X, View.Y, or View.Z
    :return: None
    :rtype: None"""
    if not isinstance(view, View):
        raise Exception(
            "Expected View.X, View.Y, or View.Z but did not get one of those."
        )
    global_vars.ORIENT_FILTER.SetDesiredCoordinateOrientation(
        constants.ORIENTATION_STRINGS[view.value]
    )
    oriented: sitk.Image = global_vars.ORIENT_FILTER.Execute(get_curr_image())
    set_curr_image(oriented)


def get_curr_rotated_slice() -> sitk.Image:
    """Return 2D rotated slice of the current image determined by global rotation and slice settings.

    Sets global_vars.EULER_3D_TRANSFORM's rotation values but not its center since all loaded images should
    have the same center.

    :return: 2D rotated slice
    :rtype: sitk.Image"""
    global_vars.EULER_3D_TRANSFORM.SetRotation(
        degrees_to_radians(global_vars.THETA_X),
        degrees_to_radians(global_vars.THETA_Y),
        degrees_to_radians(global_vars.THETA_Z),
    )
    rotated_image: sitk.Image = sitk.Resample(
        get_curr_image(), global_vars.EULER_3D_TRANSFORM
    )
    rotated_slice: sitk.Image
    if global_vars.VIEW == constants.View.X:
        rotated_slice = rotated_image[global_vars.X_CENTER, :, :]
    elif global_vars.VIEW == constants.View.Y:
        rotated_slice = rotated_image[:, global_vars.Y_CENTER, :]
    else:
        rotated_slice = rotated_image[:, :, global_vars.SLICE]

    return rotated_slice


def get_curr_smooth_slice() -> sitk.Image:
    """Return smoothed 2D rotated slice of the current image determined by global smoothing settings.

    :return: smooth 2D rotated slice
    :rtype: sitk.Image"""
    rotated_slice: sitk.Image = get_curr_rotated_slice()
    # The cast is necessary, otherwise get sitk::ERROR: Pixel type: 16-bit signed integer is not supported in 2D
    smooth_slice: sitk.Image = global_vars.SMOOTHING_FILTER.Execute(
        sitk.Cast(rotated_slice, sitk.sitkFloat64)
    )
    return smooth_slice


def get_curr_binary_thresholded_slice() -> sitk.Image:
    """Return binary thresholded slice of the current image based on binary filter determined by
    global threshold settings.

    :return: binary thresholded 2D rotated slice using global binary threshold settings
    :rtype: sitk.Image"""
    rotated_slice: sitk.Image = get_curr_rotated_slice()
    filter_slice: sitk.Image = global_vars.BINARY_THRESHOLD_FILTER.Execute(
        sitk.Cast(rotated_slice, sitk.sitkFloat64)
    )
    return filter_slice


def get_curr_otsu_slice() -> sitk.Image:
    """Return Otsu filtered slice of the current image.

    :return: Otsu filtered 2D rotated slice
    :rtype: sitk.Image"""
    rotated_slice: sitk.Image = get_curr_rotated_slice()
    filter_slice: sitk.Image = global_vars.OTSU_THRESHOLD_FILTER.Execute(
        sitk.Cast(rotated_slice, sitk.sitkFloat64)
    )
    return filter_slice


def get_curr_metadata() -> dict[str, str]:
    """Computes and returns currently displayed image's metadata.

    Note: Does not return all metadata stored in the file, just the metadata stored in sitk.Image.GetMetaDataKeys()
    For example, it's possible to get a sitk.Image's spacing using GetSpacing(), but the same spacing values won't
    be returned by this function.

    :return: metadata
    :rtype: dict[str, str]"""
    curr_img: sitk.Image = get_curr_image()
    rv: dict[str, str] = dict()
    for key in curr_img.GetMetaDataKeys():
        rv[key] = curr_img.GetMetaData(key)
    return rv


# TODO works only for NIFTI, not NRRD
def get_curr_physical_units() -> Union[str, None]:
    """Return currently displayed image's physical units from sitk.GetMetaData if it exists, else None.

    TODO works only for NIFTI, not NRRD.

    :return: units or None
    :rtype: str or None"""
    curr_img: sitk.Image = get_curr_image()
    if constants.NIFTI_METADATA_UNITS_KEY in curr_img.GetMetaDataKeys():
        return constants.NIFTI_METADATA_UNITS_VALUE_TO_PHYSICAL_UNITS[
            curr_img.GetMetaData(constants.NIFTI_METADATA_UNITS_KEY)
        ]
    return None


def get_curr_properties_tuple() -> tuple:
    """Return properties tuple for the currently loaded batch of images.

    :return: current properties tuple
    :rtype: tuple"""
    return get_properties_from_sitk_image(list(global_vars.IMAGE_DICT.values())[0])


def del_curr_img() -> None:
    """Remove currently displayed image from IMAGE_DICT.

    Decrements CURR_IMAGE_INDEX if removing the last element.

    Will not check for IMAGE_DICT being empty after the deletion (GUI should be disabled).
    This happens in the GUI.

    :return: None
    :rtype: None"""
    if len(global_vars.IMAGE_DICT) == 0:
        print("Can't remove from empty list!")
        return

    del global_vars.IMAGE_DICT[get_curr_path()]

    # Just deleted the last image. Index must decrease by 1
    if global_vars.CURR_IMAGE_INDEX == len(global_vars.IMAGE_DICT):
        global_vars.CURR_IMAGE_INDEX -= 1


def next_img() -> None:
    """Increment CURR_IMAGE_INDEX, wrapping if necessary.

    :return: None
    :rtype: None"""
    global_vars.CURR_IMAGE_INDEX = (global_vars.CURR_IMAGE_INDEX + 1) % len(
        global_vars.IMAGE_DICT
    )


def previous_img() -> None:
    """Decrement CURR_IMAGE_INDEX, wrapping if necessary.

    :return: None
    :rtype: None"""
    global_vars.CURR_IMAGE_INDEX = (global_vars.CURR_IMAGE_INDEX - 1) % len(
        global_vars.IMAGE_DICT
    )


def get_rotated_slice_hardcoded(
    mri_img_3d: sitk.Image,
    theta_x: int = 0,
    theta_y: int = 0,
    theta_z: int = 0,
    slice_num: int = 0,
) -> sitk.Image:
    """Get 2D rotated slice of mri_img_3d from hardcoded values. Rotation values are in degrees, slice_num is an int.

    For unit testing. Sets center of global EULER_3D_TRANSFORM to center of rotation of mri_img_3d.

    :param mri_img_3d:
    :type mri_img_3d: sitk.Image
    :param theta_x:
    :type theta_x: int
    :param theta_y:
    :type theta_y: int
    :param theta_z:
    :type theta_z: int
    :param slice_num:
    :type slice_num: int
    :return: 2D rotated slice using hardcoded settings
    :rtype: sitk.Image"""
    global_vars.EULER_3D_TRANSFORM.SetCenter(get_center_of_rotation(mri_img_3d))
    global_vars.EULER_3D_TRANSFORM.SetRotation(
        degrees_to_radians(theta_x),
        degrees_to_radians(theta_y),
        degrees_to_radians(theta_z),
    )
    return sitk.Resample(mri_img_3d, global_vars.EULER_3D_TRANSFORM)[:, :, slice_num]
