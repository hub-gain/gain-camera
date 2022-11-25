import numpy as np
from PyQt5 import QtGui, QtWidgets
from widgets import CustomWidget


class RecordBackgroundBox(QtWidgets.QGroupBox, CustomWidget):
    def __init__(self, *args, **kwargs):
        super(RecordBackgroundBox, self).__init__(*args, **kwargs)

    def connection_established(self, connection):
        self.connection = connection
        self.connection.parameters.background.change(self.react_to_change)
        # self.activated.connect(self.selected_exposure)
        self.react_to_change(self.connection.parameters.background.value)

        self.record_button.clicked.connect(self.record_background)
        self.clear_button.clicked.connect(self.clear_background)

    @property
    def record_button(self):
        return self.get_widget("recordBackground")

    @property
    def clear_button(self):
        return self.get_widget("clearBackground")

    def react_to_change(self, background):
        if background is not None:
            self.record_button.hide()
            self.clear_button.show()
        else:
            self.record_button.show()
            self.clear_button.hide()

    def record_background(self):
        self.connection.record_background()

    def clear_background(self):
        self.connection.clear_background()
