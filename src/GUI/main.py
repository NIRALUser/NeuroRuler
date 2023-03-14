"""Entrypoint of GUI stuff.

Note: This file contains lots of fake syntax errors because PyQt object names don't exist until after `loadUi()`.

A lot of the functions defined here belong in imgproc_helpers. Should refactor later, but need to make sure the global `globs.IMAGE_LIST` is accessible there.

Lastly, there's a lot of methods here that get the current slice (not resample). Isn't too inefficient but could be improved. TODO: Make current slice global?"""

import sys
import pathlib
import numpy as np
import SimpleITK as sitk
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import QDialog, QApplication, QMainWindow, QFileDialog
from PyQt6.uic.load_ui import loadUi
from src.utils.mri_image import MRIImage, MRIImageList
import src.utils.imgproc as imgproc
import src.utils.globs as globs

DEFAULT_WIDTH: int = 1000
"""Startup width of the GUI"""
DEFAULT_HEIGHT: int = 700
"""Startup height of the GUI"""

NRRD0_PATH: pathlib.Path = pathlib.Path('ExampleData') / 'BCP_Dataset_2month_T1w.nrrd'
NRRD1_PATH: pathlib.Path = pathlib.Path('ExampleData') / 'IBIS_Dataset_12month_T1w.nrrd'
NRRD2_PATH: pathlib.Path = pathlib.Path('ExampleData') / 'IBIS_Dataset_NotAligned_6month_T1w.nrrd'
NIFTI_PATH: pathlib.Path = pathlib.Path('ExampleData') / 'MicroBiome_1month_T1w.nii.gz'

MAIN_WINDOW_INDEX = 0
CIRCUMFERENCE_WINDOW_INDEX = 1

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi(str(pathlib.Path('.') / 'src' / 'GUI' / 'main.ui'), self)
        self.setWindowTitle('Head Circumference Tool')
        self.action_open.triggered.connect(self.browse_files)
        self.action_exit.triggered.connect(exit)
        self.next_button.clicked.connect(self.next_img)
        self.previous_button.clicked.connect(self.previous_img)
        self.apply_button.clicked.connect(self.goto_circumference)
        self.x_slider.valueChanged.connect(self.rotate_x)
        self.y_slider.valueChanged.connect(self.rotate_y)
        self.z_slider.valueChanged.connect(self.rotate_z)
        self.slice_slider.valueChanged.connect(self.slice_update)
        self.reset_button.clicked.connect(self.reset_settings)
        self.show()

    def browse_files(self):
        """This needs to be checked for compatibility on Windows.
        
        The return value of `getOpenFileNames` is a tuple `(list[str], str)`, where the left element is a list of paths.
        
        So `fnames[0][i]` is the i'th path selected."""
        # TODO: Let starting directory be a configurable setting in JSON
        files = QFileDialog.getOpenFileNames(self, 'Open file(s)', str(pathlib.Path.cwd()),
                                             'MRI images (*.nii.gz *.nii *.nrrd)')
        paths = map(pathlib.Path, files[0])
        images = list(map(MRIImage, paths))
        globs.IMAGE_LIST = MRIImageList(images)
        self.enable_elements()
        self.render_curr_slice()
        self.render_all_sliders()

    def goto_circumference(self):
        """Switch to CircumferenceWindow.
        
        Compute circumference and update slice settings."""
        curr_mri_image: MRIImage = globs.IMAGE_LIST.get_curr_mri_image()
        widget.setCurrentIndex(CIRCUMFERENCE_WINDOW_INDEX)
        circumference_window.render_curr_slice()
        circumference: float = imgproc.get_contour_length(
            imgproc.get_contour(curr_mri_image.get_rotated_slice()))
        circumference_window.ui.circumference_label.setText(f'Circumference: {circumference}')
        circumference_window.ui.slice_settings_text.setText(
            f'X rotation: {curr_mri_image.get_theta_x()}°\nY rotation: {curr_mri_image.get_theta_y()}°\nZ rotation: {curr_mri_image.get_theta_z()}°\nSlice: {curr_mri_image.get_slice_z()}')

    def enable_elements(self):
        """Enable image, buttons, and sliders. Called when Open is pressed."""
        self.image.setEnabled(True)
        self.image_num_label.setEnabled(True)
        self.previous_button.setEnabled(True)
        self.next_button.setEnabled(True)
        self.apply_button.setEnabled(True)
        self.x_slider.setEnabled(True)
        self.y_slider.setEnabled(True)
        self.z_slider.setEnabled(True)
        self.slice_slider.setEnabled(True)
        self.reset_button.setEnabled(True)

    def render_curr_slice(self):
        """Same as `CircumferenceWindow.render_curr_slice()`.
        
        Also sets text for `image_num_label` and file path in the status bar tooltip."""
        curr_mri_image: MRIImage = globs.IMAGE_LIST.get_curr_mri_image()
        slice: sitk.Image = curr_mri_image.get_rotated_slice()
        print(f'sitk.Image data type: {slice.GetPixelIDTypeAsString()}')
        # sitk: 16-bit signed integer
        index: int = globs.IMAGE_LIST.get_index()

        slice_np: np.ndarray = sitk.GetArrayFromImage(slice)
        print(f'np array data type: {slice_np.dtype}')
        # np: int16
        # NOTE: When you print slice_np to a file, it's only 0-255, i.e. uint8, even though the np type is int16.

        print(f'np.min(): {slice_np.min()}')
        print(f'np.max(): {slice_np.max()}')

        with open(str(pathlib.Path('.') / 'src' / 'GUI' / 'np_array_slice.txt'), 'w') as f:
            for i in range(slice_np.shape[0]):
                for j in range(slice_np.shape[1]):
                    f.write(f'{slice_np[i][j]},')
                f.write('\n')

        # No need to add a .copy() to the end of this, but if something breaks, try that
        # This cast causes issues for most files but it makes the NIFTI file at the bottom work fine
        slice_np = slice_np.astype('uint8')

        # sitk.GetArrayFromImage results in the transpose of the original sitk representation, so transpose back
        # .copy() is necessary here
        slice_np = np.ndarray.transpose(slice_np).copy()

        w, h = slice_np.shape

        # Note reversed order of w and h since PyQt treats them differently. But otherwise the image looks the same
        # as the array.
        q_img: QImage = QImage(slice_np.data, h, w, QImage.Format.Format_Grayscale8)

        q_pixmap: QPixmap = QPixmap(q_img)

        self.image.setPixmap(q_pixmap)
        # No zero-indexing when displaying to user
        self.image_num_label.setText(f'Image {index + 1} of {len(globs.IMAGE_LIST)}')
        # TODO: Can probably truncate the path
        self.image.setStatusTip(str(curr_mri_image.get_path()))

    def render_all_sliders(self):
        """Sets all slider values to the values stored in the `MRIImage`.
        
        Also updates rotation and slice num labels."""
        curr_mri_image: MRIImage = globs.IMAGE_LIST.get_curr_mri_image()
        theta_x = curr_mri_image.get_theta_x()
        theta_y = curr_mri_image.get_theta_y()
        theta_z = curr_mri_image.get_theta_z()
        slice_num = curr_mri_image.get_slice_z()
        self.x_slider.setValue(theta_x)
        self.y_slider.setValue(theta_y)
        self.z_slider.setValue(theta_z)
        self.slice_slider.setMaximum(curr_mri_image.get_dimensions()[2] - 1)
        self.slice_slider.setValue(slice_num)
        self.x_rotation_label.setText(f'X rotation: {theta_x}°')
        self.y_rotation_label.setText(f'Y rotation: {theta_y}°')
        self.z_rotation_label.setText(f'Z rotation: {theta_z}°')
        self.slice_num_label.setText(f'Slice: {slice_num}')

    def next_img(self):
        """Advance index and render."""
        globs.IMAGE_LIST.next()
        self.render_curr_slice()
        self.render_all_sliders()

    def previous_img(self):
        """Decrement index and render."""
        globs.IMAGE_LIST.previous()
        self.render_curr_slice()
        self.render_all_sliders()

    def rotate_x(self):
        """Handle x slider movement."""
        curr_mri_image: MRIImage = globs.IMAGE_LIST.get_curr_mri_image()
        x_slider_val: int = self.x_slider.value()
        curr_mri_image.set_theta_x(x_slider_val)
        curr_mri_image.resample()
        self.render_curr_slice()
        self.x_rotation_label.setText(f'X rotation: {x_slider_val}°')

    def rotate_y(self):
        """Handle y slider movement."""
        curr_mri_image: MRIImage = globs.IMAGE_LIST.get_curr_mri_image()
        y_slider_val: int = self.y_slider.value()
        curr_mri_image.set_theta_y(y_slider_val)
        curr_mri_image.resample()
        self.render_curr_slice()
        self.y_rotation_label.setText(f'Y rotation: {y_slider_val}°')

    def rotate_z(self):
        """Handle z slider movement."""
        curr_mri_image: MRIImage = globs.IMAGE_LIST.get_curr_mri_image()
        z_slider_val: int = self.z_slider.value()
        curr_mri_image.set_theta_z(z_slider_val)
        curr_mri_image.resample()
        self.render_curr_slice()
        self.z_rotation_label.setText(f'Z rotation: {z_slider_val}°')

    def slice_update(self):
        """Handle slice slider movement."""
        curr_mri_image: MRIImage = globs.IMAGE_LIST.get_curr_mri_image()
        slice_slider_val: int = self.slice_slider.value()
        curr_mri_image.set_slice_z(slice_slider_val)
        curr_mri_image.resample()
        self.render_curr_slice()
        self.slice_num_label.setText(f'Slice: {slice_slider_val}')

    def reset_settings(self):
        """Reset rotation values and slice num to 0 for the current image."""
        curr_mri_image: MRIImage = globs.IMAGE_LIST.get_curr_mri_image()
        curr_mri_image.set_theta_x(0)
        curr_mri_image.set_theta_y(0)
        curr_mri_image.set_theta_z(0)
        curr_mri_image.set_slice_z(0)
        curr_mri_image.resample()
        self.render_curr_slice()
        self.render_all_sliders()


class CircumferenceWindow(QMainWindow):
    def __init__(self):
        super(CircumferenceWindow, self).__init__()
        loadUi(str(pathlib.Path('.') / 'src' / 'GUI' / 'circumference.ui'), self)
        self.setWindowTitle('Circumference')
        self.action_exit.triggered.connect(exit)
        self.adjust_slice_button.clicked.connect(self.goto_main)
        self.show()

    def goto_main(self):
        """Switch to MainWindow.
        
        Image and sliders aren't modified in `CircumferenceWindow` so no need to re-render anything."""
        widget.setCurrentIndex(MAIN_WINDOW_INDEX)

    def render_curr_slice(self):
        """Same as `MainWindow.render_curr_slice()`.

        Also sets text for `image_num_label` and file path in the status bar tooltip."""
        curr_mri_image: MRIImage = globs.IMAGE_LIST.get_curr_mri_image()
        slice: sitk.Image = curr_mri_image.get_rotated_slice()
        # print(f'sitk: {slice.GetPixelIDTypeAsString()}')
        # sitk: 16-bit signed integer
        index: int = globs.IMAGE_LIST.get_index()

        slice_np: np.ndarray = sitk.GetArrayFromImage(slice)
        # print(f'np: {slice_np.dtype}')
        # np: int16
        # NOTE: When you print slice_np to a file, it's only 0-255, i.e. uint8, even though the np type is int16.

        # No need to add a .copy() to the end of this, but if something breaks, try that
        slice_np = slice_np.astype('uint8')
        # sitk.GetArrayFromImage results in the transpose of the original sitk representation, so transpose back
        # .copy() is necessary here
        slice_np = np.ndarray.transpose(slice_np).copy()

        w, h = slice_np.shape

        # Note reversed order of w and h since PyQt treats them differently. But otherwise the image looks the same
        # as the array.
        q_img: QImage = QImage(slice_np.data, h, w, QImage.Format.Format_Grayscale8)

        q_pixmap: QPixmap = QPixmap(q_img)

        self.image.setPixmap(q_pixmap)
        # No zero-indexing when displaying to user
        self.image_num_label.setText(f'Image {index + 1} of {len(globs.IMAGE_LIST)}')
        # TODO: Can probably truncate the path
        self.image.setStatusTip(str(curr_mri_image.get_path()))


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
    widget.setMinimumWidth(DEFAULT_WIDTH)
    widget.setMinimumHeight(DEFAULT_HEIGHT)
    widget.setCurrentWidget(main_window)
    widget.show()
    try:
        sys.exit(app.exec())
    except:
        print("Exiting")


if __name__ == "__main__":
    main()
