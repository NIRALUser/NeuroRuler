from NeuroRuler.utils.img_helpers import *
import NeuroRuler.utils.global_vars as global_vars

IMAGE_NAMES: list[str] = [
    "BCP_Dataset_2month_T1w.nrrd",
    "IBIS_Case1_V06_t1w_RAI.nrrd",
    "IBIS_Case2_V12_t1w_RAI.nrrd",
    "IBIS_Case3_V24_t1w_RAI.nrrd",
    "IBIS_Dataset_12month_T1w.nrrd",  # Group 1: 0-4
    "IBIS_Dataset_NotAligned_6month_T1w.nrrd",  # Group 2: 5
    "MicroBiome_1month_T1w.nii.gz",  # Group 3: 6
]

IMAGE_PATHS: list[Path] = [constants.DATA_DIR / path_str for path_str in IMAGE_NAMES]

IMAGE_DICT: dict[Path, sitk.Image] = dict()

for path in IMAGE_PATHS:
    global_vars.READER.SetFileName(str(path))
    IMAGE_DICT[path] = global_vars.READER.Execute()

GROUP_1: list[sitk.Image] = [IMAGE_DICT[k] for k in IMAGE_PATHS[:5]]
GROUP_2: list[sitk.Image] = [IMAGE_DICT[IMAGE_PATHS[5]]]
GROUP_3: list[sitk.Image] = [IMAGE_DICT[IMAGE_PATHS[6]]]


def test_setup():
    clear_globals()


def test_hashing():
    """Test that the properties tuples for the 5 images in group 1 are all the same
    but different from the properties tuple for group 2 and group 3."""
    first_group_hash = hash(get_properties_from_sitk_image(GROUP_1[0]))
    second_group_hash = hash(get_properties_from_sitk_image(GROUP_2[0]))
    third_group_hash = hash(get_properties_from_sitk_image(GROUP_3[0]))
    assert all(
        hash(get_properties_from_sitk_image(img)) == first_group_hash for img in GROUP_1
    )
    assert second_group_hash != third_group_hash
    assert first_group_hash != second_group_hash
    assert first_group_hash != third_group_hash


def test_curr_path():
    clear_globals()
    initialize_globals(IMAGE_PATHS)
    for i in range(4):
        next_img()
    assert get_curr_path() == IMAGE_PATHS[4]
    for i in range(2):
        next_img()
    # Since the group is only the first 5
    # Wraps around
    assert get_curr_path() == IMAGE_PATHS[1]
    next_img()
    assert get_curr_path() == IMAGE_PATHS[2]


def test_del_curr_img_delete_last():
    clear_globals()
    initialize_globals(IMAGE_PATHS)
    global_vars.CURR_IMAGE_INDEX = len(global_vars.IMAGE_DICT) - 1
    del_curr_img()
    assert global_vars.CURR_IMAGE_INDEX == len(global_vars.IMAGE_DICT) - 1
