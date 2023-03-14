"""Global variables.

Note: For some reason, can't do from src.utils.globs import IMAGE_LIST in GUI/main.py or utils/imgproc.py or things break.

Idk why. But import src.utils.globs as globs works fine."""

from src.utils.mri_image import MRIImageList
import pathlib

IMAGE_LIST: MRIImageList = MRIImageList()

# Since QPixmap doesn't support rendering from a sitk.Image or np.ndarray, must save images as jpg/png
# https://doc.qt.io/qtforpython-5/PySide2/QtGui/QPixmap.html
IMG_DIR: pathlib.Path = pathlib.Path('.') / 'img'
"""Directory used to save f'{i}.{IMAGE_EXTENSION}' files corresponding to the currently open images, where `i` is the index (zero-indexed) of the image.

Files will need to be renamed during Add Image or Delete Image operations."""
IMAGE_EXTENSION: str = 'jpg'
"""Extension for images stored in `IMG_DIR`."""
