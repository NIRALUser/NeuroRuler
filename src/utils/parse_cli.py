"""This is temporary code for parsing CLI args when starting the GUI.

We will start the app using python -m src.main or python -m main later (or an executable), not python -m src.GUI.main."""

import argparse


def parse_gui_cli():
    """Parse cli args using argparse, return parser.parse_args() to main()."""
    parser = argparse.ArgumentParser(usage='python -m [-s] src.GUI.main')
    parser.add_argument('-s', '--smooth',
                        help='smooth image before rendering',
                        action='store_true')
    args = parser.parse_args()
    return args
