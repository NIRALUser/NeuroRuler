"""Parse config JSON and CLI arguments to set global settings in ``gui_settings.py`` and ``cli_settings.py``."""

# TODO: (Eric) I think most of this should be refactored into the CLI/GUI packages respectively,
# and we should just keep the general parse functions here

import argparse
import json
from pathlib import Path
import string

import NeuroRuler.utils.cli_settings as cli_settings
import NeuroRuler.utils.gui_settings as gui_settings
import NeuroRuler.utils.constants as constants
import NeuroRuler.utils.exceptions as exceptions

JSON_SETTINGS: dict = dict()
"""Dict of settings resulting from JSON file parsing. Global within this file."""


def parse_cli() -> None:
    """Parse CLI (non-GUI) args and set settings in ``cli_settings.py``.

    :return: None"""
    parser = argparse.ArgumentParser(
        prog="NeuroRuler",
        description="A program that calculates head circumference from MRI data (``.nii``, ``.nii.gz``, ``.nrrd``).",
    )

    parser.add_argument("-d", "--debug", help="print debug info", action="store_true")
    parser.add_argument(
        "-r", "--raw", help='print just the "raw" circumference', action="store_true"
    )
    parser.add_argument("-x", "--x", type=int, help="x rotation (in degrees)")
    parser.add_argument("-y", "--y", type=int, help="y rotation (in degrees)")
    parser.add_argument("-z", "--z", type=int, help="z rotation (in degrees)")
    parser.add_argument("-s", "--slice", type=int, help="slice (Z slice, 0-indexed)")
    parser.add_argument(
        "-c", "--conductance", type=float, help="conductance smoothing parameter"
    )
    parser.add_argument("-i", "--iterations", type=int, help="smoothing iterations")
    parser.add_argument(
        "-t", "--step", type=float, help="time step (smoothing parameter)"
    )
    parser.add_argument("-f", "--filter", help="which filter to use (Otsu or binary)")
    parser.add_argument(
        "-l", "--lower", type=float, help="lower threshold for binary threshold"
    )
    parser.add_argument(
        "-u", "--upper", type=float, help="upper threshold for binary threshold"
    )
    parser.add_argument("file", help="file to compute circumference from")
    args = parser.parse_args()

    if args.debug:
        cli_settings.DEBUG = True
        print("Debug CLI option supplied.")

    cli_settings.RAW = args.raw

    if args.x:
        cli_settings.THETA_X = args.x

    if args.y:
        cli_settings.THETA_Y = args.y

    if args.z:
        cli_settings.THETA_Z = args.z

    if args.slice:
        cli_settings.SLICE = args.slice

    if args.conductance:
        cli_settings.CONDUCTANCE_PARAMETER = args.conductance

    if args.iterations:
        cli_settings.SMOOTHING_ITERATIONS = args.iterations

    if args.step:
        cli_settings.TIME_STEP = args.step

    if args.filter:
        if args.filter.lower() == "otsu":
            cli_settings.THRESHOLD_FILTER = constants.ThresholdFilter.Otsu
        elif args.filter.lower() == "binary":
            if args.lower is None:
                print(
                    "Must specify lower binary threshold with CLI option if using binary threshold"
                )
                exit(1)
            if args.upper is None:
                print(
                    "Must specify upper binary threshold with CLI option if using binary threshold"
                )
                exit(1)
            cli_settings.THRESHOLD_FILTER = constants.ThresholdFilter.Binary
        else:
            print("Invalid setting entered for CLI filter option.")
            exit(1)

    if args.lower:
        cli_settings.LOWER_BINARY_THRESHOLD = args.lower

    if args.upper:
        cli_settings.UPPER_BINARY_THRESHOLD = args.upper

    # Would use pathlib.Path .suffix here
    # However, '.nii.gz'.suffix would return '.gz'
    # But we expect '.nii.gz'
    extension = args.file[args.file.find(".") :]
    if extension not in constants.SUPPORTED_IMAGE_EXTENSIONS:
        print(
            f"Image has an unsupported extension. Supported image extensions are {str(constants.SUPPORTED_IMAGE_EXTENSIONS)}."
        )
        exit(1)

    cli_settings.FILE = args.file


def parse_gui_cli() -> None:
    """Parse GUI CLI args and set settings in ``gui_settings.py``.

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
        gui_settings.DEBUG = True
        print("Debug CLI option supplied.")

    if args.export_index:
        gui_settings.EXPORTED_FILE_NAMES_USE_INDEX = True
        print("Exported files will use the index displayed in the GUI.")

    if args.theme:
        if args.theme not in constants.THEMES:
            print(
                f"Invalid theme specified. Options are {list_of_options_to_str(constants.THEMES)}"
            )
            exit(1)

        gui_settings.THEME_NAME = args.theme
        gui_settings.CONTOUR_COLOR = parse_main_color_from_theme_json()
        print(f"Theme {args.theme} specified.")

    if args.color:
        gui_settings.CONTOUR_COLOR = args.color
        print(
            f"Contour color is {'#' if not args.color.isalpha() else ''}{args.color}."
        )


def parse_cli_config() -> None:
    """Parse CLI JSON config and set user settings in gui_settings.py.

    load_json will load constants.JSON_CLI_CONFIG_PATH."""
    global JSON_SETTINGS
    JSON_SETTINGS = load_json(constants.JSON_CLI_CONFIG_PATH)
    cli_settings.DEBUG = parse_bool("DEBUG")
    if cli_settings.DEBUG:
        print("Printing debug messages.")

    cli_settings.RAW = parse_bool("RAW")
    cli_settings.THETA_X = parse_int("X")
    cli_settings.THETA_Y = parse_int("Y")
    cli_settings.THETA_Z = parse_int("Z")
    cli_settings.SLICE = parse_int("SLICE")
    cli_settings.CONDUCTANCE_PARAMETER = parse_float("CONDUCTANCE")
    cli_settings.SMOOTHING_ITERATIONS = parse_int("SMOOTHING")
    cli_settings.TIME_STEP = parse_float("TIME_STEP")
    if parse_str("THRESHOLD_FILTER").lower() == "otsu":
        cli_settings.THRESHOLD_FILTER = constants.ThresholdFilter.Otsu
    elif parse_str("THRESHOLD_FILTER").lower() == "binary":
        cli_settings.THRESHOLD_FILTER = constants.ThresholdFilter.Binary
    else:
        raise exceptions.InvalidJSONField("THRESHOLD_FILTER", "str")
    cli_settings.LOWER_BINARY_THRESHOLD = parse_float("LOWER_BINARY_THRESHOLD")
    cli_settings.UPPER_BINARY_THRESHOLD = parse_float("UPPER_BINARY_THRESHOLD")


def parse_gui_config() -> None:
    """Parse GUI JSON config and set user settings in gui_settings.py.

    load_json will load constants.JSON_GUI_CONFIG_PATH."""
    global JSON_SETTINGS
    JSON_SETTINGS = load_json(constants.JSON_GUI_CONFIG_PATH)

    gui_settings.DEBUG = parse_bool("DEBUG")
    if gui_settings.DEBUG:
        print("Printing debug messages.")
    gui_settings.FILE_BROWSER_START_DIR = parse_path("FILE_BROWSER_START_DIR")
    gui_settings.EXPORTED_FILE_NAMES_USE_INDEX = parse_bool(
        "EXPORTED_FILE_NAMES_USE_INDEX"
    )

    gui_settings.THEME_NAME = JSON_SETTINGS["THEME_NAME"]
    if gui_settings.THEME_NAME not in constants.THEMES:
        raise exceptions.InvalidJSONField(
            "THEME_NAME", list_of_options_to_str(constants.THEMES)
        )

    contour_color: str = JSON_SETTINGS["CONTOUR_COLOR"]
    if contour_color == "":
        gui_settings.CONTOUR_COLOR = parse_main_color_from_theme_json()
    # A name, e.g. red, green, blue. etc., which can be converted to a QColor
    elif contour_color.isalpha():
        gui_settings.CONTOUR_COLOR = contour_color
    elif len(contour_color) == 6 and all(
        char in string.hexdigits for char in contour_color
    ):
        gui_settings.CONTOUR_COLOR = contour_color
    else:
        raise exceptions.InvalidJSONField(
            "CONTOUR_COLOR",
            'Name (e.g., "red", "blue") or 6-hexit color code "RRGGBB" or "" (empty string) '
            "to set a default color based on theme",
        )

    gui_settings.STARTUP_WIDTH_RATIO = parse_float("STARTUP_WIDTH_RATIO")
    gui_settings.STARTUP_HEIGHT_RATIO = parse_float("STARTUP_HEIGHT_RATIO")
    gui_settings.DISPLAY_ADVANCED_MENU_MESSAGES_IN_TERMINAL = parse_bool(
        "DISPLAY_ADVANCED_MENU_MESSAGES_IN_TERMINAL"
    )


def parse_main_color_from_theme_json() -> str:
    """Parse the main color from the theme JSON file (user_settings.THEME_NAME) in the highlight field.

    Uses user_settings.THEME_NAME so must be called after parse_gui_config sets user_settings.THEME_NAME
    (i.e. can be called within parse_gui_config).

    :return: main color rrggbb (hexits)
    :rtype: str"""
    path_to_theme_json: Path = (
        constants.THEME_DIR
        / gui_settings.THEME_NAME
        / (gui_settings.THEME_NAME + ".json")
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


def parse_str(field: str) -> str:
    """For str field, return the str.

    :param field: JSON field
    :type field: ````str````
    :return: string
    :rtype: ````str````"""
    try:
        return JSON_SETTINGS[field]
    except:
        raise exceptions.InvalidJSONField(field, "str")


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
