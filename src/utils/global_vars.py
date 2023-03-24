"""Global variables and functions that change throughout program execution, unlike constants.py,
that the user should not be able to modify directly, unlike user_settings.py.

Can run this file as module (python -m src.utils.global_vars) to debug stuff."""

from sortedcontainers import SortedDict
import SimpleITK as sitk

IMAGE_DICT: SortedDict = SortedDict()
"""Global mapping of unique and sorted Path to sitk.Image"""

INDEX: int = 0
"""Image of the current image in global IMAGE_DICT"""

READER: sitk.ImageFileReader = sitk.ImageFileReader()
"""Global `sitk.ImageFileReader`."""

MODEL_IMAGE: sitk.Image = sitk.Image()

EULER_3D_TRANSFORM: sitk.Euler3DTransform = sitk.Euler3DTransform()

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
