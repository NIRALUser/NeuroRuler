# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.4.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QLineEdit, QMainWindow, QMenu, QMenuBar,
    QPushButton, QRadioButton, QScrollBar, QSizePolicy,
    QSpacerItem, QStatusBar, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(858, 864)
        self.action_documentation = QAction(MainWindow)
        self.action_documentation.setObjectName(u"action_documentation")
        self.action_exit = QAction(MainWindow)
        self.action_exit.setObjectName(u"action_exit")
        self.action_open = QAction(MainWindow)
        self.action_open.setObjectName(u"action_open")
        self.action_add_images = QAction(MainWindow)
        self.action_add_images.setObjectName(u"action_add_images")
        self.action_add_images.setEnabled(False)
        self.action_remove_image = QAction(MainWindow)
        self.action_remove_image.setObjectName(u"action_remove_image")
        self.action_remove_image.setEnabled(False)
        self.action_export_png = QAction(MainWindow)
        self.action_export_png.setObjectName(u"action_export_png")
        self.action_export_png.setEnabled(False)
        self.action_export_jpg = QAction(MainWindow)
        self.action_export_jpg.setObjectName(u"action_export_jpg")
        self.action_export_jpg.setEnabled(False)
        self.action_export_csv = QAction(MainWindow)
        self.action_export_csv.setObjectName(u"action_export_csv")
        self.action_export_csv.setEnabled(False)
        self.action_export_bmp = QAction(MainWindow)
        self.action_export_bmp.setObjectName(u"action_export_bmp")
        self.action_export_bmp.setEnabled(False)
        self.action_export_ppm = QAction(MainWindow)
        self.action_export_ppm.setObjectName(u"action_export_ppm")
        self.action_export_ppm.setEnabled(False)
        self.action_export_xbm = QAction(MainWindow)
        self.action_export_xbm.setObjectName(u"action_export_xbm")
        self.action_export_xbm.setEnabled(False)
        self.action_export_xpm = QAction(MainWindow)
        self.action_export_xpm.setObjectName(u"action_export_xpm")
        self.action_export_xpm.setEnabled(False)
        self.action_github = QAction(MainWindow)
        self.action_github.setObjectName(u"action_github")
        self.action_test_stuff = QAction(MainWindow)
        self.action_test_stuff.setObjectName(u"action_test_stuff")
        self.action_print_metadata = QAction(MainWindow)
        self.action_print_metadata.setObjectName(u"action_print_metadata")
        self.action_print_dimensions = QAction(MainWindow)
        self.action_print_dimensions.setObjectName(u"action_print_dimensions")
        self.action_print_properties = QAction(MainWindow)
        self.action_print_properties.setObjectName(u"action_print_properties")
        self.action_print_direction = QAction(MainWindow)
        self.action_print_direction.setObjectName(u"action_print_direction")
        self.action_orient_for_x_view = QAction(MainWindow)
        self.action_orient_for_x_view.setObjectName(u"action_orient_for_x_view")
        self.action_orient_for_y_view = QAction(MainWindow)
        self.action_orient_for_y_view.setObjectName(u"action_orient_for_y_view")
        self.action_orient_for_z_view = QAction(MainWindow)
        self.action_orient_for_z_view.setObjectName(u"action_orient_for_z_view")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout_8 = QVBoxLayout()
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(10, 20, 20, 20)
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setPointSize(24)
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignCenter)

        self.verticalLayout_8.addWidget(self.label)

        self.verticalSpacer_10 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)

        self.verticalLayout_8.addItem(self.verticalSpacer_10)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 10, 10)
        self.label_10 = QLabel(self.centralwidget)
        self.label_10.setObjectName(u"label_10")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_10.sizePolicy().hasHeightForWidth())
        self.label_10.setSizePolicy(sizePolicy)
        font1 = QFont()
        font1.setPointSize(16)
        self.label_10.setFont(font1)
        self.label_10.setAlignment(Qt.AlignHCenter|Qt.AlignTop)

        self.verticalLayout_2.addWidget(self.label_10)

        self.verticalSpacer_5 = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.verticalLayout_2.addItem(self.verticalSpacer_5)

        self.x_rotation_label = QLabel(self.centralwidget)
        self.x_rotation_label.setObjectName(u"x_rotation_label")
        self.x_rotation_label.setEnabled(False)
        self.x_rotation_label.setAlignment(Qt.AlignCenter)

        self.verticalLayout_2.addWidget(self.x_rotation_label)

        self.x_slider = QScrollBar(self.centralwidget)
        self.x_slider.setObjectName(u"x_slider")
        self.x_slider.setEnabled(False)
        self.x_slider.setCursor(QCursor(Qt.ClosedHandCursor))
        self.x_slider.setMinimum(-90)
        self.x_slider.setMaximum(90)
        self.x_slider.setOrientation(Qt.Horizontal)

        self.verticalLayout_2.addWidget(self.x_slider)

        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_4)

        self.y_rotation_label = QLabel(self.centralwidget)
        self.y_rotation_label.setObjectName(u"y_rotation_label")
        self.y_rotation_label.setEnabled(False)
        self.y_rotation_label.setAlignment(Qt.AlignCenter)

        self.verticalLayout_2.addWidget(self.y_rotation_label)

        self.y_slider = QScrollBar(self.centralwidget)
        self.y_slider.setObjectName(u"y_slider")
        self.y_slider.setEnabled(False)
        self.y_slider.setCursor(QCursor(Qt.ClosedHandCursor))
        self.y_slider.setMinimum(-90)
        self.y_slider.setMaximum(90)
        self.y_slider.setOrientation(Qt.Horizontal)

        self.verticalLayout_2.addWidget(self.y_slider)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_3)

        self.z_rotation_label = QLabel(self.centralwidget)
        self.z_rotation_label.setObjectName(u"z_rotation_label")
        self.z_rotation_label.setEnabled(False)
        self.z_rotation_label.setAlignment(Qt.AlignCenter)

        self.verticalLayout_2.addWidget(self.z_rotation_label)

        self.z_slider = QScrollBar(self.centralwidget)
        self.z_slider.setObjectName(u"z_slider")
        self.z_slider.setEnabled(False)
        self.z_slider.setCursor(QCursor(Qt.ClosedHandCursor))
        self.z_slider.setMinimum(-90)
        self.z_slider.setMaximum(90)
        self.z_slider.setOrientation(Qt.Horizontal)

        self.verticalLayout_2.addWidget(self.z_slider)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_2)

        self.slice_num_label = QLabel(self.centralwidget)
        self.slice_num_label.setObjectName(u"slice_num_label")
        self.slice_num_label.setEnabled(False)
        self.slice_num_label.setAlignment(Qt.AlignCenter)

        self.verticalLayout_2.addWidget(self.slice_num_label)

        self.slice_slider = QScrollBar(self.centralwidget)
        self.slice_slider.setObjectName(u"slice_slider")
        self.slice_slider.setEnabled(False)
        self.slice_slider.setCursor(QCursor(Qt.ClosedHandCursor))
        self.slice_slider.setMaximum(180)
        self.slice_slider.setValue(90)
        self.slice_slider.setOrientation(Qt.Horizontal)

        self.verticalLayout_2.addWidget(self.slice_slider)

        self.verticalSpacer_18 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_18)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.x_view_radio_button = QRadioButton(self.centralwidget)
        self.x_view_radio_button.setObjectName(u"x_view_radio_button")
        self.x_view_radio_button.setEnabled(False)
        self.x_view_radio_button.setAutoExclusive(False)

        self.horizontalLayout_9.addWidget(self.x_view_radio_button)

        self.y_view_radio_button = QRadioButton(self.centralwidget)
        self.y_view_radio_button.setObjectName(u"y_view_radio_button")
        self.y_view_radio_button.setEnabled(False)
        self.y_view_radio_button.setAutoExclusive(False)

        self.horizontalLayout_9.addWidget(self.y_view_radio_button)

        self.z_view_radio_button = QRadioButton(self.centralwidget)
        self.z_view_radio_button.setObjectName(u"z_view_radio_button")
        self.z_view_radio_button.setEnabled(False)
        self.z_view_radio_button.setChecked(True)
        self.z_view_radio_button.setAutoExclusive(False)

        self.horizontalLayout_9.addWidget(self.z_view_radio_button)


        self.verticalLayout_2.addLayout(self.horizontalLayout_9)

        self.verticalSpacer = QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.reset_button = QPushButton(self.centralwidget)
        self.reset_button.setObjectName(u"reset_button")
        self.reset_button.setEnabled(False)
        self.reset_button.setCursor(QCursor(Qt.ArrowCursor))

        self.verticalLayout_2.addWidget(self.reset_button)


        self.horizontalLayout_6.addLayout(self.verticalLayout_2)

        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(10, -1, -1, 10)
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setFont(font1)
        self.label_2.setAlignment(Qt.AlignCenter)

        self.verticalLayout_3.addWidget(self.label_2)

        self.verticalSpacer_6 = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)

        self.verticalLayout_3.addItem(self.verticalSpacer_6)

        self.verticalLayout_7 = QVBoxLayout()
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(40, -1, 40, -1)
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.conductance_parameter_label = QLabel(self.centralwidget)
        self.conductance_parameter_label.setObjectName(u"conductance_parameter_label")
        self.conductance_parameter_label.setEnabled(False)

        self.horizontalLayout_3.addWidget(self.conductance_parameter_label)

        self.conductance_parameter_input = QLineEdit(self.centralwidget)
        self.conductance_parameter_input.setObjectName(u"conductance_parameter_input")
        self.conductance_parameter_input.setEnabled(False)
        sizePolicy1 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.conductance_parameter_input.sizePolicy().hasHeightForWidth())
        self.conductance_parameter_input.setSizePolicy(sizePolicy1)
        self.conductance_parameter_input.setMinimumSize(QSize(15, 0))
        self.conductance_parameter_input.setMaxLength(10)

        self.horizontalLayout_3.addWidget(self.conductance_parameter_input)


        self.verticalLayout_7.addLayout(self.horizontalLayout_3)

        self.verticalSpacer_8 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_7.addItem(self.verticalSpacer_8)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.smoothing_iterations_label = QLabel(self.centralwidget)
        self.smoothing_iterations_label.setObjectName(u"smoothing_iterations_label")
        self.smoothing_iterations_label.setEnabled(False)

        self.horizontalLayout_4.addWidget(self.smoothing_iterations_label)

        self.smoothing_iterations_input = QLineEdit(self.centralwidget)
        self.smoothing_iterations_input.setObjectName(u"smoothing_iterations_input")
        self.smoothing_iterations_input.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.smoothing_iterations_input.sizePolicy().hasHeightForWidth())
        self.smoothing_iterations_input.setSizePolicy(sizePolicy1)
        self.smoothing_iterations_input.setMinimumSize(QSize(15, 0))
        self.smoothing_iterations_input.setMaxLength(10)

        self.horizontalLayout_4.addWidget(self.smoothing_iterations_input)


        self.verticalLayout_7.addLayout(self.horizontalLayout_4)

        self.verticalSpacer_7 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_7.addItem(self.verticalSpacer_7)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.time_step_label = QLabel(self.centralwidget)
        self.time_step_label.setObjectName(u"time_step_label")
        self.time_step_label.setEnabled(False)

        self.horizontalLayout_5.addWidget(self.time_step_label)

        self.time_step_input = QLineEdit(self.centralwidget)
        self.time_step_input.setObjectName(u"time_step_input")
        self.time_step_input.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.time_step_input.sizePolicy().hasHeightForWidth())
        self.time_step_input.setSizePolicy(sizePolicy1)
        self.time_step_input.setMinimumSize(QSize(15, 0))
        self.time_step_input.setMaxLength(10)

        self.horizontalLayout_5.addWidget(self.time_step_input)


        self.verticalLayout_7.addLayout(self.horizontalLayout_5)


        self.verticalLayout_3.addLayout(self.verticalLayout_7)

        self.verticalSpacer_9 = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)

        self.verticalLayout_3.addItem(self.verticalSpacer_9)

        self.smoothing_preview_button = QPushButton(self.centralwidget)
        self.smoothing_preview_button.setObjectName(u"smoothing_preview_button")
        self.smoothing_preview_button.setEnabled(False)

        self.verticalLayout_3.addWidget(self.smoothing_preview_button)


        self.verticalLayout_6.addLayout(self.verticalLayout_3)

        self.verticalSpacer_19 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)

        self.verticalLayout_6.addItem(self.verticalSpacer_19)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.label_7 = QLabel(self.centralwidget)
        self.label_7.setObjectName(u"label_7")
        sizePolicy.setHeightForWidth(self.label_7.sizePolicy().hasHeightForWidth())
        self.label_7.setSizePolicy(sizePolicy)
        self.label_7.setFont(font1)
        self.label_7.setAlignment(Qt.AlignHCenter|Qt.AlignTop)

        self.verticalLayout_4.addWidget(self.label_7)

        self.verticalSpacer_11 = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)

        self.verticalLayout_4.addItem(self.verticalSpacer_11)

        self.verticalLayout_9 = QVBoxLayout()
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalLayout_9.setContentsMargins(40, -1, 40, -1)
        self.verticalSpacer_12 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_9.addItem(self.verticalSpacer_12)

        self.otsu_radio_button = QRadioButton(self.centralwidget)
        self.otsu_radio_button.setObjectName(u"otsu_radio_button")
        self.otsu_radio_button.setEnabled(False)
        self.otsu_radio_button.setChecked(True)
        self.otsu_radio_button.setAutoExclusive(False)

        self.verticalLayout_9.addWidget(self.otsu_radio_button)

        self.verticalSpacer_13 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_9.addItem(self.verticalSpacer_13)

        self.binary_radio_button = QRadioButton(self.centralwidget)
        self.binary_radio_button.setObjectName(u"binary_radio_button")
        self.binary_radio_button.setEnabled(False)
        self.binary_radio_button.setAutoExclusive(False)

        self.verticalLayout_9.addWidget(self.binary_radio_button)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.label_9 = QLabel(self.centralwidget)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setEnabled(False)

        self.horizontalLayout_8.addWidget(self.label_9)

        self.lineEdit_5 = QLineEdit(self.centralwidget)
        self.lineEdit_5.setObjectName(u"lineEdit_5")
        self.lineEdit_5.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.lineEdit_5.sizePolicy().hasHeightForWidth())
        self.lineEdit_5.setSizePolicy(sizePolicy1)
        self.lineEdit_5.setMinimumSize(QSize(15, 0))

        self.horizontalLayout_8.addWidget(self.lineEdit_5)


        self.verticalLayout_5.addLayout(self.horizontalLayout_8)

        self.verticalSpacer_15 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_5.addItem(self.verticalSpacer_15)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.label_8 = QLabel(self.centralwidget)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setEnabled(False)

        self.horizontalLayout_7.addWidget(self.label_8)

        self.lineEdit_4 = QLineEdit(self.centralwidget)
        self.lineEdit_4.setObjectName(u"lineEdit_4")
        self.lineEdit_4.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.lineEdit_4.sizePolicy().hasHeightForWidth())
        self.lineEdit_4.setSizePolicy(sizePolicy1)
        self.lineEdit_4.setMinimumSize(QSize(15, 0))

        self.horizontalLayout_7.addWidget(self.lineEdit_4)


        self.verticalLayout_5.addLayout(self.horizontalLayout_7)


        self.verticalLayout_9.addLayout(self.verticalLayout_5)


        self.verticalLayout_4.addLayout(self.verticalLayout_9)

        self.verticalSpacer_14 = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)

        self.verticalLayout_4.addItem(self.verticalSpacer_14)

        self.threshold_preview_button = QPushButton(self.centralwidget)
        self.threshold_preview_button.setObjectName(u"threshold_preview_button")
        self.threshold_preview_button.setEnabled(False)

        self.verticalLayout_4.addWidget(self.threshold_preview_button)


        self.verticalLayout_6.addLayout(self.verticalLayout_4)


        self.horizontalLayout_6.addLayout(self.verticalLayout_6)


        self.verticalLayout_8.addLayout(self.horizontalLayout_6)

        self.verticalSpacer_20 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)

        self.verticalLayout_8.addItem(self.verticalSpacer_20)

        self.apply_button = QPushButton(self.centralwidget)
        self.apply_button.setObjectName(u"apply_button")
        self.apply_button.setEnabled(False)
        self.apply_button.setCursor(QCursor(Qt.ArrowCursor))
        self.apply_button.setCheckable(False)

        self.verticalLayout_8.addWidget(self.apply_button)


        self.horizontalLayout.addLayout(self.verticalLayout_8)

        self.line = QFrame(self.centralwidget)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.VLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.horizontalLayout.addWidget(self.line)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(20, 20, 20, 20)
        self.circumference_label = QLabel(self.centralwidget)
        self.circumference_label.setObjectName(u"circumference_label")
        self.circumference_label.setEnabled(False)
        self.circumference_label.setFont(font1)
        self.circumference_label.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.circumference_label)

        self.verticalSpacer_17 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_17)

        self.image = QLabel(self.centralwidget)
        self.image.setObjectName(u"image")
        self.image.setEnabled(True)
        self.image.setMinimumSize(QSize(0, 500))
        self.image.setSizeIncrement(QSize(0, 0))
        self.image.setScaledContents(True)
        self.image.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.image)

        self.image_path_label = QLabel(self.centralwidget)
        self.image_path_label.setObjectName(u"image_path_label")
        self.image_path_label.setEnabled(False)
        self.image_path_label.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.image_path_label)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.previous_button = QPushButton(self.centralwidget)
        self.previous_button.setObjectName(u"previous_button")
        self.previous_button.setEnabled(False)
        self.previous_button.setCursor(QCursor(Qt.ArrowCursor))

        self.horizontalLayout_2.addWidget(self.previous_button)

        self.image_num_label = QLabel(self.centralwidget)
        self.image_num_label.setObjectName(u"image_num_label")
        self.image_num_label.setEnabled(False)
        self.image_num_label.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_2.addWidget(self.image_num_label)

        self.next_button = QPushButton(self.centralwidget)
        self.next_button.setObjectName(u"next_button")
        self.next_button.setEnabled(False)
        self.next_button.setCursor(QCursor(Qt.ArrowCursor))

        self.horizontalLayout_2.addWidget(self.next_button)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.verticalSpacer_16 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_16)

        self.export_button = QPushButton(self.centralwidget)
        self.export_button.setObjectName(u"export_button")
        self.export_button.setEnabled(False)

        self.verticalLayout.addWidget(self.export_button)


        self.horizontalLayout.addLayout(self.verticalLayout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 858, 24))
        self.menubar.setNativeMenuBar(True)
        self.menu_file = QMenu(self.menubar)
        self.menu_file.setObjectName(u"menu_file")
        self.action_export = QMenu(self.menu_file)
        self.action_export.setObjectName(u"action_export")
        self.menu_help = QMenu(self.menubar)
        self.menu_help.setObjectName(u"menu_help")
        self.menu_debug = QMenu(self.menubar)
        self.menu_debug.setObjectName(u"menu_debug")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menu_file.menuAction())
        self.menubar.addAction(self.menu_help.menuAction())
        self.menubar.addAction(self.menu_debug.menuAction())
        self.menu_file.addAction(self.action_open)
        self.menu_file.addAction(self.action_add_images)
        self.menu_file.addAction(self.action_remove_image)
        self.menu_file.addAction(self.action_export.menuAction())
        self.menu_file.addAction(self.action_exit)
        self.action_export.addAction(self.action_export_csv)
        self.action_export.addSeparator()
        self.action_export.addAction(self.action_export_png)
        self.action_export.addAction(self.action_export_jpg)
        self.action_export.addAction(self.action_export_bmp)
        self.action_export.addAction(self.action_export_ppm)
        self.action_export.addAction(self.action_export_xbm)
        self.action_export.addAction(self.action_export_xpm)
        self.menu_help.addAction(self.action_github)
        self.menu_help.addAction(self.action_documentation)
        self.menu_debug.addAction(self.action_test_stuff)
        self.menu_debug.addAction(self.action_print_metadata)
        self.menu_debug.addAction(self.action_print_dimensions)
        self.menu_debug.addAction(self.action_print_properties)
        self.menu_debug.addAction(self.action_print_direction)
        self.menu_debug.addAction(self.action_orient_for_x_view)
        self.menu_debug.addAction(self.action_orient_for_y_view)
        self.menu_debug.addAction(self.action_orient_for_z_view)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.action_documentation.setText(QCoreApplication.translate("MainWindow", u"Documentation", None))
#if QT_CONFIG(tooltip)
        self.action_documentation.setToolTip(QCoreApplication.translate("MainWindow", u"Open documentation website in web browser.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.action_documentation.setStatusTip(QCoreApplication.translate("MainWindow", u"Open documentation website in web browser.", None))
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(shortcut)
        self.action_documentation.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+D", None))
#endif // QT_CONFIG(shortcut)
        self.action_exit.setText(QCoreApplication.translate("MainWindow", u"Exit", None))
#if QT_CONFIG(tooltip)
        self.action_exit.setToolTip(QCoreApplication.translate("MainWindow", u"Exit.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.action_exit.setStatusTip(QCoreApplication.translate("MainWindow", u"Exit.", None))
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(shortcut)
        self.action_exit.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+W", None))
#endif // QT_CONFIG(shortcut)
        self.action_open.setText(QCoreApplication.translate("MainWindow", u"Open", None))
#if QT_CONFIG(tooltip)
        self.action_open.setToolTip(QCoreApplication.translate("MainWindow", u"Select image(s) to be opened.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.action_open.setStatusTip(QCoreApplication.translate("MainWindow", u"Select image(s) to be opened.", None))
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(shortcut)
        self.action_open.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+O", None))
#endif // QT_CONFIG(shortcut)
        self.action_add_images.setText(QCoreApplication.translate("MainWindow", u"Add Images", None))
#if QT_CONFIG(tooltip)
        self.action_add_images.setToolTip(QCoreApplication.translate("MainWindow", u"Add image(s) to the end of the list. No duplicates.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.action_add_images.setStatusTip(QCoreApplication.translate("MainWindow", u"Add image(s) to the end of the list. No duplicates.", None))
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(shortcut)
        self.action_add_images.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+A", None))
#endif // QT_CONFIG(shortcut)
        self.action_remove_image.setText(QCoreApplication.translate("MainWindow", u"Remove Image", None))
#if QT_CONFIG(tooltip)
        self.action_remove_image.setToolTip(QCoreApplication.translate("MainWindow", u"Remove currently displayed image from the list. Does not delete the file from disk.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.action_remove_image.setStatusTip(QCoreApplication.translate("MainWindow", u"Remove currently displayed image from the list. Does not delete the file from disk.", None))
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(shortcut)
        self.action_remove_image.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+R", None))
#endif // QT_CONFIG(shortcut)
        self.action_export_png.setText(QCoreApplication.translate("MainWindow", u"PNG", None))
#if QT_CONFIG(tooltip)
        self.action_export_png.setToolTip(QCoreApplication.translate("MainWindow", u"Export slice as PNG.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.action_export_png.setStatusTip(QCoreApplication.translate("MainWindow", u"Export slice as PNG.", None))
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(shortcut)
        self.action_export_png.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+E, Ctrl+P", None))
#endif // QT_CONFIG(shortcut)
        self.action_export_jpg.setText(QCoreApplication.translate("MainWindow", u"JPG", None))
#if QT_CONFIG(tooltip)
        self.action_export_jpg.setToolTip(QCoreApplication.translate("MainWindow", u"Export slice as JPG.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.action_export_jpg.setStatusTip(QCoreApplication.translate("MainWindow", u"Export slice as JPG.", None))
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(shortcut)
        self.action_export_jpg.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+E, Ctrl+J", None))
#endif // QT_CONFIG(shortcut)
        self.action_export_csv.setText(QCoreApplication.translate("MainWindow", u"CSV", None))
#if QT_CONFIG(tooltip)
        self.action_export_csv.setToolTip(QCoreApplication.translate("MainWindow", u"Export image data as CSV.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.action_export_csv.setStatusTip(QCoreApplication.translate("MainWindow", u"Export image data as CSV.", None))
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(shortcut)
        self.action_export_csv.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+E, Ctrl+C", None))
#endif // QT_CONFIG(shortcut)
        self.action_export_bmp.setText(QCoreApplication.translate("MainWindow", u"BMP", None))
#if QT_CONFIG(tooltip)
        self.action_export_bmp.setToolTip(QCoreApplication.translate("MainWindow", u"Export slice as BMP.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.action_export_bmp.setStatusTip(QCoreApplication.translate("MainWindow", u"Export slice as BMP.", None))
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(shortcut)
        self.action_export_bmp.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+E, Ctrl+B", None))
#endif // QT_CONFIG(shortcut)
        self.action_export_ppm.setText(QCoreApplication.translate("MainWindow", u"PPM", None))
#if QT_CONFIG(tooltip)
        self.action_export_ppm.setToolTip(QCoreApplication.translate("MainWindow", u"Export slice as PPM.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.action_export_ppm.setStatusTip(QCoreApplication.translate("MainWindow", u"Export slice as PPM.", None))
#endif // QT_CONFIG(statustip)
        self.action_export_xbm.setText(QCoreApplication.translate("MainWindow", u"XBM", None))
#if QT_CONFIG(tooltip)
        self.action_export_xbm.setToolTip(QCoreApplication.translate("MainWindow", u"Export slice as XBM.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.action_export_xbm.setStatusTip(QCoreApplication.translate("MainWindow", u"Export slice as XBM.", None))
#endif // QT_CONFIG(statustip)
        self.action_export_xpm.setText(QCoreApplication.translate("MainWindow", u"XPM", None))
#if QT_CONFIG(tooltip)
        self.action_export_xpm.setToolTip(QCoreApplication.translate("MainWindow", u"Export slice as XPM.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.action_export_xpm.setStatusTip(QCoreApplication.translate("MainWindow", u"Export slice as XPM.", None))
#endif // QT_CONFIG(statustip)
        self.action_github.setText(QCoreApplication.translate("MainWindow", u"GitHub", None))
#if QT_CONFIG(tooltip)
        self.action_github.setToolTip(QCoreApplication.translate("MainWindow", u"Open GitHub website in web browser.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.action_github.setStatusTip(QCoreApplication.translate("MainWindow", u"Open GitHub website in web browser.", None))
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(shortcut)
        self.action_github.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+G", None))
#endif // QT_CONFIG(shortcut)
        self.action_test_stuff.setText(QCoreApplication.translate("MainWindow", u"Test stuff", None))
#if QT_CONFIG(tooltip)
        self.action_test_stuff.setToolTip(QCoreApplication.translate("MainWindow", u"Connected to test_stuff method. Modify to test stuff.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.action_test_stuff.setStatusTip(QCoreApplication.translate("MainWindow", u"Connected to test_stuff method. Modify to test stuff.", None))
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(shortcut)
        self.action_test_stuff.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+T", None))
#endif // QT_CONFIG(shortcut)
        self.action_print_metadata.setText(QCoreApplication.translate("MainWindow", u"Print metadata", None))
#if QT_CONFIG(tooltip)
        self.action_print_metadata.setToolTip(QCoreApplication.translate("MainWindow", u"Print metadata to terminal.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.action_print_metadata.setStatusTip(QCoreApplication.translate("MainWindow", u"Print metadata to terminal.", None))
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(shortcut)
        self.action_print_metadata.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+P, Ctrl+M", None))
#endif // QT_CONFIG(shortcut)
        self.action_print_dimensions.setText(QCoreApplication.translate("MainWindow", u"Print dimensions", None))
#if QT_CONFIG(tooltip)
        self.action_print_dimensions.setToolTip(QCoreApplication.translate("MainWindow", u"Print dimensions to terminal.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.action_print_dimensions.setStatusTip(QCoreApplication.translate("MainWindow", u"Print dimensions to terminal.", None))
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(shortcut)
        self.action_print_dimensions.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+P, Ctrl+S", None))
#endif // QT_CONFIG(shortcut)
        self.action_print_properties.setText(QCoreApplication.translate("MainWindow", u"Print properties", None))
#if QT_CONFIG(tooltip)
        self.action_print_properties.setToolTip(QCoreApplication.translate("MainWindow", u"Print properties of the loaded batch.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.action_print_properties.setStatusTip(QCoreApplication.translate("MainWindow", u"Print properties of the loaded batch.", None))
#endif // QT_CONFIG(statustip)
        self.action_print_direction.setText(QCoreApplication.translate("MainWindow", u"Print direction", None))
#if QT_CONFIG(statustip)
        self.action_print_direction.setStatusTip(QCoreApplication.translate("MainWindow", u"Print direction", None))
#endif // QT_CONFIG(statustip)
        self.action_orient_for_x_view.setText(QCoreApplication.translate("MainWindow", u"Orient for X view", None))
        self.action_orient_for_y_view.setText(QCoreApplication.translate("MainWindow", u"Orient for Y view", None))
        self.action_orient_for_z_view.setText(QCoreApplication.translate("MainWindow", u"Orient for Z view", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Settings", None))
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"Slice Options", None))
        self.x_rotation_label.setText(QCoreApplication.translate("MainWindow", u"X rotation", None))
#if QT_CONFIG(tooltip)
        self.x_slider.setToolTip(QCoreApplication.translate("MainWindow", u"Control X rotation value. Left click on the left end or right end to decrease or increase angle by 1 degree.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.x_slider.setStatusTip(QCoreApplication.translate("MainWindow", u"Control X rotation value. Left click on the left end or right end to decrease or increase angle by 1 degree.", None))
#endif // QT_CONFIG(statustip)
        self.y_rotation_label.setText(QCoreApplication.translate("MainWindow", u"Y rotation", None))
#if QT_CONFIG(tooltip)
        self.y_slider.setToolTip(QCoreApplication.translate("MainWindow", u"Control Y rotation value. Left click on the left end or right end to decrease or increase angle by 1 degree.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.y_slider.setStatusTip(QCoreApplication.translate("MainWindow", u"Control Y rotation value. Left click on the left end or right end to decrease or increase angle by 1 degree.", None))
#endif // QT_CONFIG(statustip)
        self.z_rotation_label.setText(QCoreApplication.translate("MainWindow", u"Z rotation", None))
#if QT_CONFIG(tooltip)
        self.z_slider.setToolTip(QCoreApplication.translate("MainWindow", u"Control Z rotation value. Left click on the left end or right end to decrease or increase angle by 1 degree.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.z_slider.setStatusTip(QCoreApplication.translate("MainWindow", u"Control Z rotation value. Left click on the left end or right end to decrease or increase angle by 1 degree.", None))
#endif // QT_CONFIG(statustip)
        self.slice_num_label.setText(QCoreApplication.translate("MainWindow", u"Slice", None))
#if QT_CONFIG(tooltip)
        self.slice_slider.setToolTip(QCoreApplication.translate("MainWindow", u"Control slice value. Left click on the left end or right end to decrease or increase by 1.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.slice_slider.setStatusTip(QCoreApplication.translate("MainWindow", u"Control slice value. Left click on the left end or right end to decrease or increase by 1.", None))
#endif // QT_CONFIG(statustip)
        self.x_view_radio_button.setText(QCoreApplication.translate("MainWindow", u"X view", None))
        self.y_view_radio_button.setText(QCoreApplication.translate("MainWindow", u"Y view", None))
        self.z_view_radio_button.setText(QCoreApplication.translate("MainWindow", u"Z view", None))
#if QT_CONFIG(tooltip)
        self.reset_button.setToolTip(QCoreApplication.translate("MainWindow", u"Reset rotation and slice values for the current image.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.reset_button.setStatusTip(QCoreApplication.translate("MainWindow", u"Reset rotation and slice values for the current image.", None))
#endif // QT_CONFIG(statustip)
        self.reset_button.setText(QCoreApplication.translate("MainWindow", u"Reset", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Smoothing Options", None))
        self.conductance_parameter_label.setText(QCoreApplication.translate("MainWindow", u"Conductance:", None))
        self.conductance_parameter_input.setPlaceholderText(QCoreApplication.translate("MainWindow", u"3.0", None))
        self.smoothing_iterations_label.setText(QCoreApplication.translate("MainWindow", u"Iterations:", None))
        self.smoothing_iterations_input.setPlaceholderText(QCoreApplication.translate("MainWindow", u"5", None))
        self.time_step_label.setText(QCoreApplication.translate("MainWindow", u"Time Step:", None))
        self.time_step_input.setPlaceholderText(QCoreApplication.translate("MainWindow", u"0.0625", None))
        self.smoothing_preview_button.setText(QCoreApplication.translate("MainWindow", u"Preview", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"Threshold Options", None))
        self.otsu_radio_button.setText(QCoreApplication.translate("MainWindow", u"Otsu Threshold", None))
        self.binary_radio_button.setText(QCoreApplication.translate("MainWindow", u"Binary Threshold", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"Lower Threshold:", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"Upper Threshold:", None))
        self.threshold_preview_button.setText(QCoreApplication.translate("MainWindow", u"Preview", None))
#if QT_CONFIG(tooltip)
        self.apply_button.setToolTip(QCoreApplication.translate("MainWindow", u"Compute circumference using current settings.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.apply_button.setStatusTip(QCoreApplication.translate("MainWindow", u"Compute circumference using current settings.", None))
#endif // QT_CONFIG(statustip)
        self.apply_button.setText(QCoreApplication.translate("MainWindow", u"Apply", None))
        self.circumference_label.setText(QCoreApplication.translate("MainWindow", u"Calculated Circumference: N/A", None))
#if QT_CONFIG(statustip)
        self.image.setStatusTip(QCoreApplication.translate("MainWindow", u"Image path is displayed here.", None))
#endif // QT_CONFIG(statustip)
        self.image.setText(QCoreApplication.translate("MainWindow", u"Select images using File > Open!", None))
        self.image_path_label.setText(QCoreApplication.translate("MainWindow", u"Image path", None))
#if QT_CONFIG(tooltip)
        self.previous_button.setToolTip(QCoreApplication.translate("MainWindow", u"Previous image.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.previous_button.setStatusTip(QCoreApplication.translate("MainWindow", u"Previous image.", None))
#endif // QT_CONFIG(statustip)
        self.previous_button.setText(QCoreApplication.translate("MainWindow", u"Previous", None))
        self.image_num_label.setText(QCoreApplication.translate("MainWindow", u"Image 0 of 0", None))
#if QT_CONFIG(tooltip)
        self.next_button.setToolTip(QCoreApplication.translate("MainWindow", u"Next image.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.next_button.setStatusTip(QCoreApplication.translate("MainWindow", u"Next image.", None))
#endif // QT_CONFIG(statustip)
        self.next_button.setText(QCoreApplication.translate("MainWindow", u"Next", None))
        self.export_button.setText(QCoreApplication.translate("MainWindow", u"Export", None))
        self.menu_file.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
#if QT_CONFIG(tooltip)
        self.action_export.setToolTip(QCoreApplication.translate("MainWindow", u"Export image data as CSV or export the image.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.action_export.setStatusTip(QCoreApplication.translate("MainWindow", u"Export image data as CSV or export the image.", None))
#endif // QT_CONFIG(statustip)
        self.action_export.setTitle(QCoreApplication.translate("MainWindow", u"Export", None))
        self.menu_help.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
#if QT_CONFIG(tooltip)
        self.menu_debug.setToolTip(QCoreApplication.translate("MainWindow", u"Tools for debugging.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.menu_debug.setStatusTip(QCoreApplication.translate("MainWindow", u"Tools for debugging.", None))
#endif // QT_CONFIG(statustip)
        self.menu_debug.setTitle(QCoreApplication.translate("MainWindow", u"Debug", None))
    # retranslateUi

