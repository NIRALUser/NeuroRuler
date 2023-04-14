"""After installing NeuroRuler via pip, the functions here are importable like so

from {package_name} import gui

Currently, the package name is GUI (TODO: Change this)"""

import sys
import os
import src.GUI.main as main
import src.utils.parser as parser


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
        # For Windows. App icon works without this on macOS.
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except:
        pass

    parser.parse_config_json()
    parser.parse_gui_cli()
    main.main()


def GUI() -> None:
    """Alias for gui()."""
    gui()
