"""Global variables and functions that change throughout program execution, unlike constants.py,
that the user should not be able to modify directly, unlike user_settings.py.

Can run this file as module (python -m src.utils.global_vars) to debug stuff."""

from sortedcontainers import SortedDict
import SimpleITK as sitk
from pathlib import Path

IMAGE_DICT: SortedDict = SortedDict()
"""Global mapping of unique and sorted (i.e., the dictionary can be indexed by indices 0, 1, 2, ...) Path to
sitk.Image.

The first element is always the MODEL_IMAGE. All images in IMAGE_DICT.values() much match the properties
of MODEL_IMAGE, as defined by mri_image.validate_image."""

INDEX: int = 0
"""Image of the current image in global IMAGE_DICT"""

MODEL_IMAGE: sitk.Image = sitk.Image()
"""The prototypical image that all other images to be loaded in the GUI are compared to. All loaded images must have
the same properties (defined in mri_image.validate_image) as the model image.

Should always be the first loaded image (i.e., reset on deletions)."""

# TODO: Can optimize speed if this changes to list[tuple[tuple, list[tuple[Path, sitk.Image]]]]
IMAGE_GROUPS: list[tuple[tuple, list[Path]]] = []
"""List of groups of Paths of images. Each group has the same properties,
as defined by mri_image.validate_image.

Here is the meaning of the type:

[
    (properties tuple, [path1, path2, path3...])
    (properties tuple, [path1, path2, path3...])
]

A single group is ((properties), list[Path]), where (properties) is the tuple of properties
for the sitk.Images given by that list of Paths.

Includes the IMAGE_DICT group as its first group.

IMAGE_GROUPS[i] gets (properties of group i, list[Path])

IMAGE_GROUPS[i][0] gets (properties of group)

IMAGE_GROUPS[i][1] gets list[Path]."""

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
