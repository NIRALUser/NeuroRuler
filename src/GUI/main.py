"""Entrypoint of GUI stuff.

Note: This file contains lots of fake syntax errors because PyQt object names don't exist until after `loadUi()`.

Lots of global variables in this file :(, need to find a way to get around this.

A lot of the functions defined here belong in imgproc_helpers. Should refactor later, but need to make sure the global `IMAGE_LIST` is accessible there.

Lastly, there's a lot of methods here that get the current slice (not resample). Isn't too inefficient but could be improved. TODO: Make current slice global?"""

import sys
import pathlib
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.uic.load_ui import loadUi
from PyQt6.QtWidgets import QDialog, QApplication, QMainWindow, QFileDialog
import SimpleITK as sitk
from src.utils.mri_image import MRIImage, MRIImageList
from src.utils.imgproc_helpers import *
import src.utils.globs as globs

DEFAULT_WIDTH: int = 1000
"""Startup width of the GUI"""
DEFAULT_HEIGHT: int = 700
"""Startup height of the GUI"""

# Since QPixmap doesn't support rendering from a sitk.Image or np.ndarray, must save images as jpg/png
# https://doc.qt.io/qtforpython-5/PySide2/QtGui/QPixmap.html
IMG_DIR: pathlib.Path = pathlib.Path('.') / 'img'
"""Directory used to save f'{i}.{IMAGE_EXTENSION}' files corresponding to the currently open images, where `i` is the index (zero-indexed) of the image.

Files will need to be renamed during Add Image or Delete Image operations."""
IMAGE_EXTENSION: str = 'jpg'
"""Extension for images stored in `IMG_DIR`."""

NRRD0_PATH: pathlib.Path = pathlib.Path('ExampleData/BCP_Dataset_2month_T1w.nrrd')
NRRD1_PATH: pathlib.Path = pathlib.Path('ExampleData/IBIS_Dataset_12month_T1w.nrrd')
NRRD2_PATH: pathlib.Path = pathlib.Path('ExampleData/IBIS_Dataset_NotAligned_6month_T1w.nrrd')
NIFTI_PATH: pathlib.Path = pathlib.Path('ExampleData/MicroBiome_1month_T1w.nii.gz')

MAIN_WINDOW_INDEX = 0
CIRCUMFERENCE_WINDOW_INDEX = 1

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi('src/GUI/main.ui', self)
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
        """This needs to be checked for compatibilty on Windows.
        
        The return value of `getOpenFileNames` is a tuple `(list[str], str)`, where the left element is a list of paths.
        
        So `fnames[0][i]` is the i'th path selected."""
        # TODO: Let starting directory be a configurable setting in JSON
        files = QFileDialog.getOpenFileNames(self, 'Open file(s)', str(pathlib.Path.cwd()), 'MRI images (*.nii.gz *.nii *.nrrd)')
        paths = map(pathlib.Path, files[0])
        images = list(map(MRIImage, paths))
        globs.IMAGE_LIST = MRIImageList(images)
        self.enable_elements()
        self.save_all_slices_to_img_dir()
        self.render_curr_image_from_img_dir()
        self.render_all_sliders()

    
    def goto_circumference(self):
        """Switch to CircumferenceWindow.
        
        Compute circumference and update slice settings."""
        widget.setCurrentIndex(CIRCUMFERENCE_WINDOW_INDEX)
        circumference_window.render_curr_image_from_img_dir()
        circumference: float = get_contour_length(process_slice_and_get_contour(globs.CURR_SLICE))
        circumference_window.circumference_label.setText(f'Circumference: {circumference}')
        circumference_window.slice_settings_text.setText(f'X rotation: {globs.CURR_MRI_IMAGE.get_theta_x()}°\nY rotation: {globs.CURR_MRI_IMAGE.get_theta_y()}°\nZ rotation: {globs.CURR_MRI_IMAGE.get_theta_z()}°\nSlice: {globs.CURR_MRI_IMAGE.get_slice_z()}')

    
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

    
    def save_all_slices_to_img_dir(self):
        """Only called after `Open` is pressed. Saves all `rotated_slice`s in `IMAGE_LIST` to `./img/` to ensure that all can be rendered.
        
        Each `MRIImage` gets a `rotated_slice` field during initialization with rotation and slice values all 0, which allows this to work."""
        for (i, mri_image) in enumerate(globs.IMAGE_LIST):
            save_sitk_slice_to_file(mri_image.get_rotated_slice(), IMG_DIR / f'{i}.{IMAGE_EXTENSION}')

    
    def save_curr_slice_to_img_dir(self):
        """Save the current slice to `IMG_DIR`."""
        save_sitk_slice_to_file(globs.CURR_SLICE, IMG_DIR / f'{globs.INDEX}.{IMAGE_EXTENSION}')


    def render_curr_image_from_img_dir(self):
        """Same as `CircumferenceWindow.render_curr_image_from_img_dir`.
        
        Render the current image from stored file (i.e., no resampling).
        
        Call only if `MRIImage.rotated_slice` at `image_list.index` has already been stored to `IMG_DIR`.
        
        Also sets text for `image_num_label` and file path in the status bar tooltip."""
        filepath = IMG_DIR / f'{globs.INDEX}.{IMAGE_EXTENSION}'
        self.image.setPixmap(QtGui.QPixmap(str(filepath)))
        # No zero indexing when displaying to user
        self.image_num_label.setText(f'Image {globs.INDEX + 1} of {len(globs.IMAGE_LIST)}')
        # TODO: Can probably truncate the path
        self.image.setStatusTip(str(globs.CURR_MRI_IMAGE.get_path()))

    
    def render_all_sliders(self):
        """Sets all slider values to the values stored in the `MRIImage`.
        
        Also updates rotation and slice num labels."""
        theta_x = globs.CURR_MRI_IMAGE.get_theta_x()
        theta_y = globs.CURR_MRI_IMAGE.get_theta_y()
        theta_z = globs.CURR_MRI_IMAGE.get_theta_z()
        slice_num = globs.CURR_MRI_IMAGE.get_slice_z()
        self.x_slider.setValue(theta_x)
        self.y_slider.setValue(theta_y)
        self.z_slider.setValue(theta_z)
        self.slice_slider.setMaximum(globs.CURR_MRI_IMAGE.get_dimensions()[2] - 1)
        self.slice_slider.setValue(slice_num)
        self.x_rotation_label.setText(f'X rotation: {theta_x}°')
        self.y_rotation_label.setText(f'Y rotation: {theta_y}°')
        self.z_rotation_label.setText(f'Z rotation: {theta_z}°')
        self.slice_num_label.setText(f'Slice: {slice_num}')


    """
    Careful with setter methods below!
    IMAGE_LIST.next() and .previous() and CURR_MRI_IMAGE.resample() will modify global variables!
    """


    def next_img(self):
        """Advance index and render."""
        globs.IMAGE_LIST.next()
        self.render_curr_image_from_img_dir()
        self.render_all_sliders()


    def previous_img(self):
        """Decrement index and render."""
        globs.IMAGE_LIST.previous()
        self.render_curr_image_from_img_dir()
        self.render_all_sliders()

    
    def rotate_x(self):
        """Handle x slider movement."""
        x_slider_val: int = self.x_slider.value()
        globs.CURR_MRI_IMAGE.set_theta_x(x_slider_val)
        globs.CURR_MRI_IMAGE.resample()
        self.save_curr_slice_to_img_dir()
        self.render_curr_image_from_img_dir()
        self.x_rotation_label.setText(f'X rotation: {x_slider_val}°')


    def rotate_y(self):
        """Handle y slider movement."""
        y_slider_val: int = self.y_slider.value()
        globs.CURR_MRI_IMAGE.set_theta_y(y_slider_val)
        globs.CURR_MRI_IMAGE.resample()
        self.save_curr_slice_to_img_dir()
        self.render_curr_image_from_img_dir()
        self.y_rotation_label.setText(f'Y rotation: {y_slider_val}°')


    def rotate_z(self):
        """Handle z slider movement."""
        z_slider_val: int = self.z_slider.value()
        globs.CURR_MRI_IMAGE.set_theta_z(z_slider_val)
        globs.CURR_MRI_IMAGE.resample()
        self.save_curr_slice_to_img_dir()
        self.render_curr_image_from_img_dir()
        self.z_rotation_label.setText(f'Z rotation: {z_slider_val}°')


    def slice_update(self):
        """Handle slice slider movement."""
        slice_slider_val: int = self.slice_slider.value()
        globs.CURR_MRI_IMAGE.set_slice_z(slice_slider_val)
        globs.CURR_MRI_IMAGE.resample()
        self.save_curr_slice_to_img_dir()
        self.render_curr_image_from_img_dir()
        self.slice_num_label.setText(f'Slice: {slice_slider_val}')


    def reset_settings(self):
        """Reset rotation values and slice num to 0 for the current image."""
        globs.CURR_MRI_IMAGE.set_theta_x(0)
        globs.CURR_MRI_IMAGE.set_theta_y(0)
        globs.CURR_MRI_IMAGE.set_theta_z(0)
        globs.CURR_MRI_IMAGE.set_slice_z(0)
        globs.CURR_MRI_IMAGE.resample()
        self.save_curr_slice_to_img_dir()
        self.render_curr_image_from_img_dir()
        self.render_all_sliders()

    
class CircumferenceWindow(QMainWindow):
    def __init__(self):
        super(CircumferenceWindow, self).__init__()
        loadUi('src/GUI/circumference.ui', self)
        self.action_exit.triggered.connect(exit)
        self.adjust_slice_button.clicked.connect(self.goto_main)
        self.show()

    
    def goto_main(self):
        """Switch to MainWindow.
        
        Image and sliders aren't modified in `CircumferenceWindow` so no need to re-render anything."""
        widget.setCurrentIndex(MAIN_WINDOW_INDEX)


    def render_curr_image_from_img_dir(self):
        """Same as `MainWindow.render_curr_image_from_img_dir`.
        
        Render the current image from stored file (i.e., no resampling).
        
        Call only if `MRIImage.rotated_slice` at `image_list.index` has already been stored to `IMG_DIR`.
        
        Also sets text for `image_num_label` and file path in the status bar tooltip."""
        filepath = IMG_DIR / f'{globs.INDEX}.{IMAGE_EXTENSION}'
        self.image.setPixmap(QtGui.QPixmap(str(filepath)))
        # No zero indexing when displaying to user
        self.image_num_label.setText(f'Image {globs.INDEX + 1} of {len(globs.IMAGE_LIST)}')
        # TODO: Can probably truncate the path
        self.image.setStatusTip(str(globs.CURR_MRI_IMAGE.get_path()))


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
    widget.show()
    try:
        sys.exit(app.exec())
    except:
        print("Exiting")


if __name__ == "__main__":
    main()
