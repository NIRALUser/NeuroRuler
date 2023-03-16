"""Entrypoint of GUI stuff.

Loads `src/GUI/main.ui` and `src/GUI/circumference.ui`, both made in QtDesigner.

Note: This file contains lots of fake syntax errors because PyQt object names don't exist until after `loadUi()`.

Lastly, there's a lot of boilerplate here to get current slice, i.e. `globs.IMAGE_LIST[globs.IMAGE_LIST.index]`

Isn't too inefficient but could be improved. Use global variable?"""

import sys
from pathlib import Path
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
import src.utils.settings as settings
from src.utils.parse_cli import parse_gui_cli

DEFAULT_WIDTH: int = 1000
"""Startup width of the GUI"""
DEFAULT_HEIGHT: int = 700
"""Startup height of the GUI"""


class MainWindow(QMainWindow):
    """Main window of the application.

    Displays image and rotation & slice sliders, along with a reset button.

    Also displays the index of the current image and previous & next buttons."""
    def __init__(self):
        """Load main.ui file from QtDesigner and connect GUI events to methods."""
        super(MainWindow, self).__init__()
        loadUi(str(Path.cwd() / 'src' / 'GUI' / 'main.ui'), self)
        self.setWindowTitle('Head Circumference Tool')
        self.action_open.triggered.connect(self.browse_files)
        self.action_exit.triggered.connect(exit)
        self.action_export_png.triggered.connect(lambda: self.export_slice_as_img('png'))
        self.action_export_jpg.triggered.connect(lambda: self.export_slice_as_img('jpg'))
        self.action_export_bmp.triggered.connect(lambda: self.export_slice_as_img('bmp'))
        self.action_export_ppm.triggered.connect(lambda: self.export_slice_as_img('ppm'))
        self.action_export_xbm.triggered.connect(lambda: self.export_slice_as_img('xbm'))
        self.action_export_xpm.triggered.connect(lambda: self.export_slice_as_img('xpm'))
        self.next_button.clicked.connect(self.next_img)
        self.previous_button.clicked.connect(self.previous_img)
        self.apply_button.clicked.connect(self.goto_circumference)
        self.x_slider.valueChanged.connect(self.rotate_x)
        self.y_slider.valueChanged.connect(self.rotate_y)
        self.z_slider.valueChanged.connect(self.rotate_z)
        self.slice_slider.valueChanged.connect(self.slice_update)
        self.reset_button.clicked.connect(self.reset_settings)
        self.show()

    def goto_circumference(self) -> None:
        """Called when Apply button is clicked.

        From MainWindow, switch to CircumferenceWindow.

        Enable and disable CircumferenceWindow GUI elements.

        Compute circumference and update slice settings. Re-render MRI slice (it won't change, but this is still required)."""
        curr_mri_image: MRIImage = globs.IMAGE_LIST[globs.IMAGE_LIST.index]
        CIRCUMFERENCE_WINDOW.enable_and_disable_elements()
        STACKED_WIDGET.setCurrentWidget(CIRCUMFERENCE_WINDOW)
        CIRCUMFERENCE_WINDOW.render_curr_slice()
        circumference: float = imgproc.length_of_contour(
            imgproc.contour(curr_mri_image.resample()))
        CIRCUMFERENCE_WINDOW.circumference_label.setText(f'Circumference: {circumference}')
        CIRCUMFERENCE_WINDOW.slice_settings_text.setText(
            f'X rotation: {curr_mri_image.theta_x}°\nY rotation: {curr_mri_image.theta_y}°\nZ rotation: {curr_mri_image.theta_z}°\nSlice: {curr_mri_image.slice_z}')

    # TODO: This needs to be checked for compatibility on Windows.
    def browse_files(self) -> None:
        """Called after File > Open.

        Opens file menu and enables GUI elements after user selects files.

        Initializes the global IMAGE_LIST."""
        # str(globs.SUPPORTED_EXTENSIONS) returns "('*.nii.gz', '*.nii', '*.nrrd' ... )"
        # getOpenFileNames expects the form "Name (*.nii.gz *.nii *.nrrd)"
        file_filter: str = 'MRI images ' + str(globs.SUPPORTED_EXTENSIONS).replace("'", "").replace(",", "")
        # TODO: Let starting directory be a configurable setting in JSON
        # The return value of `getOpenFileNames` is a tuple (list[str], str), where the left element is a list of paths.
        # So `fnames[0][i]` is the i'th path selected.
        files = QFileDialog.getOpenFileNames(self, 'Open files', str(Path.cwd()), file_filter)
        self.enable_and_disable_elements()
        paths = map(Path, files[0])
        images = list(map(MRIImage, paths))
        globs.IMAGE_LIST = MRIImageList(images)
        self.render_curr_slice()
        self.render_all_sliders()

    def enable_and_disable_elements(self) -> None:
        """Called when File > Open is clicked and when switching from CircumferenceWindow to MainWindow (i.e., when Adjust button is clicked).

        Enable image, menu items, buttons, and sliders."""
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
        self.action_export_csv.setEnabled(False)
        self.action_export_png.setEnabled(True)
        self.action_export_jpg.setEnabled(True)
        self.action_export_bmp.setEnabled(True)
        self.action_export_ppm.setEnabled(True)
        self.action_export_xbm.setEnabled(True)
        self.action_export_xpm.setEnabled(True)
        self.x_rotation_label.setEnabled(True)
        self.y_rotation_label.setEnabled(True)
        self.z_rotation_label.setEnabled(True)
        self.slice_num_label.setEnabled(True)

    def render_curr_slice(self) -> None:
        """Called after any action that updates the image. Specifically, Previous and Next buttons and any slider.

        Also called after File > Open.

        Same as `CircumferenceWindow.render_curr_slice()`.

        Resamples the currently selected MRIImage using rotation and slice settings, then renders the resulting slice in the GUI.

        Also sets text for `image_num_label` and file path in the status bar tooltip."""
        curr_mri_image: MRIImage = globs.IMAGE_LIST[globs.IMAGE_LIST.index]
        index: int = globs.IMAGE_LIST.index
        # Usually signed int16, sometimes float32/64 data type
        # See https://github.com/COMP523TeamD/HeadCircumferenceTool/issues/4#issuecomment-1468552326
        # But when printed to a file, the actual array has minimum 0. Maximum is usually 500-1000 in a slice.
        rotated_slice: sitk.Image = curr_mri_image.resample()

        # GUI code should not contain anything that has to do with transpose stuff but no way around it
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
        self.image.setStatusTip(str(curr_mri_image.path))

    def render_all_sliders(self) -> None:
        """Sets all slider values to the values stored in the current `MRIImage`.
        
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
        """Called when Next button is clicked.

        Advance index and render image."""
        globs.IMAGE_LIST.next()
        self.render_curr_slice()
        self.render_all_sliders()

    def previous_img(self):
        """Called when Previous button is clicked.

        Decrement index and render image."""
        globs.IMAGE_LIST.previous()
        self.render_curr_slice()
        self.render_all_sliders()

    def rotate_x(self):
        """Called any time the user updates the x slider.

        Handle x slider movement."""
        curr_mri_image: MRIImage = globs.IMAGE_LIST[globs.IMAGE_LIST.index]
        x_slider_val: int = self.x_slider.value()
        curr_mri_image.theta_x = x_slider_val
        self.render_curr_slice()
        self.x_rotation_label.setText(f'X rotation: {x_slider_val}°')

    def rotate_y(self):
        """Called any time the user updates the y slider.

        Handle y slider movement."""
        curr_mri_image: MRIImage = globs.IMAGE_LIST[globs.IMAGE_LIST.index]
        y_slider_val: int = self.y_slider.value()
        curr_mri_image.theta_y = y_slider_val
        self.render_curr_slice()
        self.y_rotation_label.setText(f'Y rotation: {y_slider_val}°')

    def rotate_z(self):
        """Called any time the user updates the z slider.

        Handle z slider movement."""
        curr_mri_image: MRIImage = globs.IMAGE_LIST[globs.IMAGE_LIST.index]
        z_slider_val: int = self.z_slider.value()
        curr_mri_image.theta_z = z_slider_val
        self.render_curr_slice()
        self.z_rotation_label.setText(f'Z rotation: {z_slider_val}°')

    def slice_update(self):
        """Called any time the user updates the slice slider.

        Handle slice slider movement."""
        curr_mri_image: MRIImage = globs.IMAGE_LIST[globs.IMAGE_LIST.index]
        slice_slider_val: int = self.slice_slider.value()
        curr_mri_image.slice_z = slice_slider_val
        self.render_curr_slice()
        self.slice_num_label.setText(f'Slice: {slice_slider_val}')

    def reset_settings(self):
        """Called when Reset is clicked.

        Resets rotation values and slice num to 0 for the current image, then re-renders image and sliders."""
        curr_mri_image: MRIImage = globs.IMAGE_LIST[globs.IMAGE_LIST.index]
        curr_mri_image.theta_x = 0
        curr_mri_image.theta_y = 0
        curr_mri_image.theta_z = 0
        curr_mri_image.slice_z = 0
        self.render_curr_slice()
        self.render_all_sliders()

    def export_slice_as_img(self, extension: str):
        """Called when an Export as image menu item is clicked.

        Exports image currently displayed in GUI to settings.IMG_DIR.

        Filename has format {file_name}_{theta_x}_{theta_y}_{theta_z}_{slice}.{extension}

        Supported formats in this function are the ones supported by QPixmap, namely BMP, JPG, JPEG, PNG, PPM, XBM, XPM."""
        curr_mri_image: MRIImage = globs.IMAGE_LIST[globs.IMAGE_LIST.index]
        # This gets the last part of the file name, i.e. what's after the last slash
        # Also add 1 for 1-indexing
        file_name: str = globs.IMAGE_LIST.index + 1 if settings.EXPORTED_FILE_NAMES_USE_INDEX else curr_mri_image.path.name
        theta_x: int = curr_mri_image.theta_x
        theta_y: int = curr_mri_image.theta_y
        theta_z: int = curr_mri_image.theta_z
        slice_z: int = curr_mri_image.slice_z
        path: str = str(settings.IMG_DIR / f'{file_name}_{theta_x}_{theta_y}_{theta_z}_{slice_z}.{extension}')
        self.image.pixmap().save(path, extension)


class CircumferenceWindow(QMainWindow):
    """Displayed after pressing Apply in MainWindow.

    Displays the same MRI slice as in MainWindow and the computed circumference.

    No sliders but displays rotation & slice values."""
    def __init__(self):
        """Load circumference.ui and connect GUI events to methods."""
        super(CircumferenceWindow, self).__init__()
        loadUi(str(Path.cwd() / 'src' / 'GUI' / 'circumference.ui'), self)
        self.setWindowTitle('Circumference')
        self.enable_and_disable_elements()
        self.action_exit.triggered.connect(exit)
        self.action_export_png.triggered.connect(lambda: self.export_slice_as_img('png'))
        self.action_export_jpg.triggered.connect(lambda: self.export_slice_as_img('jpg'))
        self.action_export_bmp.triggered.connect(lambda: self.export_slice_as_img('bmp'))
        self.action_export_ppm.triggered.connect(lambda: self.export_slice_as_img('ppm'))
        self.action_export_xbm.triggered.connect(lambda: self.export_slice_as_img('xbm'))
        self.action_export_xpm.triggered.connect(lambda: self.export_slice_as_img('xpm'))
        self.adjust_slice_button.clicked.connect(self.goto_main_window)
        self.show()

    def goto_main_window(self):
        """Called when Adjust is clicked.

        From CircumferenceWindow, switch to MainWindow.

        Enables and disables MainWindow GUI elements."""
        MAIN_WINDOW.enable_and_disable_elements()
        STACKED_WIDGET.setCurrentWidget(MAIN_WINDOW)

    def enable_and_disable_elements(self):
        """Called when switching from MainWindow to CircumferenceWindow (i.e., Apply button is clicked).

        Needs only handle the things that are different from MainWindow."""
        print(
            "enabling and disabling circumference window elements, but it's not working. specifically export csv isn't enabled")
        # TODO: Doesn't work
        self.action_export_csv.setEnabled(True)

    def render_curr_slice(self):
        """Called after any action that updates the image. Specifically, Previous and Next buttons and any slider.

        Also called after File > Open.

        Same as `MainWindow.render_curr_slice()`.

        Resamples the currently selected MRIImage using rotation and slice settings, then renders the resulting slice in the GUI.

        Also sets text for `image_num_label` and file path in the status bar tooltip."""
        curr_mri_image: MRIImage = globs.IMAGE_LIST[globs.IMAGE_LIST.index]
        index: int = globs.IMAGE_LIST.index
        # Usually signed int16, sometimes float32/64 data type
        # See https://github.com/COMP523TeamD/HeadCircumferenceTool/issues/4#issuecomment-1468552326
        # But when printed to a file, the actual array has minimum 0. Maximum is usually 500-1000 in a slice.
        rotated_slice: sitk.Image = curr_mri_image.resample()

        # GUI code should not contain anything that has to do with transpose stuff but no way around it
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
        self.image.setStatusTip(str(curr_mri_image.path))

    def export_slice_as_img(self, extension: str):
        """Called when an Export as image menu item is clicked.

        Same as MainWindow.export_slice_as_img.

        Exports image currently displayed in GUI to settings.IMG_DIR.

        Filename has format {file_name}_{theta_x}_{theta_y}_{theta_z}_{slice}.{extension}

        Supported formats in this function are the ones supported by QPixmap, namely BMP, JPG, JPEG, PNG, PPM, XBM, XPM."""
        curr_mri_image: MRIImage = globs.IMAGE_LIST[globs.IMAGE_LIST.index]
        # This gets the last part of the file name, i.e. what's after the last slash
        # Also add 1 for 1-indexing
        file_name: str = globs.IMAGE_LIST.index + 1 if settings.EXPORTED_FILE_NAMES_USE_INDEX else curr_mri_image.path.name
        theta_x: int = curr_mri_image.theta_x
        theta_y: int = curr_mri_image.theta_y
        theta_z: int = curr_mri_image.theta_z
        slice_z: int = curr_mri_image.slice_z
        path: str = str(settings.IMG_DIR / f'{file_name}_{theta_x}_{theta_y}_{theta_z}_{slice_z}.{extension}')
        self.image.pixmap().save(path, extension)


def main() -> None:
    """Main entrypoint of GUI."""
    parse_gui_cli()

    if not (Path.cwd() / settings.IMG_DIR).exists():
        (Path.cwd() / settings.IMG_DIR).mkdir()

    app = QApplication(sys.argv)
    global STACKED_WIDGET
    # This holds MainWindow and CircumferenceWindow.
    # Setting the index allows for switching between windows.
    STACKED_WIDGET = QtWidgets.QStackedWidget()
    global MAIN_WINDOW
    MAIN_WINDOW = MainWindow()
    global CIRCUMFERENCE_WINDOW
    CIRCUMFERENCE_WINDOW = CircumferenceWindow()

    STACKED_WIDGET.addWidget(MAIN_WINDOW)
    STACKED_WIDGET.addWidget(CIRCUMFERENCE_WINDOW)
    STACKED_WIDGET.setMinimumWidth(DEFAULT_WIDTH)
    STACKED_WIDGET.setMinimumHeight(DEFAULT_HEIGHT)
    STACKED_WIDGET.setCurrentWidget(MAIN_WINDOW)
    STACKED_WIDGET.show()
    try:
        sys.exit(app.exec())
    except:
        print("Exiting")


if __name__ == "__main__":
    main()
