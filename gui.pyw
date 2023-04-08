#!/usr/bin/env python3

# Note: If changing this file, mirror the changes into gui.py
# Windows users should be able to double-click this file to run it without a terminal popping up
# Currently doesn't work, though

import sys
import os

# Source: https://stackoverflow.com/questions/5047734/in-osx-change-application-name-from-python
if sys.platform.startswith("darwin"):
    # Set app name, if PyObjC is installed
    # Python 2 has PyObjC preinstalled
    # Python 3: pip3 install pyobjc-framework-Cocoa
    try:
        from Foundation import NSBundle

        bundle = NSBundle.mainBundle()
        if bundle:
            app_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
            app_info = bundle.localizedInfoDictionary() or bundle.infoDictionary()
            if app_info:
                app_info["CFBundleName"] = app_name
    except ImportError:
        pass

# Source: https://stackoverflow.com/questions/1551605/how-to-set-applications-taskbar-icon-in-windows-7/1552105#1552105
import ctypes

myappid = u"mycompany.myproduct.subproduct.version"  # arbitrary string
try:
    # For Windows. App icon works without this on macOS.
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except:
    pass

from src.GUI.main import main
from src.utils.parser import parse_json, parse_gui_cli
parse_json()
parse_gui_cli()
main()
