"""Global settings that the user should be able to modify directly, unlike global_vars.py and constants.py, via
JSON, GUI, CLI, etc.

Default values are what's in the config.json file.

The values in this file don't matter since they'll be overwritten by what's in config.json and then by CLI options,
if any. But the values here should match the values in config.json for consistency."""

from pathlib import Path
import src.utils.constants as constants

DEBUG: bool = False
"""Whether or not to print debugging information throughout execution."""

FILE_BROWSER_START_DIR: Path = constants.DATA_DIR
"""The starting directory that is opened in the file browser.

Defaults to DATA_DIR during development, for now.

Should default to user's home directory later."""

EXPORTED_FILE_NAMES_USE_INDEX: bool = False
"""If True, then exported files will be named using the index in the program.

E.g. 1_0_0_0_0.png, 2_90_180_0_60.csv, etc., where the first part is the file name and
the other parts are image settings.

If False (default), then exported files will be named using the file name of the original file.

E.g. MicroBiome_1month_T1w_0_0_0_0.png, MicroBiome_1month_T1w_90_180_0_60.csv."""

THEME_NAME: str = "dark-hct"
"""Name of theme in src/GUI/themes.

The full path to the .qss file is {constants.THEME_DIR}/{THEME_NAME}/stylesheet.qss."""

CONTOUR_COLOR: str = ""
"""Color of the contour. "" means it will be automatically determined by the value of THEME_NAME.

This can be a 6-hexit string rrggbb (don't prepend 0x) or a name (e.g. red, blue, etc.).

Internally, this is converted to a QColor using imgproc.string_to_QColor().
QColor supports 8-hexit rrggbbaa but doesn't work in our GUI, i.e. aa=00 appears fully bright in the GUI."""

STARTUP_WIDTH_RATIO: float = 0.65
"""Max GUI width as fraction of primary monitor width. Configurable in JSON"""
STARTUP_HEIGHT_RATIO: float = 0.6
"""Max GUI height as fraction of primary monitor height. Configurable in JSON"""

DISPLAY_ADVANCED_MENU_MESSAGES_IN_TERMINAL: bool = False
"""Whether the advanced menu messages display in terminal or new window"""
