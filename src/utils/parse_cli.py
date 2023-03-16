"""This is temporary code for parsing CLI args when starting the GUI.

We will start the app using python -m src.main or python -m main later (or an executable), not python -m src.GUI.main."""

import argparse
import src.utils.settings as settings


def parse_gui_cli() -> None:
    """Parse GUI CLI args."""
    parser = argparse.ArgumentParser(usage='python -m [-s] [-e] src.GUI.main')
    parser.add_argument('-s', '--smooth',
                        help='smooth image before rendering (False by default)',
                        action='store_true')
    parser.add_argument('-e', '--export_index',
                        help='exported filenames will use the index displayed in the GUI',
                        action='store_true')
    args = parser.parse_args()

    if args.smooth:
        settings.SMOOTH_BEFORE_RENDERING = True
        print('Smooth CLI option supplied.')
    if args.export_index:
        settings.EXPORTED_FILE_NAMES_USE_INDEX = True
        print('Exported files will use the index displayed in the GUI.')
