"""GUI settings set through command-line arguments and ``gui_config.json``.

Command-line arguments override the values in the JSON.

There shouldn't be any blank (empty string) values here
(like the blank values in ``gui_config.json`` that are set to default values by ``parser.py``)
because if parsing the GUI json fails (e.g., doesn't exist),
then we need an actual working value here."""

from pathlib import Path
import NeuroRuler.utils.constants as constants

DEBUG: bool = False
"""Whether or not to print debugging information throughout execution."""

FILE_BROWSER_START_DIR: Path = Path.cwd()
"""The starting directory that is opened in the file browser.

Defaults to cwd."""

EXPORTED_FILE_NAMES_USE_INDEX: bool = False
"""If True, then exported files will be named using the index in the program.

E.g. 1_0_0_0_0.png, 2_90_180_0_60.csv, etc., where the first part is the file name and
the other parts are image settings.

If False (default), then exported files will be named using the file name of the original file.

E.g. MicroBiome_1month_T1w_0_0_0_0.png, MicroBiome_1month_T1w_90_180_0_60.csv."""

THEME_NAME: str = "dark-nr"
"""Name of theme in NeuroRuler/GUI/themes.

The full path to the .qss file is {constants.THEME_DIR}/{THEME_NAME}/stylesheet.qss."""

CONTOUR_COLOR: str = "b55162"
"""Color of the contour.

This can be a 6-hexit string rrggbb (don't prepend 0x) or a name (e.g. red, blue, etc.).

Internally, this is converted to a QColor using imgproc.string_to_QColor().
QColor supports 8-hexit rrggbbaa but doesn't work in our GUI, i.e. aa=00 appears fully bright in the GUI."""

STARTUP_WIDTH_RATIO: float = 0.65
"""Max GUI width as fraction of primary monitor width. Configurable in JSON"""
STARTUP_HEIGHT_RATIO: float = 0.6
"""Max GUI height as fraction of primary monitor height. Configurable in JSON"""

DISPLAY_ADVANCED_MENU_MESSAGES_IN_TERMINAL: bool = False
"""Whether the advanced menu messages display in terminal or new window"""
