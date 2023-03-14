"""This is temporary code for parsing CLI args when starting the GUI.

We will start the app using python -m src.main or python -m main later (or an executable), not python -m src.GUI.main."""

import argparse

def parse_cli():
    """Parse cli args using argparse, return parser.parse_args() to main()."""
    parser = argparse.ArgumentParser(usage='python -m [-h] [-p] [-n] src.GUI.main\nYou should run with only one of these flags.')
    parser.add_argument('-j', '--jpg',
                        help='store jpg to disk for image rendering',
                        action='store_true')
    parser.add_argument('-p', '--png',
                        help='store png to disk for image rendering',
                        action='store_true')
    parser.add_argument('-n', '--np',
                        help='in-memory numpy arrays only, don\'t store anything to disk',
                        action='store_true')
    args = parser.parse_args()
    return args 
