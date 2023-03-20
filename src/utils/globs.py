"""Global variables and functions that change throughout program execution, unlike constants.py,
that the user should not be able to modify directly, unlike settings.py.

Can run this file as module (python -m src.utils.globs) to test stuff."""

import warnings
import functools
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


# Autodocumentation throws an error when this isn't here... which file still imports deprecated from globs???
# Source: https://stackoverflow.com/questions/2536307/decorators-in-the-python-standard-lib-deprecated-specifically
def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used."""

    @functools.wraps(func)
    def new_func(*args, **kwargs):
        warnings.simplefilter("always", DeprecationWarning)  # turn off filter
        warnings.warn(
            "Call to deprecated function {}.".format(func.__name__),
            category=DeprecationWarning,
            stacklevel=2,
        )
        warnings.simplefilter("default", DeprecationWarning)  # reset filter
        return func(*args, **kwargs)

    return new_func


def main():
    """For testing."""
    print(EXAMPLE_IMAGES)
    print(
        f"\nNumber of example images in {str(constants.EXAMPLE_DATA_DIR.name)}/: {len(EXAMPLE_IMAGES)}"
    )
    print(f"img.get_size(): {EXAMPLE_IMAGES[0].get_size()}")
    # Errors for some reason, but the return type of sitk.Image.GetSize() is tuple, tested in terminal
    # print(f'type(img.get_size()): {type(EXAMPLE_IMAGES[0].get_size())}')


if __name__ == "__main__":
    main()
