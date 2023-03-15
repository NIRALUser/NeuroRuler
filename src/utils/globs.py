"""Global variables.

Note: For some reason, can't do from src.utils.globs import IMAGE_LIST in GUI/main.py or utils/imgproc.py or things break.

Idk why. But import src.utils.globs as globs works fine."""

import warnings
import functools
from src.utils.mri_image import MRIImageList

IMAGE_LIST: MRIImageList = MRIImageList()

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
