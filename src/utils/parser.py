"""Parse config JSON and CLI arguments to set global settings."""

import argparse
import json
from pathlib import Path
import string

import src.utils.user_settings as user_settings
import src.utils.constants as constants
import src.utils.exceptions as exceptions

SETTINGS: dict = dict()
"""Dict of settings resulting from JSON file parsing. Global within this file."""


def parse_json() -> None:
    """Parse JSON and set user settings in user_settings.py.

    load_json will load constants.JSON_CONFIG_PATH."""
    global SETTINGS
    SETTINGS = load_json(constants.JSON_CONFIG_PATH)
    if len(SETTINGS) != constants.EXPECTED_NUM_FIELDS_IN_JSON:
        raise Exception(
            f"Expected {constants.EXPECTED_NUM_FIELDS_IN_JSON} rows in JSON file but found {len(SETTINGS)}."
        )

    user_settings.DEBUG = parse_bool("DEBUG")
    if user_settings.DEBUG:
        print("Printing debug messages.")
    user_settings.IMG_DIR = parse_path("IMG_DIR")
    user_settings.FILE_BROWSER_START_DIR = parse_path("FILE_BROWSER_START_DIR")
    user_settings.EXPORTED_FILE_NAMES_USE_INDEX = parse_bool(
        "EXPORTED_FILE_NAMES_USE_INDEX"
    )

    user_settings.THEME_NAME = SETTINGS["THEME_NAME"]
    if user_settings.THEME_NAME not in constants.THEMES:
        raise exceptions.InvalidJSONField(
            "THEME_NAME", list_of_options_to_str(constants.THEMES)
        )

    contour_color: str = SETTINGS["CONTOUR_COLOR"]
    if contour_color == "":
        user_settings.CONTOUR_COLOR = default_contour_color()
    elif contour_color.isalpha():
        user_settings.CONTOUR_COLOR = contour_color
    elif len(contour_color) == 6 and all(
        char in string.hexdigits for char in contour_color
    ):
        user_settings.CONTOUR_COLOR = contour_color
    else:
        raise exceptions.InvalidJSONField(
            "CONTOUR_COLOR",
            'Name (e.g., "red", "blue") or 6-hexit color code "RRGGBB" or "" (empty string) '
            "to set a default color based on theme",
        )

    user_settings.STARTUP_WIDTH_RATIO = parse_float("STARTUP_WIDTH_RATIO")
    user_settings.STARTUP_HEIGHT_RATIO = parse_float("STARTUP_HEIGHT_RATIO")
    user_settings.DISPLAY_ADVANCED_MENU_MESSAGES_IN_TERMINAL = parse_bool(
        "DISPLAY_ADVANCED_MENU_MESSAGES_IN_TERMINAL"
    )


# Source: https://github.com/Alexhuszagh/BreezeStyleSheets/blob/main/configure.py#L82
def load_json(path: Path) -> dict:
    """Load config.json file, ignoring comments //.

    Source: https://github.com/Alexhuszagh/BreezeStyleSheets/blob/main/configure.py#L82
    """
    with open(path) as f:
        lines = f.read().splitlines()
    lines = [i for i in lines if not i.strip().startswith("//")]
    return json.loads("\n".join(lines))


def parse_bool(field: str) -> bool:
    """For bool field "True" or "False", return the bool.

    :param field: JSON field
    :type field: str
    :raise: exceptions.InvalidJSONField if s is not "True" or "False"
    :return: True or False
    :rtype: bool"""
    if SETTINGS[field] != "True" and SETTINGS[field] != "False":
        raise exceptions.InvalidJSONField(
            field, 'bool ("True" or "False", with quotation marks)'
        )
    return True if SETTINGS[field] == "True" else False


def parse_path(field: str) -> Path:
    """For path field, return a Path.

    :param field: JSON field
    :type field: str
    :raise: exceptions.InvalidJSONField
    :return:
    :rtype: Path"""
    try:
        return Path(SETTINGS[field])
    except:
        raise exceptions.InvalidJSONField(field, "path")


def parse_int(field: str) -> int:
    """For int field, return int.

    :param field: JSON field
    :type field: str
    :raise: exceptions.InvalidJSONField
    :return:
    :rtype: int"""
    try:
        return int(SETTINGS[field])
    except:
        raise exceptions.InvalidJSONField(field, "int")


def parse_float(field: str) -> float:
    """For float field, return float.

    :param field: JSON field
    :type field: str
    :raise: exceptions.InvalidJSONField
    :return:
    :rtype: float"""
    try:
        return float(SETTINGS[field])
    except:
        raise exceptions.InvalidJSONField(field, "float")


def parse_gui_cli() -> None:
    """Parse GUI CLI args and set global settings in `user_settings.py`."""
    parser = argparse.ArgumentParser(
        usage="./gui.py [-h] [-d] [-s] [-e] [-t THEME] [-c COLOR]"
    )
    parser.add_argument("-d", "--debug", help="print debug info", action="store_true")
    parser.add_argument(
        "-s", "--smooth", help="smooth image before rendering", action="store_true"
    )
    parser.add_argument(
        "-e",
        "--export-index",
        help="exported file names use the index displayed in the GUI instead of the \
                        original file name",
        action="store_true",
    )
    parser.add_argument(
        "-t",
        "--theme",
        help="configure theme, options are "
        + list_of_options_to_str(constants.THEMES).replace('"', ""),
    )
    parser.add_argument(
        "-c",
        "--color",
        help="contour color as name (e.g. red) or hex color code rrggbb",
    )
    args = parser.parse_args()

    if args.debug:
        user_settings.DEBUG = True
        print("Debug CLI option supplied.")

    if args.export_index:
        user_settings.EXPORTED_FILE_NAMES_USE_INDEX = True
        print("Exported files will use the index displayed in the GUI.")

    if args.theme:
        if args.theme not in constants.THEMES:
            print(
                f"Invalid theme specified. Options are {list_of_options_to_str(constants.THEMES)}"
            )
            exit(1)

        user_settings.THEME_NAME = args.theme
        user_settings.CONTOUR_COLOR = default_contour_color()
        print(f"Theme {args.theme} specified.")

    if args.color:
        user_settings.CONTOUR_COLOR = args.color
        print(
            f"Contour color is {'#' if not args.color.isalpha() else ''}{args.color}."
        )


def list_of_options_to_str(strs: list[str]) -> str:
    r"""Convert list[str] of options of the form ['a', 'b', 'c', 'd'] to str representation
    "a", "b", "c", or "d" """
    # Need at least 1 comma in the list
    assert len(strs) > 2
    s = str(strs)[1:-1].replace("'", '"')
    final_comma_position: int = s.rfind(",")
    return s[: final_comma_position + 1] + " or " + s[final_comma_position + 2 :]


def default_contour_color() -> str:
    """Uses theme name to determine a default contour color.

    Only call after validating theme name so that a str (not None) must be returned.

    :return: color code "RRGGBB"
    :rtype: str"""
    if "hct" in user_settings.THEME_NAME:
        return constants.HCT_MAIN_COLOR
    elif user_settings.THEME_NAME == "dark":
        return constants.DARK_THEME_COLOR
    elif user_settings.THEME_NAME == "light":
        return constants.LIGHT_THEME_COLOR
