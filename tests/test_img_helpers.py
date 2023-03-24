import pytest
from pathlib import Path
import SimpleITK as sitk

import src.utils.constants as constants
from src.utils.img_helpers import *
import src.utils.global_vars as global_vars

IMAGE_NAMES: list[str] = [
    'BCP_Dataset_2month_T1w.nrrd',
    'IBIS_Case1_V06_t1w_RAI.nrrd',
    'IBIS_Case2_V12_t1w_RAI.nrrd',
    'IBIS_Case3_V24_t1w_RAI.nrrd',
    'IBIS_Dataset_12month_T1w.nrrd',            # Group 1: 0-4
    'IBIS_Dataset_NotAligned_6month_T1w.nrrd',  # Group 2: 5
    'MicroBiome_1month_T1w.nii.gz',             # Group 3: 6
]

IMAGE_PATHS: list[Path] = [
    constants.EXAMPLE_DATA_DIR / path_str for path_str in IMAGE_NAMES
]

IMAGE_DICT: dict[Path, sitk.Image] = dict()

for path in IMAGE_PATHS:
    global_vars.READER.SetFileName(str(path))
    IMAGE_DICT[path] = global_vars.READER.Execute()

def test_setup():
    clear_globals()

def test_update_image_groups():
    clear_globals()
    assert len(global_vars.IMAGE_GROUPS) == 0
    update_image_groups(IMAGE_PATHS)
    assert len(global_vars.IMAGE_GROUPS) == 3
    clear_globals()
    update_image_groups(IMAGE_PATHS[:5])
    assert len(global_vars.IMAGE_GROUPS) == 1
    clear_globals()
    update_image_groups(IMAGE_PATHS[:6])
    assert len(global_vars.IMAGE_GROUPS) == 2

def test_curr_path():
    clear_globals()
    update_image_groups(IMAGE_PATHS)
    for i in range(4):
        next_img()
    assert curr_path() == IMAGE_PATHS[4]
    for i in range(2):
        next_img()
    # Since the group is only the first 5
    # Wraps around
    assert curr_path() == IMAGE_PATHS[1]
    next_img()
    assert curr_path() == IMAGE_PATHS[2]

def test_del_curr_img_delete_last():
    clear_globals()
    update_image_groups(IMAGE_PATHS)
    global_vars.CURR_IMAGE_INDEX = len(global_vars.IMAGE_GROUPS[0][1]) - 1
    del_curr_img()
    assert global_vars.CURR_IMAGE_INDEX == len(global_vars.IMAGE_GROUPS[0][1]) - 1
