import numpy as np
from PyQt5 import QtGui, QtWidgets
from widgets import CustomWidget
from pyqtgraph.Qt import QtCore


INPUT_NAMES = ("cropX0", "cropX1", "cropY0", "cropY1")


class CropBoxWidget(QtWidgets.QGroupBox, CustomWidget):
    def __init__(self, *args, **kwargs):
        super(CropBoxWidget, self).__init__(*args, **kwargs)

    def connection_established(self, connection):
        self.connection = connection
        self.connection.parameters.crop.change(self.react_to_change)
        self.connection.parameters.crop_enabled.change(self.react_to_change)

        self.checkbox_enable.stateChanged.connect(self.change_crop)
        for name in INPUT_NAMES:
            self.get_widget(name).valueChanged.connect(self.change_crop)

    @property
    def checkbox_enable(self):
        return self.get_widget("enableCrop")

    def get_crop_bounds(self):
        values = [self.get_widget(key).value() for key in INPUT_NAMES]
        if values[1] <= values[0]:
            values[1] = values[0] + 5
        if values[3] <= values[2]:
            values[3] = values[2] + 5
        return values

    def react_to_change(self, *args):
        # IMPORTANT: both values have to be queried first, and set later.
        # Otherwise there will be a problem with event handlers.
        crop_enabled = self.connection.parameters.crop_enabled.value
        crop = list(self.connection.parameters.crop.value)

        self.checkbox_enable.setCheckState(2 if crop_enabled else 0)
        for idx, name in enumerate(INPUT_NAMES):
            self.get_widget(name).setValue(crop[idx])

    def change_crop(self):
        def delayed_change():
            """Delayed change is required in order to be able to initially set
            both `crop_enabled` and `crop` without firing a change in between."""
            self.connection.parameters.crop_enabled.value = (
                self.checkbox_enable.isChecked()
            )
            self.connection.parameters.crop.value = tuple(self.get_crop_bounds())

        QtCore.QTimer.singleShot(100, delayed_change)
