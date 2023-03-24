"""Global variables and functions that change throughout program execution, unlike constants.py,
that the user should not be able to modify directly, unlike user_settings.py.

Can run this file as module (python -m src.utils.global_vars) to debug stuff."""

import SimpleITK as sitk
from pathlib import Path

IMAGE_GROUPS: list[tuple[tuple, dict[Path, sitk.Image]]] = list()
"""List of groups of Paths of images. Each group has the same properties,
as defined by mri_image.validate_image.

[
    (properties tuple, dict[Path, sitk.Image])
    (properties tuple, dict[Path, sitk.Image])
    ...
]

A single group is
    (properties tuple, dict[Path, sitk.Image])
and all sitk.Image in that tuple have the same properties, as defined by mri_image.get_properties

dict[Path, sitk.Image] is an images dict.
We could instead store (properties tuple, list[sitk.Image]), but dict allows us to avoid duplicate Paths.
Also, I don't think sitk.Image stores path.

The IMAGE_DICT group is by default the first group in this list. If we want to be able to change batches in the GUI,
we can modify mutate IMAGE_DICT to point to a different group's dict.

IMAGE_GROUPS[i] gets (properties of group i, images dict)

IMAGE_GROUPS[i][0] gets (properties of group i)

IMAGE_GROUPS[i][1] gets group i's images dict."""

IMAGE_DICT: dict[Path, sitk.Image] = dict()
"""Global mapping of unique Path to sitk.Image. The current (i.e., loaded in GUI) group of images in IMAGE_GROUPS.

The model image is always the first sitk.Image in the dictionary.

Since Python 3.7+, dicts maintain insertion order. Therefore, we can use INDEX for retrieval and deletion.

Use list(IMAGE_DICT.keys())[i] to return the i'th key in the dict. This may be slow but will be used only
in the GUI for insertion and deletion operations, which are uncommon, so should be okay.

All images in the dictionary always have matching properties, as defined by mri_image.get_properties.
This is due to the setup of IMAGE_GROUPS."""

CURR_IMAGE_INDEX: int = 0
"""Image of the current image in the current batch."""

CURR_BATCH_INDEX: int = 0
"""Index of the current group/batch in IMAGE_GROUPS."""

READER: sitk.ImageFileReader = sitk.ImageFileReader()
"""Global `sitk.ImageFileReader`."""

EULER_3D_TRANSFORM: sitk.Euler3DTransform = sitk.Euler3DTransform()
"""Global sitk.Euler3DTransform for 3D rotations.

It is assumed that all currently loaded images have the same center of rotation. The center won't change
for the currently loaded batch of images.

File > Open (a perhaps different batch) may change the center.

Rotation values are the global rotation values in global_vars.py."""

THETA_X: int = 0
"""In degrees"""
THETA_Y: int = 0
"""In degrees"""
THETA_Z: int = 0
"""In degrees"""
SLICE: int = 0
"""0-indexed"""


def main():
    """For testing."""
    pass


if __name__ == "__main__":
    main()
