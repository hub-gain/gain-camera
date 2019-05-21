import numpy as np
from PyQt5 import QtGui, QtWidgets
from widgets import CustomWidget


class ConfigureRecordingBox(QtWidgets.QGroupBox, CustomWidget):
    def __init__(self, *args, **kwargs):
        super(ConfigureRecordingBox, self).__init__(*args, **kwargs)

    def connection_established(self, connection):
        self.connection = connection

        self.connection.parameters.trigger.change(self.react_to_trigger_change)
        self.connection.parameters.recording.change(self.react_to_recording_change)
        self.connection.parameters.recording_length.change(self.react_to_recording_length_change)

        self.trigger_checkbox.stateChanged.connect(self.change_trigger)
        self.recording_checkbox.stateChanged.connect(self.change_recording)
        self.recording_length_input.valueChanged.connect(self.change_recording_length)
        self.clear_recording_button.clicked.connect(self.clear_recording)

    @property
    def trigger_checkbox(self):
        return self.get_widget('enableTrigger')

    @property
    def recording_checkbox(self):
        return self.get_widget('enableRecording')

    @property
    def recording_length_input(self):
        return self.get_widget('recordingLength')

    @property
    def clear_recording_button(self):
        return self.get_widget('clearRecording')

    def react_to_trigger_change(self, trigger):
        self.trigger_checkbox.setCheckState(2 if trigger else 0)

    def change_trigger(self, trigger):
        self.connection.enable_trigger(trigger)

    def react_to_recording_change(self, recording):
        self.recording_checkbox.setCheckState(2 if recording else 0)

    def change_recording(self, recording):
        self.connection.parameters.recording.value = recording

    def react_to_recording_length_change(self, recording_length):
        self.recording_length_input.setValue(recording_length)

    def change_recording_length(self):
        self.connection.parameters.recording_length.value = \
            self.recording_length_input.value()

    def clear_recording(self):
        self.connection.parameters.clear_recording.value = True
        self.connection.parameters.clear_recording.value = False
