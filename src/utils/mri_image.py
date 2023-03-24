"""MRI image helper functions."""

from typing import Union
import SimpleITK as sitk
from pathlib import Path


import src.utils.global_vars as global_vars
from src.utils.constants import degrees_to_radians
import src.utils.constants as constants


# TODO: Check more properties
def validate_image(img: sitk.Image) -> bool:
    """Check that `img` has the same properties as the MODEL_IMAGE.

    For now, checks that dimensions and center of rotation and spacing are the same.

    TODO: Check more properties

    :param img:
    :type img: sitk.Image
    :return: True if `img` has the same properties as MODEL_IMAGE, else False.
    :rtype: bool"""
    return (
        img.GetSize() == global_vars.MODEL_IMAGE.GetSize()
        and img.TransformContinuousIndexToPhysicalPoint(
            [(dimension - 1) / 2.0 for dimension in img.GetSize()]
        )
        == global_vars.MODEL_IMAGE.TransformContinuousIndexToPhysicalPoint(
            [(dimension - 1) / 2.0 for dimension in global_vars.MODEL_IMAGE.GetSize()]
        )
        and img.GetSpacing() == global_vars.MODEL_IMAGE.GetSpacing()
    )


def get_curr_path() -> Path:
    """Return the Path of the current image, i.e. global_vars.IMAGE_DICT.keys()[global_vars.INDEX]

    :return: Path of current image
    :rtype: Path"""
    return global_vars.IMAGE_DICT.keys()[global_vars.INDEX]


def get_curr_image() -> sitk.Image:
    """Return the image at the current index in global_vars.IMAGE_DICT.

    :return: current image
    :rtype: sitk.Image"""
    return global_vars.IMAGE_DICT[global_vars.IMAGE_DICT.keys()[global_vars.INDEX]]


def get_rotated_slice() -> sitk.Image:
    """Return 2D rotated slice of the image at the current index determined by rotation and slice settings in global_vars.py

    Sets global_vars.EULER_3D_TRANSFORM's rotation values but not its center since all loaded images should
    have the same center. TODO: Check this in `validate()`

    :return: 2D rotated slice
    :rtype: sitk.Image"""
    global_vars.EULER_3D_TRANSFORM.SetRotation(
        degrees_to_radians(global_vars.THETA_X),
        degrees_to_radians(global_vars.THETA_Y),
        degrees_to_radians(global_vars.THETA_Z),
    )
    return sitk.Resample(get_curr_image(), global_vars.EULER_3D_TRANSFORM)[
        :, :, global_vars.SLICE
    ]


def get_rotated_slice_hardcoded(
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
    global_vars.EULER_3D_TRANSFORM.SetCenter(
        mri_img_3d.TransformContinuousIndexToPhysicalPoint(
            [(dimension - 1) / 2.0 for dimension in mri_img_3d.GetSize()]
        )
    )
    global_vars.EULER_3D_TRANSFORM.SetRotation(
        degrees_to_radians(theta_x),
        degrees_to_radians(theta_y),
        degrees_to_radians(theta_z),
    )
    return sitk.Resample(mri_img_3d, global_vars.EULER_3D_TRANSFORM)[:, :, slice_num]


def get_metadata() -> dict[str, str]:
    """Computes and returns current image's metadata.

    Note: Does not return all metadata stored in the file, just the metadata stored in sitk.Image.GetMetaDataKeys()
    For example, it's possible for a sitk.Image to have spacing values retrieved by GetSpacing(), but the same spacing values won't
    be returned by this function.

    :return: metadata
    :rtype: dict[str, str]"""
    curr_img: sitk.Image = get_curr_image()
    rv: dict[str, str] = dict()
    for key in curr_img.GetMetaDataKeys():
        rv[key] = curr_img.GetMetaData(key)
    return rv


# TODO: works only for NIFTI, not NRRD
def get_physical_units() -> Union[str, None]:
    """Return current image's physical units from sitk.GetMetaData if it exists, else None.

    TODO: works only for NIFTI, not NRRD"""
    curr_img: sitk.Image = get_curr_image()
    if constants.NIFTI_METADATA_UNITS_KEY in curr_img.GetMetaDataKeys():
        return constants.NIFTI_METADATA_UNITS_VALUE_TO_PHYSICAL_UNITS[
            curr_img.GetMetaData(constants.NIFTI_METADATA_UNITS_KEY)
        ]
    return None


def get_model_image_path() -> Path:
    """Get path of the model image. Internally, traverses the dictionary keys until the value is the MODEL_IMAGE."""
    for path in global_vars.IMAGE_DICT.keys():
        if global_vars.IMAGE_DICT[path] == global_vars.MODEL_IMAGE:
            return path
