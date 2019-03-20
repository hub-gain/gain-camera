import sys
import numpy as np
import pyqtgraph as pg

from matplotlib import pyplot as plt
from pyqtgraph.Qt import QtCore, QtGui

from gain_connection import Connection
from utils import img2count


class ExposureTimeComboBox(QtGui.QComboBox):
    values = np.arange(-2, -13.1, -1)
    value_names = [str(v) for v in values]

    def __init__(self, connection, *args, **kwargs):
        QtGui.QComboBox.__init__(self, *args, **kwargs)

        self.connection = connection
        self.addItems(self.value_names)
        self.currentIndexChanged.connect(self.selected_exposure)

    def selected_exposure(self, idx):
        value = self.values[idx]
        self.connection.set_exposure_time(value)


class App(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(App, self).__init__(parent)

        self.connection = Connection()

        #### Create Gui Elements ###########
        self.mainbox = QtGui.QWidget()
        self.setCentralWidget(self.mainbox)
        self.mainbox.setLayout(QtGui.QVBoxLayout())

        self.canvas = pg.GraphicsLayoutWidget()
        self.mainbox.layout().addWidget(self.canvas)

        self.atom_numbers = []
        self.plotwidget = pg.PlotWidget()
        self.plotcurve = pg.PlotCurveItem()
        self.plotwidget.addItem(self.plotcurve)
        self.mainbox.layout().addWidget(self.plotwidget)

        self.exposure_time = ExposureTimeComboBox(self.connection)
        self.mainbox.layout().addWidget(self.exposure_time)

        self.views = []
        self.imgs = []

        for idx in range(3):
            view = self.canvas.addViewBox()
            view.setAspectLocked(True)
            view.setRange(QtCore.QRectF(0,0, 480, 744))

            #  image plot
            img = pg.ImageItem(border='w')
            view.addItem(img)

            self.views.append(view)
            self.imgs.append(img)

            if idx < 2:
                self.canvas.nextColumn()


        #### Start  #####################
        self.connection.connect()
        self.connection.run_acquisition_thread()
        self.draw_images()

    def draw_images(self):
        atoms = []
        for idx in range(3):
            data = self.connection.image_data[idx]
            self.imgs[idx].setImage(data, levels=(0, 255))
            # FIXME: query real exposure from server!
            exposure = self.exposure_time.values[self.exposure_time.currentIndex() or 0]
            atoms.append(
                img2count(data, exposure)
            )
        atoms = np.sum(atoms)
        last = 0
        if len(self.atom_numbers) > 0:
            last = self.atom_numbers[-1]
        if atoms != last:
            # FIXME: Better!
            self.atom_numbers.append(atoms)

        self.atom_numbers = self.atom_numbers[-200:]

        self.plotcurve.setData(self.atom_numbers)

        QtCore.QTimer.singleShot(1, self.draw_images)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    thisapp = App()
    thisapp.show()
    sys.exit(app.exec_())
