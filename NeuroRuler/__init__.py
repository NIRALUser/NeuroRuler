"""After installing NeuroRuler via pip, the functions here are importable like so

from NeuroRuler import {function}

where NeuroRuler is the name of the package this __init__.py file is in."""

import sys
import os
import NeuroRuler.CLI.main as climain
import NeuroRuler.GUI.main as guimain
import NeuroRuler.utils.parser as parser


def cli() -> None:
    """Run CLI."""
    parser.parse_config_json()
    parser.parse_cli()
    climain.main()


def gui() -> None:
    """Start GUI."""
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
    # myappid: Use unicode
    import ctypes

    myappid = "mycompany.myproduct.subproduct.version"  # arbitrary string
    try:
        # For Windows.
        # App icon works without this on macOS.
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except:
        pass

    parser.parse_config_json()
    parser.parse_gui_cli()
    guimain.main()
