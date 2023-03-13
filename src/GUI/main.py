"""Entrypoint of GUI stuff."""

import sys
import pathlib
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.uic.load_ui import loadUi
from PyQt6.QtWidgets import QDialog, QApplication, QMainWindow, QFileDialog
import SimpleITK as sitk
from src.utils.mri_image import MRIImage, MRIImageList
from src.utils.imgproc_helpers import *

NRRD0_PATH = 'ExampleData/BCP_Dataset_2month_T1w.nrrd'
NRRD1_PATH = 'ExampleData/IBIS_Dataset_12month_T1w.nrrd'
NRRD2_PATH = 'ExampleData/IBIS_Dataset_NotAligned_6month_T1w.nrrd'
NIFTI_PATH = 'ExampleData/MicroBiome_1month_T1w.nii.gz'

MAIN_WINDOW_INDEX = 0
CIRCUMFERENCE_WINDOW_INDEX = 1


class MainWindow(QMainWindow):

    image_list: MRIImageList = MRIImageList()
    
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi('src/GUI/main.ui', self)
        self.action_open.triggered.connect(self.browse_files)
        self.action_exit.triggered.connect(exit)
        self.next_button.clicked.connect(self.next_img)
        self.previous_button.clicked.connect(self.previous_img)
        self.apply_button.clicked.connect(self.goto_circumference)
        self.show()

    
    def browse_files(self):
        """This needs to be checked for compatibilty on Windows.
        
        The return value of `getOpenFileNames` is a tuple (list[str], str), where the left element is a list of paths.
        
        So fnames[0][i] is the i'th path selected."""
        # TODO: Let starting directory be a configurable setting in JSON
        files = QFileDialog.getOpenFileNames(self, 'Open file(s)', str(pathlib.Path.cwd()), 'MRI images (*.nii.gz *.nii *.nrrd)')
        paths = map(pathlib.Path, files[0])
        images = list(map(MRIImage, paths))
        self.image_list = MRIImageList(images)
        self.image.setEnabled(True)
        self.update_image()

    
    def goto_circumference(self):
        """Switch to CircumferenceWindow."""
        widget.setCurrentIndex(CIRCUMFERENCE_WINDOW_INDEX)
    

    # TODO: Finish this function after reworking MRIImage to encapsulate a sitk.Image, not a path
    def update_image(self):
        """Update the displayed image."""
        curr_image = self.image_list.get_curr_mri_image()
        # jpg for speed (compared to png). Not computing circumference from this.
        filepath = pathlib.Path('.') / 'img' / f'{self.image_list.get_index()}.jpg'
        save_sitk_slice_to_file(curr_image.resample(), filepath)
        self.image.setPixmap(QtGui.QPixmap(str(filepath)))

    def next_img(self):
        self.image_list.next()
        self.update_image()

    def previous_img(self):
        self.image_list.previous()
        self.update_image()

    
class CircumferenceWindow(QMainWindow):
    from src.utils.globs import IMAGE_LIST

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
