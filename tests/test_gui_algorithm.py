import sys
import unittest

from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt
from src.GUI.main import MainWindow

app = QApplication(sys.argv)


class TestGUI(unittest.TestCase):
    def setUp(self):
        """This method runs before each test.

        Creates a MainWindow() instance."""
        self.window: MainWindow = MainWindow()

    def test_image_label_text(self):
        """Test image label's initial text."""
        self.assertEqual(self.window.image.text(), "Select images using File > Open!")

    def test_image_initially_enabled(self):
        """Test image label's initial state."""
        self.assertEqual(self.window.image.isEnabled(), True)
