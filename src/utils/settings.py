"""Global settings."""

from pathlib import Path

SMOOTH_BEFORE_RENDERING: bool = False
"""Whether or not to smooth the image before rendering, defaults to False.

Affects MRIImage.resample() and imgproc.contour()."""
IMG_DIR: Path = Path.cwd() / 'img'
"""Directory for storing images. Defaults to `./img/`."""
EXPORTED_FILE_NAMES_USE_INDEX: bool = False
"""If True, then exported files will be named using the index in the program.

E.g. 1_0_0_0_0.png, 2_90_180_0_60.csv, etc., where the first part is the file name and the other parts are settings.

If False (default), then exported files will be named using the file name of the original file.

E.g. MicroBiome_1month_T1w_0_0_0_0.png, MicroBiome_1month_T1w_90_180_0_60.csv."""

IMAGE_STATUS_BAR_SHOWS_FULL_PATH: bool = False
"""If False (default), the GUI will display only the file name of the image instead of the full path."""
