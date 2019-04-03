import numpy as np
from PyQt5 import QtGui, QtWidgets
from widgets import CustomWidget
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg

from utils import img2count


class AtomNumberWidget(pg.PlotWidget, CustomWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.plotcurve = pg.PlotCurveItem()
        self.addItem(self.plotcurve)

        self.atom_numbers = []

        self.connection = None
        self.parameters = None
        self.exposure = None
        self.recording_length = None
        self.recording = None

    def connection_established(self, connection):
        self.connection = connection
        params = connection.parameters

        def exposure_changed(exposure):
            self.exposure = exposure
        params.exposure.change(exposure_changed)

        def recording_length_changed(recording_length):
            self.recording_length = recording_length
            self.clip_atom_number_recording()
        params.recording_length.change(recording_length_changed)

        def clear_recording_changed(clear):
            if clear:
                self.atom_numbers = []
                params.clear_recording.value = False
        params.clear_recording.change(clear_recording_changed)

        def recording_changed(recording):
            self.recording = recording
        params.recording.change(recording_changed)

    @property
    def ready(self):
        return self.connection is not None \
             and self.exposure is not None \
             and self.recording_length is not None

    def update(self, image_data):
        if not self.recording or not self.ready:
            return

        exposure = self.exposure
        atoms = [
            img2count(data, exposure) for data in image_data
        ]
        atoms = np.sum(atoms)

        self.atom_numbers.append(float(atoms))
        self.clip_atom_number_recording()
        self.plotcurve.setData(self.atom_numbers)

    def clip_atom_number_recording(self):
        """Clip the recording of atom numbers such that `recording_length` is respected."""
        self.atom_numbers = self.atom_numbers[-self.recording_length:]