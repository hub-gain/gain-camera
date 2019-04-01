import numpy as np
from PyQt5 import QtGui, QtWidgets
from widgets import CustomWidget
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg


class AtomNumberWidget(pg.PlotWidget, CustomWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.plotcurve = pg.PlotCurveItem()
        self.addItem(self.plotcurve)

    def draw(self, atom_numbers):
        self.plotcurve.setData(atom_numbers)