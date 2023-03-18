"""Parse CLI arguments."""

from PyQt6 import QtGui
import argparse
import src.utils.settings as settings
import src.utils.globs as globs


def parse_gui_cli() -> None:
    """Parse GUI CLI args.

    Sets global settings in `settings.py`."""
    parser = argparse.ArgumentParser(usage='python -m [-h] [-d] [-s] [-e] [-f] [-t THEME] [-c COLOR] src.GUI.main')
    parser.add_argument('-d', '--debug',
                        help='print debug info',
                        action='store_true')
    parser.add_argument('-s', '--smooth',
                        help='smooth image before rendering',
                        action='store_true')
    parser.add_argument('-e', '--export-index',
                        help='exported filenames will use the index displayed in the GUI',
                        action='store_true')
    parser.add_argument('-f', '--full-path',
                        help='image status bar will show full path',
                        action='store_true')
    parser.add_argument('-t', '--theme',
                        help='configure theme, options are dark-hct, light-hct, dark, light')
    parser.add_argument('-c', '--color',
                        help='contour color as name (e.g. red) or hex rrggbb')
    args = parser.parse_args()

    if args.debug:
        settings.DEBUG = True
        print('Debug CLI option supplied.')
    if args.smooth:
        settings.SMOOTH_BEFORE_RENDERING = True
        print('Smooth CLI option supplied.')
    if args.export_index:
        settings.EXPORTED_FILE_NAMES_USE_INDEX = True
        print('Exported files will use the index displayed in the GUI.')
    if args.full_path:
        settings.IMAGE_STATUS_BAR_SHOWS_FULL_PATH = True
        print('Image status bar will show full path to image.')
    if args.theme:
        if args.theme not in globs.THEMES:
            print(f'Invalid theme specified. Options are {globs.THEMES}.')
            exit(1)
        settings.THEME_NAME = args.theme
        print(f'Theme {args.theme} specified.')
    if args.color:
        settings.CONTOUR_COLOR = args.color
        print(f"Contour color is {'#' if not args.color.isalpha() else ''}{args.color}.")
