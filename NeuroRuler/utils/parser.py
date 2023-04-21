"""Parse config JSON and CLI arguments to set global settings."""

import argparse
import json
from pathlib import Path
import string

import NeuroRuler.utils.user_settings as user_settings
import NeuroRuler.utils.constants as constants
import NeuroRuler.utils.exceptions as exceptions
import pkg_resources

JSON_SETTINGS: dict = dict()
"""Dict of settings resulting from JSON file parsing. Global within this file."""


def parse_gui_cli() -> None:
    """Parse GUI CLI args and set global settings in `user_settings.py`.

    :return: None"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", help="print debug info", action="store_true")
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
        user_settings.CONTOUR_COLOR = parse_main_color_from_theme_json()
        print(f"Theme {args.theme} specified.")

    if args.color:
        user_settings.CONTOUR_COLOR = args.color
        print(
            f"Contour color is {'#' if not args.color.isalpha() else ''}{args.color}."
        )


def parse_config_json() -> None:
    """Parse config JSON and set user settings in user_settings.py.

    load_json will load constants.JSON_CONFIG_PATH."""
    global JSON_SETTINGS
    JSON_SETTINGS = load_json(constants.JSON_CONFIG_PATH)
    if len(JSON_SETTINGS) != constants.EXPECTED_NUM_FIELDS_IN_JSON:
        raise Exception(
            f"Expected {constants.EXPECTED_NUM_FIELDS_IN_JSON} rows in JSON file but found {len(JSON_SETTINGS)}."
        )

    user_settings.DEBUG = parse_bool("DEBUG")
    if user_settings.DEBUG:
        print("Printing debug messages.")
    user_settings.FILE_BROWSER_START_DIR = parse_path("FILE_BROWSER_START_DIR")
    user_settings.EXPORTED_FILE_NAMES_USE_INDEX = parse_bool(
        "EXPORTED_FILE_NAMES_USE_INDEX"
    )

    user_settings.THEME_NAME = JSON_SETTINGS["THEME_NAME"]
    if user_settings.THEME_NAME not in constants.THEMES:
        raise exceptions.InvalidJSONField(
            "THEME_NAME", list_of_options_to_str(constants.THEMES)
        )

    contour_color: str = JSON_SETTINGS["CONTOUR_COLOR"]
    if contour_color == "":
        user_settings.CONTOUR_COLOR = parse_main_color_from_theme_json()
    # A name, e.g. red, green, blue. etc., which can be converted to a QColor
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


def parse_main_color_from_theme_json() -> str:
    """Parse the main color from the theme JSON file (user_settings.THEME_NAME) in the highlight field.

    Uses user_settings.THEME_NAME so must be called after parse_config_json sets user_settings.THEME_NAME
    (i.e. can be called within parse_config_json).

    :return: main color rrggbb (hexits)
    :rtype: str"""
    path_to_theme_json: Path = (
        constants.THEME_DIR
        / user_settings.THEME_NAME
        / (user_settings.THEME_NAME + ".json")
    )
    theme_json: dict = load_json(path_to_theme_json)
    color: str = theme_json["highlight"]
    if len(color) == 7:
        return color[1:]
    else:
        if "rgba(" not in color:
            raise Exception(
                f"{path_to_theme_json} has an invalid highlight field. Must be #rrggbb or rgba(r, g, b, a) (decimal)"
            )
        color = color.replace("rgba(", "").replace(")", "")
        channels: list[str] = color.split(",")
        r, g, b = int(channels[0]), int(channels[1]), int(channels[2])
        r, g, b = hex(r)[2:].zfill(2), hex(g)[2:].zfill(2), hex(b)[2:].zfill(2)
        return r + g + b


# Source: https://github.com/Alexhuszagh/BreezeStyleSheets/blob/main/configure.py#L82
def load_json(path: Path) -> dict:
    """Load config.json file, ignoring comments //.

    Source: https://github.com/Alexhuszagh/BreezeStyleSheets/blob/main/configure.py#L82

    :param path: path to JSON configuration file
    :type path: Path
    :return: JSON represented as dict
    :rtype: dict
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
    if JSON_SETTINGS[field] != "True" and JSON_SETTINGS[field] != "False":
        raise exceptions.InvalidJSONField(
            field, 'bool ("True" or "False", with quotation marks)'
        )
    return True if JSON_SETTINGS[field] == "True" else False


def parse_path(field: str) -> Path:
    """For path field, return a Path.

    :param field: JSON field
    :type field: str
    :raise: exceptions.InvalidJSONField
    :return:
    :rtype: Path"""
    try:
        return Path(JSON_SETTINGS[field])
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
        return int(JSON_SETTINGS[field])
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
        return float(JSON_SETTINGS[field])
    except:
        raise exceptions.InvalidJSONField(field, "float")


def list_of_options_to_str(strs: list[str]) -> str:
    r"""Convert list[str] of options of the form ['a', 'b', 'c', 'd'] to str representation
    "a", "b", "c", or "d"

    :param strs:
    :type strs: list[str]
    :return: str representation "a", "b", "c", or "d"
    :rtype: str"""
    # Need at least 1 comma in the list
    assert len(strs) > 2
    s = str(strs)[1:-1].replace("'", '"')
    final_comma_position: int = s.rfind(",")
    return s[: final_comma_position + 1] + " or " + s[final_comma_position + 2 :]
