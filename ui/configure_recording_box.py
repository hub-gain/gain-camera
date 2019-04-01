import numpy as np
from PyQt5 import QtGui, QtWidgets
from widgets import CustomWidget


class ConfigureRecordingBox(QtWidgets.QGroupBox, CustomWidget):
    def __init__(self, *args, **kwargs):
        super(ConfigureRecordingBox, self).__init__(*args, **kwargs)

    def connection_established(self, connection):
        self.connection = connection
        self.connection.parameters.trigger.change(self.react_to_trigger_change)
        #self.activated.connect(self.selected_exposure)

        self.trigger_checkbox.stateChanged.connect(self.change_trigger)

    @property
    def trigger_checkbox(self):
        return self.get_widget('enableTrigger')

    def react_to_trigger_change(self, trigger):
        self.trigger_checkbox.setCheckState(2 if trigger else 0)

    def change_trigger(self, trigger):
        self.connection.parameters.trigger.value = trigger