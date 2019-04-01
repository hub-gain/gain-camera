import numpy as np
from PyQt5 import QtGui, QtWidgets
from widgets import CustomWidget


class SelectExposureTimeWidget(QtWidgets.QComboBox, CustomWidget):
    values = [int(v) for v in np.arange(-2, -13.1, -1)]
    value_names = [str(v) for v in values]

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
