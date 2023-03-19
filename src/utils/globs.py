"""Global variables and functions that change throughout program execution, unlike constants.py,
that the user should not be able to modify directly, unlike settings.py.

Can run this file as module (python -m src.utils.globs) to test stuff."""

import SimpleITK as sitk
import src.utils.constants as constants
from src.utils.mri_image import MRIImageList, MRIImage

IMAGE_LIST: MRIImageList = MRIImageList()
"""Global list of MRIImage."""

READER: sitk.ImageFileReader = sitk.ImageFileReader()
"""Global `sitk.ImageFileReader`."""

EXAMPLE_IMAGES: list[MRIImage] = []
"""`list[MRIImage]` formed from the data in `EXAMPLE_DATA_DIR`.

Would go in constants.py but the type annotation requires MRIImage to be imported."""
for extension in constants.SUPPORTED_EXTENSIONS:
    for path in constants.EXAMPLE_DATA_DIR.glob(extension):
        EXAMPLE_IMAGES.append(MRIImage(path))


def main():
    """For testing."""
    print(EXAMPLE_IMAGES)
    print(f'\nNumber of example images in {str(constants.EXAMPLE_DATA_DIR.name)}/: {len(EXAMPLE_IMAGES)}')
    print(f'img.get_size(): {EXAMPLE_IMAGES[0].get_size()}')
    # Errors for some reason, but the return type of sitk.Image.GetSize() is tuple, tested in terminal
    # print(f'type(img.get_size()): {type(EXAMPLE_IMAGES[0].get_size())}')


if __name__ == "__main__":
    main()
