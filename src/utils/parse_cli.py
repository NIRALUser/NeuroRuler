"""Parse CLI arguments."""

import argparse
import src.utils.settings as settings


def parse_gui_cli() -> None:
    """Parse GUI CLI args.

    Sets global settings in `settings.py`."""
    parser = argparse.ArgumentParser(usage='python -m [-s] [-e] [-f] src.GUI.main')
    parser.add_argument('-s', '--smooth',
                        help='smooth image before rendering (False by default)',
                        action='store_true')
    parser.add_argument('-e', '--export_index',
                        help='exported filenames will use the index displayed in the GUI',
                        action='store_true')
    parser.add_argument('-f', '--fullpath',
                        help='image status bar will show full path',
                        action='store_true')
    args = parser.parse_args()

    if args.smooth:
        settings.SMOOTH_BEFORE_RENDERING = True
        print('Smooth CLI option supplied.')
    if args.export_index:
        settings.EXPORTED_FILE_NAMES_USE_INDEX = True
        print('Exported files will use the index displayed in the GUI.')
    if args.fullpath:
        settings.IMAGE_STATUS_BAR_SHOWS_FULL_PATH = True
        print('Image status bar will show full path to image.')
