from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel


class QClickableLabel(QLabel):
    """Clickable QLabel

    When double clicked, the binded slider will be set to 0.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self._binded_slider = None

    @property
    def binded_slider(self):
        return self._binded_slider

    @binded_slider.setter
    def binded_slider(self, slider):
        self._binded_slider = slider

    def mouseDoubleClickEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            if self.binded_slider:
                self.binded_slider.setValue(0)
