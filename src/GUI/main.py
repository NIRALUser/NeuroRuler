"""Entrypoint of GUI stuff.

Note: This file contains lots of fake syntax errors because PyQt object names don't exist until after `loadUi()`.

Lastly, there's a lot of boilerplate here to get current slice. globs.IMAGE_LIST[globs.IMAGE_LIST.index]

Isn't too inefficient but could be improved. Global variable?"""

import sys
import pathlib
import numpy as np
import SimpleITK as sitk
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import QDialog, QApplication, QMainWindow, QFileDialog
from PyQt6.uic.load_ui import loadUi
import qimage2ndarray
from src.utils.mri_image import MRIImage, MRIImageList
import src.utils.imgproc as imgproc
import src.utils.globs as globs

DEFAULT_WIDTH: int = 1000
"""Startup width of the GUI"""
DEFAULT_HEIGHT: int = 700
"""Startup height of the GUI"""

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi(str(pathlib.Path.cwd() / 'src' / 'GUI' / 'main.ui'), self)
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

    def browse_files(self) -> None:
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

    def goto_circumference(self) -> None:
        """Switch to CircumferenceWindow.
        
        Compute circumference and update slice settings."""
        curr_mri_image: MRIImage = globs.IMAGE_LIST[globs.IMAGE_LIST.index]
        stacked_widget.setCurrentWidget(circumference_window)
        circumference_window.render_curr_slice()
        circumference: float = imgproc.length_of_contour(
            imgproc.contour(curr_mri_image.resample()))
        circumference_window.circumference_label.setText(f'Circumference: {circumference}')
        circumference_window.slice_settings_text.setText(
            f'X rotation: {curr_mri_image.theta_x}°\nY rotation: {curr_mri_image.theta_y}°\nZ rotation: {curr_mri_image.theta_z}°\nSlice: {curr_mri_image.slice_z}')

    def enable_elements(self) -> None:
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
        curr_mri_image: MRIImage = globs.IMAGE_LIST[globs.IMAGE_LIST.index]
        index: int = globs.IMAGE_LIST.index
        # Usually signed int16, sometimes float32/64 data type
        # See https://github.com/COMP523TeamD/HeadCircumferenceTool/issues/4#issuecomment-1468552326
        # But when printed to a file, the actual array has minimum 0. Maximum is usually 500-1000 in a slice.
        rotated_slice: sitk.Image = curr_mri_image.resample()

        # Note: sitk.GetArrayFromImage returns a numpy array that is the transpose of the sitk representation.
        slice_np: np.ndarray = sitk.GetArrayFromImage(rotated_slice)

        # Retranspose.
        # TODO: There used to be a .copy() after the transpose because there'd be an error otherwise.
        # After switching to qimage2ndarray.gray2qimage, it seems .copy() is no longer needed, but might need to investigate.
        slice_np = np.ndarray.transpose(slice_np)

        # TODO: Investigate normalization parameters further
        # http://hmeine.github.io/qimage2ndarray/#converting-ndarrays-into-qimages
        q_img = qimage2ndarray.gray2qimage(slice_np, normalize=True)

        q_pixmap: QPixmap = QPixmap(q_img)

        self.image.setPixmap(q_pixmap)
        # No zero-indexing when displaying to user
        self.image_num_label.setText(f'Image {index + 1} of {len(globs.IMAGE_LIST)}')
        # TODO: Can probably truncate the path
        self.image.setStatusTip(str(curr_mri_image.filepath))

    def render_all_sliders(self):
        """Sets all slider values to the values stored in the `MRIImage`.
        
        Also updates rotation and slice num labels."""
        curr_mri_image: MRIImage = globs.IMAGE_LIST[globs.IMAGE_LIST.index]
        theta_x = curr_mri_image.theta_x
        theta_y = curr_mri_image.theta_y
        theta_z = curr_mri_image.theta_z
        slice_num = curr_mri_image.slice_z
        self.x_slider.setValue(theta_x)
        self.y_slider.setValue(theta_y)
        self.z_slider.setValue(theta_z)
        self.slice_slider.setMaximum(curr_mri_image.get_size()[2] - 1)
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
        curr_mri_image: MRIImage = globs.IMAGE_LIST[globs.IMAGE_LIST.index]
        x_slider_val: int = self.x_slider.value()
        curr_mri_image.theta_x = x_slider_val
        self.render_curr_slice()
        self.x_rotation_label.setText(f'X rotation: {x_slider_val}°')

    def rotate_y(self):
        """Handle y slider movement."""
        curr_mri_image: MRIImage = globs.IMAGE_LIST[globs.IMAGE_LIST.index]
        y_slider_val: int = self.y_slider.value()
        curr_mri_image.theta_y = y_slider_val
        self.render_curr_slice()
        self.y_rotation_label.setText(f'Y rotation: {y_slider_val}°')

    def rotate_z(self):
        """Handle z slider movement."""
        curr_mri_image: MRIImage = globs.IMAGE_LIST[globs.IMAGE_LIST.index]
        z_slider_val: int = self.z_slider.value()
        curr_mri_image.theta_z = z_slider_val
        self.render_curr_slice()
        self.z_rotation_label.setText(f'Z rotation: {z_slider_val}°')

    def slice_update(self):
        """Handle slice slider movement."""
        curr_mri_image: MRIImage = globs.IMAGE_LIST[globs.IMAGE_LIST.index]
        slice_slider_val: int = self.slice_slider.value()
        curr_mri_image.slice_z = slice_slider_val
        self.render_curr_slice()
        self.slice_num_label.setText(f'Slice: {slice_slider_val}')

    def reset_settings(self):
        """Reset rotation values and slice num to 0 for the current image."""
        curr_mri_image: MRIImage = globs.IMAGE_LIST[globs.IMAGE_LIST.index]
        curr_mri_image.theta_x = 0
        curr_mri_image.theta_y = 0
        curr_mri_image.theta_z = 0
        curr_mri_image.slice_z = 0
        self.render_curr_slice()
        self.render_all_sliders()


class CircumferenceWindow(QMainWindow):
    def __init__(self):
        super(CircumferenceWindow, self).__init__()
        loadUi(str(pathlib.Path.cwd() / 'src' / 'GUI' / 'circumference.ui'), self)
        self.setWindowTitle('Circumference')
        self.action_exit.triggered.connect(exit)
        self.adjust_slice_button.clicked.connect(self.goto_main)
        self.show()

    def goto_main(self):
        """Switch to MainWindow.
        
        Image and sliders can't be modified in `CircumferenceWindow`, so no need to re-render anything."""
        stacked_widget.setCurrentWidget(main_window)

    def render_curr_slice(self):
        """Same as `MainWindow.render_curr_slice()`.
        
        Also sets text for `image_num_label` and file path in the status bar tooltip."""
        curr_mri_image: MRIImage = globs.IMAGE_LIST[globs.IMAGE_LIST.index]
        index: int = globs.IMAGE_LIST.index
        # Usually signed int16, sometimes float32/64 data type
        # See https://github.com/COMP523TeamD/HeadCircumferenceTool/issues/4#issuecomment-1468552326
        # But when printed to a file, the actual array has minimum 0. Maximum is usually 500-1000 in a slice.
        rotated_slice: sitk.Image = curr_mri_image.resample()

        # Note: sitk.GetArrayFromImage returns a numpy array that is the transpose of the sitk representation.
        slice_np: np.ndarray = sitk.GetArrayFromImage(rotated_slice)

        # Retranspose.
        # TODO: There used to be a .copy() after the transpose because there'd be an error otherwise.
        # After switching to qimage2ndarray.gray2qimage, it seems .copy() is no longer needed, but might need to investigate.
        slice_np = np.ndarray.transpose(slice_np)

        # TODO: Investigate normalization parameters further
        # http://hmeine.github.io/qimage2ndarray/#converting-ndarrays-into-qimages
        q_img = qimage2ndarray.gray2qimage(slice_np, normalize=True)

        q_pixmap: QPixmap = QPixmap(q_img)

        self.image.setPixmap(q_pixmap)
        # No zero-indexing when displaying to user
        self.image_num_label.setText(f'Image {index + 1} of {len(globs.IMAGE_LIST)}')
        # TODO: Can probably truncate the path
        self.image.setStatusTip(str(curr_mri_image.filepath))


def main() -> None:
    app = QApplication(sys.argv)
    global stacked_widget
    # This holds MainWindow and CircumferenceWindow.
    # Setting the index allows for switching between windows.
    stacked_widget = QtWidgets.QStackedWidget()
    global main_window
    main_window = MainWindow()
    global circumference_window
    circumference_window = CircumferenceWindow()

    stacked_widget.addWidget(main_window)
    stacked_widget.addWidget(circumference_window)
    stacked_widget.setMinimumWidth(DEFAULT_WIDTH)
    stacked_widget.setMinimumHeight(DEFAULT_HEIGHT)
    stacked_widget.setCurrentWidget(main_window)
    stacked_widget.show()
    try:
        sys.exit(app.exec())
    except:
        print("Exiting")


if __name__ == "__main__":
    main()
