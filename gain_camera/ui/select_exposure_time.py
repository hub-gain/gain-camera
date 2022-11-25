import numpy as np
from PyQt5 import QtGui, QtWidgets
from widgets import CustomWidget
from gain_camera.utils import EXPOSURES

MAX_TIME = 250  # in ms


class SelectExposureTimeWidget(QtWidgets.QComboBox, CustomWidget):
    values = [int(v) for v in EXPOSURES]
    value_names = [
        "%d (%.2f ms)" % (v, MAX_TIME / (2**idx)) for idx, v in enumerate(values)
    ]

    def __init__(self, *args, **kwargs):
        super(SelectExposureTimeWidget, self).__init__(*args, **kwargs)

        self.addItems(self.value_names)

    def connection_established(self, connection):
        self.connection = connection
        self.connection.parameters.exposure.change(self.react_to_change)
        self.activated.connect(self.selected_exposure)

    def selected_exposure(self, idx):
        value = self.values[idx]
        self.connection.parameters.exposure.value = int(value)
        self.setCurrentIndex(idx)

    def react_to_change(self, value):
        self.setCurrentIndex(self.values.index(value))
