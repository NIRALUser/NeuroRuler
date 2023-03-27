"""Global variables and functions that change throughout program execution, unlike constants.py,
that the user should not be able to modify directly, unlike user_settings.py."""

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

The IMAGE_DICT group is by default the 0'th group in this list. If we want to be able to change batches,
we can change CURR_BATCH_INDEX.

IMAGE_GROUPS[list(IMAGE_GROUPS.keys())[0]] gets the first group of images (dict maintains insertion order
in Python 3.7+, https://mail.python.org/pipermail/python-dev/2017-December/151283.html)."""

IMAGE_DICT: dict[Path, sitk.Image] = dict()
"""The current (i.e., loaded in GUI) group of images in IMAGE_GROUPS.

Since Python 3.7+, dicts maintain insertion order. Therefore, we can use CURR_IMAGE_INDEX for retrieval and deletion.

Use list(IMAGE_DICT.keys())[i] to return the i'th key in the dict, which can also index into the dict.
Not sure about this operation's speed, but it's used only
in the GUI for insertion and deletion operations, should be fine.

All images in the dictionary have matching properties, as defined by mri_image.get_properties.
This is due to the setup of IMAGE_GROUPS."""

CURR_IMAGE_INDEX: int = 0
"""Image of the current image in the loaded batch of images, which is a dict[Path, sitk.Image].

You should probably use the helper functions in img_helpers instead of this (unless you're writing helper
functions)."""

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

Switching the batch will change the center. Make sure to set it. Or encapsulate an Euler3DTransform for each batch?

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
