"""Global variables and functions that change throughout program execution, unlike constants.py,
that the user should not be able to modify directly, unlike user_settings.py.

Can run this file as module (python -m src.utils.global_vars) to debug stuff."""

import SimpleITK as sitk
from pathlib import Path

IMAGE_GROUPS: dict[tuple, dict[Path, sitk.Image]] = dict()
"""Mapping from properties tuple to a group of images, where a group of images is a dict[Path, sitk.Image].

Each dictionary of images has the same properties, as defined by img_helpers.get_properties()

{
    properties tuple: dict[Path, sitk.Image]
    properties tuple: dict[Path, sitk.Image]
    ...
}

dict[Path, sitk.Image] is a group of images.
We could instead store list[sitk.Image], but dict allows us to avoid duplicate Paths easily.
Also, I don't think sitk.Image stores path.

The IMAGE_DICT group is by default the 0'th group in this list. If we want to be able to change batches in the GUI,
we can change CURR_BATCH_INDEX.

IMAGE_GROUPS[properties tuple] gets the dict[Path, sitk.Image] images corresponding to those properties.

IMAGE_GROUPS[list(IMAGE_GROUPS.keys())[0]] gets the first group of images (since dict maintains insertion order
in Python 3.7+, https://mail.python.org/pipermail/python-dev/2017-December/151283.html)."""

IMAGE_DICT: dict[Path, sitk.Image] = dict()
"""The current (i.e., loaded in GUI) group of images in IMAGE_GROUPS.

Since Python 3.7+, dicts maintain insertion order. Therefore, we can use CURR_IMAGE_INDEX for retrieval and deletion.

Use list(IMAGE_DICT.keys())[i] to return the i'th key in the dict, which can also index into the dict.
This may be slow but will be used only
in the GUI for insertion and deletion operations, which are uncommon, so should be okay.

All images in the dictionary always have matching properties, as defined by mri_image.get_properties.
This is due to the setup of IMAGE_GROUPS."""

CURR_IMAGE_INDEX: int = 0
"""Image of the current image in the current batch of images, which is a dict[Path, sitk.Image].

Typical use would be IMAGE_DICT[list(IMAGE_DICT.keys())[CURR_IMAGE_INDEX]] (or just use img_helpers functions),
which would return a sitk.Image."""

CURR_BATCH_INDEX: int = 0
"""TODO: Not implemented (idk if useful yet). For now, this is just 0 throughout the program.

It's meant to be the index of the current group/batch in IMAGE_GROUPS.
Indexing into IMAGE_GROUPS using this number
(IMAGE_GROUPS[list(IMAGE_GROUPS.keys())[CURR_BATCH_INDEX]])
will result in a dict of images.

Remember to update the center of EULER_3D_TRANSFORM if updating batch index!"""

READER: sitk.ImageFileReader = sitk.ImageFileReader()
"""Global `sitk.ImageFileReader`."""

EULER_3D_TRANSFORM: sitk.Euler3DTransform = sitk.Euler3DTransform()
"""Global sitk.Euler3DTransform for 3D rotations.

It is assumed that all currently loaded images have the same center of rotation. The center won't change
for the currently loaded batch of images.

Going to a different batch will change the center. Make sure to set it. Or encapsulate an Euler3DTransform for each batch.

Rotation values are the global rotation values in global_vars.py."""

THETA_X: int = 0
"""In degrees"""
THETA_Y: int = 0
"""In degrees"""
THETA_Z: int = 0
"""In degrees"""
SLICE: int = 0
"""0-indexed"""

# TODO: documentation
SETTINGS_VIEW_ENABLED: bool = True
"""Whether the user is able to adjust settings (settings screen) or not
(circumference and contoured image screen).

Used in src/GUI/main.py"""


def main():
    """For testing."""
    pass


if __name__ == "__main__":
    main()
