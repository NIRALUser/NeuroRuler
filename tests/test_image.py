"""Test Image and ImageList.

Note: After changing `MRIImage` to encapsulate an actual `sitk.Image`, the tests run slower.

This file doesn't test equality between `MRIImage.img` fields. I assume if the path is the same and I get `img` from the path when changing it, then the `img` will be the same.

TODO: Test this later."""

import pytest
import pathlib
from src.utils.mri_image import MRIImage, MRIImageList

NRRD0_PATH = pathlib.Path('ExampleData/BCP_Dataset_2month_T1w.nrrd')
NRRD1_PATH = pathlib.Path('ExampleData/IBIS_Dataset_12month_T1w.nrrd')
NRRD2_PATH = pathlib.Path('ExampleData/IBIS_Dataset_NotAligned_6month_T1w.nrrd')
NIFTI_PATH = pathlib.Path('ExampleData/MicroBiome_1month_T1w.nii.gz')

IMAGE_0 = MRIImage(NRRD0_PATH, 0, 0, 0, 0)
IMAGE_1 = MRIImage(NRRD1_PATH, 3, 2, 1, 0)
IMAGE_2 = MRIImage(NRRD2_PATH, 0, 1, 2, 3)

IMAGES = [IMAGE_0, IMAGE_1, IMAGE_2]

IMAGE_LIST = MRIImageList(IMAGES)

"""
===========
Image tests
===========
"""
def test_init_and_getters():
    assert IMAGE_0.get_path() == NRRD0_PATH
    assert IMAGE_0.get_theta_x() == 0
    assert IMAGE_0.get_theta_y() == 0
    assert IMAGE_0.get_theta_z() == 0
    assert IMAGE_0.get_slice_z() == 0

    assert IMAGE_1.get_path() == NRRD1_PATH
    assert IMAGE_1.get_theta_x() == 3
    assert IMAGE_1.get_theta_y() == 2
    assert IMAGE_1.get_theta_z() == 1
    assert IMAGE_1.get_slice_z() == 0

def test_image_repr():
    assert str(IMAGE_0) == f'MRIImage(\'{NRRD0_PATH}\', 0, 0, 0, 0)'

def test_setters():
    img = MRIImage(NRRD0_PATH)
    img.set_path(NRRD1_PATH)
    img.set_theta_x(1)
    img.set_theta_y(2)
    img.set_theta_z(3)
    img.set_slice_z(4)
    assert img.get_path() == NRRD1_PATH
    assert img.get_theta_x() == 1
    assert img.get_theta_y() == 2
    assert img.get_theta_z() == 3
    assert img.get_slice_z() == 4

def test_eq_and_neq():
    """`==` and `!=` check reference equality."""
    assert IMAGE_0 != IMAGE_1
    assert IMAGE_0 != IMAGE_2
    assert IMAGE_1 != IMAGE_2
    img = MRIImage(NRRD0_PATH, 0, 0, 0, 0)
    assert img != IMAGE_0
    assert img.equals(IMAGE_0)

def test_deepcopy():
    clone = IMAGE_2.deepcopy()
    assert clone.get_path() == NRRD2_PATH
    assert clone.get_theta_x() == 0
    assert clone.get_theta_y() == 1
    assert clone.get_theta_z() == 2
    assert clone.get_slice_z() == 3

    clone.set_path(NRRD0_PATH)
    clone.set_theta_x(1700)
    clone.set_theta_y(1800)
    clone.set_theta_z(1900)
    clone.set_slice_z(9001)

    assert clone.get_path() == NRRD0_PATH
    assert clone.get_theta_x() == 1700
    assert clone.get_theta_y() == 1800
    assert clone.get_theta_z() == 1900
    assert clone.get_slice_z() == 9001

    # Check that the original wasn't mutated
    assert IMAGE_2.get_path() == NRRD2_PATH
    assert IMAGE_2.get_theta_x() == 0
    assert IMAGE_2.get_theta_y() == 1
    assert IMAGE_2.get_theta_z() == 2
    assert IMAGE_2.get_slice_z() == 3

def test_equals_method():
    """`.equals()` checks for deep equality."""
    clone = IMAGE_2.deepcopy()
    assert clone != IMAGE_2
    assert clone.equals(IMAGE_2)

"""
===============
ImageList tests
===============
"""

def test_initialize_with_list_of_image():
    image_list = MRIImageList([MRIImage(NRRD0_PATH, 1, 1, 1, 1), MRIImage(NRRD0_PATH, 1, 1, 1, 1)])
    assert len(image_list) == 2
    image_list.append(MRIImage(NRRD0_PATH, 1, 1, 1, 1))
    assert len(image_list) == 3

def test_initialize_with_other_ImageList():
    other = MRIImageList([MRIImage(NRRD0_PATH, 1, 1, 1, 1), MRIImage(NRRD0_PATH, 1, 1, 1, 1)])
    assert len(MRIImageList(other)) == 2

def test_initialize_with_no_arg():
    image_list = MRIImageList()
    assert not len(image_list)
    image_list.append(MRIImage(NRRD0_PATH, 0, 0, 0, 0))
    assert len(image_list) == 1

def test_repr():
    assert str(IMAGE_LIST) == f'[MRIImage(\'{NRRD0_PATH}\', 0, 0, 0, 0), MRIImage(\'{NRRD1_PATH}\', 3, 2, 1, 0), MRIImage(\'{NRRD2_PATH}\', 0, 1, 2, 3)]'

# The invididual Image elements are not deep copied
# This is the same as normal Python behavior: https://stackoverflow.com/questions/19068707/does-a-slicing-operation-give-me-a-deep-or-shallow-copy
def test_get_item():
    assert IMAGE_LIST[0] == IMAGE_0
    assert IMAGE_LIST[1] == IMAGE_1
    assert IMAGE_LIST[2] == IMAGE_2

    # Elements inside are shallow copies
    clone = IMAGE_LIST[:]
    assert clone[0] == IMAGE_0
    assert clone[1] == IMAGE_1
    assert clone[2] == IMAGE_2

    slice = IMAGE_LIST[:2]
    assert len(slice) == 2
    assert slice[0] == IMAGE_0 and slice[1] == IMAGE_1

    # Test that slicing creates a reference to a cloned ImageList (but not the underlying elements)
    clone = IMAGE_LIST[:]
    clone.append(MRIImage(NRRD2_PATH))
    assert len(IMAGE_LIST) != len(clone)
    assert clone[0] == IMAGE_LIST[0]
    assert clone[1] == IMAGE_LIST[1]
    assert clone[2] == IMAGE_LIST[2]

def test_del_item():
    clone = IMAGE_LIST[:]
    with pytest.raises(IndexError):
        del clone[3]
    del clone[0]
    assert clone[0] == IMAGE_1
    assert clone[1] == IMAGE_2
    del clone[0]
    assert clone[0] == IMAGE_2
    del clone[0]
    with pytest.raises(IndexError):
        del clone[0]

def test_set_item():
    """Syntax error because ImageList.__getitem__ return type can't be Union[Image, ImageList].

    So after indexing, Python can't know before runtime that the return value will be ImageList or Image.
    
    But the `.equals()` method works at runtime."""
    clone = IMAGE_LIST[:]
    clone[0] = IMAGE_2.deepcopy()
    # Syntax error because ImageList.__getitem__ return type can't be Union[Image, ImageList]
    # But the method works
    assert clone[0].equals(IMAGE_2)
    assert clone[0] != IMAGE_2

    clone[1] = IMAGE_2
    assert clone[1] == IMAGE_2
    assert clone[1].equals(IMAGE_2)
