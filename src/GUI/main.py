"""Entrypoint of GUI stuff."""

import sys
import pathlib
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.uic.load_ui import loadUi
from PyQt6.QtWidgets import QDialog, QApplication, QMainWindow, QFileDialog

MAIN_WINDOW_INDEX = 0
CIRCUMFERENCE_WINDOW_INDEX = 1

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi('src/GUI/main.ui', self)
        self.action_open.triggered.connect(self.browse_files)
        self.action_exit.triggered.connect(exit)
        self.apply_button.clicked.connect(self.goto_circumference)
        self.show()

    
    def browse_files(self):
        """This needs to be checked for compatibilty on Windows.
        
        The return value of `getOpenFileNames` is a tuple (list[str], str), where the left element is a list of paths.
        
        So fnames[0][i] is the i'th path selected."""
        files = QFileDialog.getOpenFileNames(self, 'Open file(s)', str(pathlib.Path.home()), 'Images (*.nii, *.gz, *.nrrd)')
        paths: list[str] = files[0]

    
    def goto_circumference(self):
        """Switch to CircumferenceWindow."""
        widget.setCurrentIndex(CIRCUMFERENCE_WINDOW_INDEX)


class CircumferenceWindow(QMainWindow):
    def __init__(self):
        super(CircumferenceWindow, self).__init__()
        loadUi('src/GUI/circumference.ui', self)
        self.action_exit.triggered.connect(exit)
        self.adjust_slice_button.clicked.connect(self.goto_main)
        self.show()

    
    def goto_main(self):
        """Switch to MainWindow."""
        widget.setCurrentIndex(MAIN_WINDOW_INDEX)


def main() -> None:
    app = QApplication(sys.argv)
    global widget
    widget = QtWidgets.QStackedWidget()
    global main_window
    main_window = MainWindow()
    global circumference_window
    circumference_window = CircumferenceWindow()
    widget.addWidget(main_window)
    widget.addWidget(circumference_window)
    widget.setMinimumWidth(500)
    widget.setMinimumHeight(500)
    widget.show()

    try:
        sys.exit(app.exec())
    except:
        print("Exiting")


if __name__ == "__main__":
    main()
