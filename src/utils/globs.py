"""Global variables.

Can run this file as module (python -m src.utils.globs) to test stuff."""

import warnings
import functools
from src.utils.mri_image import MRIImageList
from pathlib import Path

IMAGE_LIST: MRIImageList = MRIImageList()
SUPPORTED_EXTENSIONS = ('*.nii.gz', '*.nii', '*.nrrd')
EXAMPLE_DATA_DIR: Path = Path.cwd() / 'ExampleData'
EXAMPLE_IMAGE_PATHS = []

for type in SUPPORTED_EXTENSIONS:
    for path in EXAMPLE_DATA_DIR.glob(type):
        EXAMPLE_IMAGE_PATHS.append(path)

NUM_CONTOURS_IN_INVALID_SLICE: int = 10
"""If this number of contours or more is detected in a slice after processing (Otsu, largest component, etc.), then the slice is considered invalid."""


# Source: https://stackoverflow.com/questions/2536307/decorators-in-the-python-standard-lib-deprecated-specifically
def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used."""

    @functools.wraps(func)
    def new_func(*args, **kwargs):
        warnings.simplefilter('always', DeprecationWarning)  # turn off filter
        warnings.warn("Call to deprecated function {}.".format(func.__name__),
                      category=DeprecationWarning,
                      stacklevel=2)
        warnings.simplefilter('default', DeprecationWarning)  # reset filter
        return func(*args, **kwargs)

    return new_func

def main():
    """For testing."""
    for path in EXAMPLE_IMAGE_PATHS:
        print(path.parent.name + '/' + path.name)
    print(f'\nNumber of example images in {str(EXAMPLE_DATA_DIR.name)}: {len(EXAMPLE_IMAGE_PATHS)}')

if __name__ == "__main__":
    main()
