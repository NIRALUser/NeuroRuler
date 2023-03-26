#!/usr/bin/env python3

# Note: If changing this file, mirror the changes into gui.pyw
# This file can be double-clicked on Windows to start without opening a terminal

from src.GUI.main import main
from src.utils.parser import parse_json, parse_gui_cli

parse_json()
parse_gui_cli()
main()
