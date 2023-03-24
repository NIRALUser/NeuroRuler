"""MRI image helper functions."""

from typing import Union
import SimpleITK as sitk
from pathlib import Path


import src.utils.global_vars as global_vars
from src.utils.constants import degrees_to_radians
import src.utils.constants as constants

# TODO: I wrote this before writing other stuff. This code can probably be optimized a little.
def initialize_globals(model_image_path: Path) -> None:
    """After pressing File > Open, the global variables need to be (re)initialized.

    The mutated global variables: IMAGE_DICT, INDEX, READER, MODEL_IMAGE, IMAGE_GROUPS, THETA_X, THETA_Y, THETA_Z, SLICE,
    EULER_3D_TRANSFORM.

    Specifically, populates IMAGE_DICT and IMAGE_LIST with the first image (i.e., MODEL_IMAGE).

    :param model_image_path:
    :type model_image_path: Path"""
    global_vars.IMAGE_DICT.clear()
    global_vars.INDEX = 0
    global_vars.READER.SetFileName(str(model_image_path))
    model_image: sitk.Image = global_vars.READER.Execute()
    global_vars.MODEL_IMAGE = model_image
    global_vars.IMAGE_DICT[Path(model_image_path)] = model_image
    global_vars.IMAGE_GROUPS.append((get_properties(model_image), [model_image_path]))
    global_vars.THETA_X = 0
    global_vars.THETA_Y = 0
    global_vars.THETA_Z = 0
    global_vars.SLICE = int((model_image.GetSize()[2] - 1) / 2)
    global_vars.EULER_3D_TRANSFORM.SetCenter(
        model_image.TransformContinuousIndexToPhysicalPoint(
            [((dimension - 1) / 2.0) for dimension in model_image.GetSize()]
        )
    )


# TODO: Create a separate version of this function for groups only (i.e., CLI only, no GUI)
# IMAGE_DICT is only for the GUI. No need for it for CLI
# However, we should have both IMAGE_DICT and IMAGE_GROUPS for GUI (GUI should inform user if they
# loaded images with different properties)
def put_paths_in_image_groups(path_list: list[Path]) -> None:
    """Given list[str] of paths, put each path (and corresponding sitk.Image) into global IMAGE_DICT
    and IMAGE_GROUPS.

    Must call AFTER initialize_globals() to make sure there's an existing MODEL_IMAGE in IMAGE_DICT.

    A sitk.Image matching the properties of MODEL_IMAGE is put into IMAGE_DICT. A sitk.Image matching
    the properties of a group in IMAGE_LIST is put into that group. Otherwise, a new group is created.

    :param path_list:
    :type path_list: list[Path]"""
    for path in path_list:
        new_img_properties: tuple = get_properties(path)
        for group in global_vars.IMAGE_GROUPS:
            if new_img_properties == group[0]:
                group[1].append(path)
        else:
            global_vars.IMAGE_GROUPS.append((new_img_properties, [path]))
    image_dict_paths: list[Path] = global_vars.IMAGE_GROUPS[0][1]
    for path in image_dict_paths:
        global_vars.READER.SetFileName(str(path))
        global_vars.IMAGE_DICT[path] = global_vars.READER.Execute()


# TODO: Add more properties
def get_properties(sitk_image_or_path: Union[sitk.Image, Path]) -> tuple:
    """Tuple of properties of a sitk.Image or Path of an image.

    TODO: Add more properties
    
    :param img:
    :type img: sitk.Image
    :return: (dimensions, center of rotation used in EULER_3D_TRANSFORM, spacing)
    :rtype: tuple"""
    sitk_image = sitk_image_or_path
    if isinstance(sitk_image_or_path, Path):
        global_vars.READER.SetFileName(str(sitk_image_or_path))
        sitk_image = global_vars.READER.Execute()

    # Ignore the errors. sitk_image must be of type sitk.Image here
    return (
        sitk_image.GetSize(),
        sitk_image.TransformContinuousIndexToPhysicalPoint(
            [(dimension - 1) / 2.0 for dimension in sitk_image.GetSize()]
        ),
        sitk_image.GetSpacing(),
    )


# TODO: Might not be needed anymore but leaving it just in case
# def compare_img_properties(img1: sitk.Image, img2: sitk.Image) -> bool:
#     """Check whether two images have the same properties.

#     Properties checked defined in get_properties().

#     :param img1:
#     :type img1: sitk.Image
#     :param img2:
#     :type img2: sitk.Image
#     :return: True if `img1` and `img2` have the same properties, else False
#     :rtype: bool"""
#     # Tuple == operator checks deep equality, not reference equality
#     return get_properties(img1) == get_properties(img2)


def curr_path() -> Path:
    """Return the Path of the current image, i.e. global_vars.IMAGE_DICT.keys()[global_vars.INDEX]

    :return: Path of current image
    :rtype: Path"""
    return global_vars.IMAGE_DICT.keys()[global_vars.INDEX]


def curr_image() -> sitk.Image:
    """Return the image at the current index in global_vars.IMAGE_DICT.

    :return: current image
    :rtype: sitk.Image"""
    return global_vars.IMAGE_DICT[global_vars.IMAGE_DICT.keys()[global_vars.INDEX]]


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


def model_image_path() -> Path:
    """Get path of the model image.

    Since MODEL_IMAGE should always be the first image, internally returns the first key in the global
    IMAGE_DICT.

    :return: MODEL_IMAGE's Path
    :rtype: Path"""
    return global_vars.IMAGE_DICT.keys()[0]
