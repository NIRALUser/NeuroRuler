#!/usr/bin/env python3

# Note: If changing this file, mirror the changes into gui.pyw
# This file is meant to be run from the terminal via ./gui.py.
# Windows users can also double-click it, but a terminal would pop up

from src.GUI.main import main
from src.utils.parser import parse_json, parse_gui_cli

parse_json()
parse_gui_cli()
main()
