"""Image helper functions.

Holds helper functions for working with IMAGE_GROUPS and IMAGE_DICT in global_vars.py."""

from typing import Union
import SimpleITK as sitk
from pathlib import Path
import src.utils.global_vars as global_vars
from src.utils.constants import degrees_to_radians
import src.utils.constants as constants


def update_image_groups(path_list: list[Path]) -> None:
    """Given list[str] of paths, put each path (and corresponding sitk.Image) into global IMAGE_DICT
    and IMAGE_GROUPS.

    :param path_list:
    :type path_list: list[Path]"""
    for path in path_list:
        global_vars.READER.SetFileName(str(path))
        new_img: sitk.Image = global_vars.READER.Execute()
        new_img_properties: tuple = get_properties(new_img)
        if new_img_properties in global_vars.IMAGE_GROUPS:
            # A duplicate path will get here, but we reassign the sitk.Image anyway
            # Because maybe the path stayed the same but the image file changed
            # No harm in reassigning. Already needed to do READER.Execute() to get properties anyway, might
            # as well reassign.
            global_vars.IMAGE_GROUPS[new_img_properties][path] = new_img
        else:
            # Create new dictionary associated with the new properties.
            # First entry is path: new_img
            global_vars.IMAGE_GROUPS[new_img_properties] = {path: new_img}
    global_vars.IMAGE_DICT = global_vars.IMAGE_GROUPS[
        list(global_vars.IMAGE_GROUPS.keys())[0]
    ]


def initialize_globals(path_list: list[Path]) -> None:
    """After pressing File > Open, the global variables need to be cleared and (re)initialized.

    The mutated global variables: IMAGE_GROUPS, IMAGE_DICT, INDEX, READER, THETA_X, THETA_Y, THETA_Z, SLICE,
    EULER_3D_TRANSFORM.

    Specifically, clears IMAGE_GROUPS and then populates it. IMAGE_DICT is the first image dict in IMAGE_GROUPS.

    :param path_list:
    :type path_list: list[Path]"""
    global_vars.IMAGE_GROUPS.clear()
    update_image_groups(path_list)
    # IMAGE_DICT was updated by update_image_groups
    global_vars.CURR_IMAGE_INDEX = 0
    global_vars.THETA_X = 0
    global_vars.THETA_Y = 0
    global_vars.THETA_Z = 0
    # curr_img has the same properties as the whole group in IMAGE_DICT
    curr_img: sitk.Image = curr_image()
    global_vars.SLICE = get_middle_of_z_dimension(curr_img)
    global_vars.EULER_3D_TRANSFORM.SetCenter(get_center_of_rotation(curr_img))
    global_vars.EULER_3D_TRANSFORM.SetRotation(0, 0, 0)


def clear_globals():
    """Clear global variables for unit testing in test_img_helpers.

    Don't need to reset Euler3DTransform since that's not used in the tests there."""
    global_vars.IMAGE_GROUPS.clear()
    global_vars.IMAGE_DICT.clear()
    global_vars.CURR_IMAGE_INDEX = 0
    global_vars.THETA_X = 0
    global_vars.THETA_Y = 0
    global_vars.THETA_Z = 0
    global_vars.SLICE = 0


# TODO: Add more properties
def get_properties(img: sitk.Image) -> tuple:
    """Tuple of properties of a sitk.Image.

    TODO: Add more properties

    :param img:
    :type img: sitk.Image
    :return: (dimensions, center of rotation used in EULER_3D_TRANSFORM, spacing)
    :rtype: tuple"""
    return (
        img.GetSize(),
        get_center_of_rotation(img),
        img.GetSpacing(),
    )


def curr_path() -> Path:
    """Return the Path of the current image.

    :return: Path of current image
    :rtype: Path"""
    return list(global_vars.IMAGE_DICT.keys())[global_vars.CURR_IMAGE_INDEX]


def curr_image() -> sitk.Image:
    """Return the image at the current index in global_vars.IMAGE_DICT.

    :return: current image
    :rtype: sitk.Image"""
    return global_vars.IMAGE_DICT[curr_path()]


def curr_rotated_slice() -> sitk.Image:
    """Return 2D rotated slice of the current image determined by rotation and slice settings in global_vars.py

    Sets global_vars.EULER_3D_TRANSFORM's rotation values but not its center since all loaded images should
    have the same center. TODO: Check this in `validate()`

    :return: 2D rotated slice
    :rtype: sitk.Image"""
    global_vars.EULER_3D_TRANSFORM.SetRotation(
        degrees_to_radians(global_vars.THETA_X),
        degrees_to_radians(global_vars.THETA_Y),
        degrees_to_radians(global_vars.THETA_Z),
    )
    return sitk.Resample(curr_image(), global_vars.EULER_3D_TRANSFORM)[
        :, :, global_vars.SLICE
    ]


def rotated_slice_hardcoded(
    mri_img_3d: sitk.Image,
    theta_x: int = 0,
    theta_y: int = 0,
    theta_z: int = 0,
    slice_num: int = 0,
):
    """Get 2D rotated slice of mri_img_3d from hardcoded values. Rotation values are in degrees, slice_num is an int.

    For unit testing.

    :param mri_img_3d:
    :type mri_img_3d: sitk.Image
    :param theta_x:
    :type theta_x: int
    :param theta_y:
    :type theta_y: int
    :param theta_z:
    :type theta_z: int
    :param slice_num:
    :type slice_num: int"""
    global_vars.EULER_3D_TRANSFORM.SetCenter(get_center_of_rotation(mri_img_3d))
    global_vars.EULER_3D_TRANSFORM.SetRotation(
        degrees_to_radians(theta_x),
        degrees_to_radians(theta_y),
        degrees_to_radians(theta_z),
    )
    return sitk.Resample(mri_img_3d, global_vars.EULER_3D_TRANSFORM)[:, :, slice_num]


def curr_metadata() -> dict[str, str]:
    """Computes and returns current image's metadata.

    Note: Does not return all metadata stored in the file, just the metadata stored in sitk.Image.GetMetaDataKeys()
    For example, it's possible for a sitk.Image to have spacing values retrieved by GetSpacing(), but the same spacing values won't
    be returned by this function.

    :return: metadata
    :rtype: dict[str, str]"""
    curr_img: sitk.Image = curr_image()
    rv: dict[str, str] = dict()
    for key in curr_img.GetMetaDataKeys():
        rv[key] = curr_img.GetMetaData(key)
    return rv


# TODO: works only for NIFTI, not NRRD
def curr_physical_units() -> Union[str, None]:
    """Return current image's physical units from sitk.GetMetaData if it exists, else None.

    TODO: works only for NIFTI, not NRRD.

    :return: units or None
    :rtype: str or None"""
    curr_img: sitk.Image = curr_image()
    if constants.NIFTI_METADATA_UNITS_KEY in curr_img.GetMetaDataKeys():
        return constants.NIFTI_METADATA_UNITS_VALUE_TO_PHYSICAL_UNITS[
            curr_img.GetMetaData(constants.NIFTI_METADATA_UNITS_KEY)
        ]
    return None


def get_curr_properties_tuple() -> tuple:
    """Return properties tuple for the current loaded group of images.

    :return: current properties tuple
    :rtype: tuple"""
    return list(global_vars.IMAGE_GROUPS.keys())[global_vars.CURR_BATCH_INDEX]


def get_middle_of_z_dimension(img: sitk.Image) -> int:
    """int((img.GetSize()[2] - 1) / 2)

    :param img:
    :type img: sitk.Image
    :return: int((img.GetSize()[2] - 1) / 2)
    :rtype: int"""
    return int((img.GetSize()[2] - 1) / 2)


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


def del_curr_img() -> None:
    """Won't remove if IMAGE_DICT is empty. Will print message and return early.

    Will decrement CURR_IMAGE_INDEX if removing the last element.

    Will not check for IMAGE_DICT being empty after the deletion. This happens in the GUI.
    """
    if len(global_vars.IMAGE_DICT) == 0:
        print("Can't remove from empty list!")
        return

    del global_vars.IMAGE_DICT[curr_path()]

    # Just deleted the last image. Index must decrease by 1
    if global_vars.CURR_IMAGE_INDEX == len(global_vars.IMAGE_DICT):
        global_vars.CURR_IMAGE_INDEX -= 1


def next_img() -> None:
    global_vars.CURR_IMAGE_INDEX = (global_vars.CURR_IMAGE_INDEX + 1) % len(
        global_vars.IMAGE_DICT
    )


def previous_img() -> None:
    global_vars.CURR_IMAGE_INDEX = (global_vars.CURR_IMAGE_INDEX - 1) % len(
        global_vars.IMAGE_DICT
    )
