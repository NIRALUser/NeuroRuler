"""Global settings that the user should be able to modify via JSON or GUI."""

from pathlib import Path

DEBUG: bool = False
"""Whether or not to print debugging information throughout execution.

Defaults to False."""

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

CONTOUR_COLOR: str = 'b55162'
"""Color of the contour. Defaults to globs.APP_MAIN_COLOR = #b55162.

R 181 G 81 B 98

This can be a 6-hexit string rrggbb (don't prepend 0x) or a name (e.g. red, blue, etc.).

Internally, this is converted to a QColor using imgproc.string_to_QColor().

QColor supports 8-hexit rrggbbaa but doesn't work in our GUI, i.e. aa=00 appears fully bright in the GUI.

The problem likely lies in :code:`src.GUI.main.render_curr_slice()`."""

THEME_NAME: str = 'dark-hct'
"""Name of theme in src/GUI/themes.

Defaults to 'dark-hct'.

Configurable via -t, --theme.

The full path to the .qss file is {globs.THEME_DIR}/{THEME_NAME}/stylesheet.qss."""
