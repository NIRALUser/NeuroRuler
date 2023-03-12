"""Entrypoint of GUI stuff."""

import sys
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.uic.load_ui import loadUi
from PyQt6.QtWidgets import QDialog, QApplication, QMainWindow

MAIN_WINDOW_INDEX = 0
CIRCUMFERENCE_WINDOW_INDEX = 1

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi('Playground/GUI/main.ui', self)
        self.show()
        self.apply_button.clicked.connect(self.goto_circumference)

    
    def goto_circumference(self):
        widget.setCurrentIndex(CIRCUMFERENCE_WINDOW_INDEX)


class CircumferenceWindow(QMainWindow):
    def __init__(self):
        super(CircumferenceWindow, self).__init__()
        loadUi('Playground/GUI/circumference.ui', self)
        self.show()
        self.adjust_slice_button.clicked.connect(self.goto_main)

    
    def goto_main(self):
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
